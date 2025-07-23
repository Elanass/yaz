"""
WebAuthn / Passkeys (FIDO2) Authentication Service
Passwordless biometric authentication for clinical users
"""

import json
import base64
import secrets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from webauthn import generate_registration_options, verify_registration_response
from webauthn import generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor, 
    UserVerificationRequirement,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    AuthenticatorAttachment
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from sqlalchemy.orm import Session
import structlog

from ..core.config import settings
from ..db.models import User, WebAuthnCredential
from ..schemas.auth import WebAuthnRegistrationRequest, WebAuthnAuthenticationRequest
from ..services.audit_service import AuditService, AuditEvent, AuditEventType, AuditSeverity

logger = structlog.get_logger(__name__)

class AuthenticatorType(str, Enum):
    """Types of authenticators"""
    PLATFORM = "platform"  # Built-in (FaceID, TouchID, Windows Hello)
    CROSS_PLATFORM = "cross-platform"  # External (YubiKey, etc.)
    HYBRID = "hybrid"  # Both

class CredentialStatus(str, Enum):
    """WebAuthn credential status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    COMPROMISED = "compromised"

@dataclass
class WebAuthnChallenge:
    """WebAuthn challenge data"""
    challenge: str
    user_id: int
    challenge_type: str  # "registration" or "authentication"
    expires_at: datetime
    origin: str
    rp_id: str

class WebAuthnService:
    """WebAuthn/FIDO2 service for passwordless authentication"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.rp_id = settings.WEBAUTHN_RP_ID
        self.rp_name = settings.WEBAUTHN_RP_NAME
        self.origin = settings.WEBAUTHN_ORIGIN
        
        # Temporary challenge storage (in production, use Redis)
        self._challenges: Dict[str, WebAuthnChallenge] = {}
    
    async def begin_registration(
        self,
        user: User,
        authenticator_type: AuthenticatorType = AuthenticatorType.PLATFORM,
        user_verification: UserVerificationRequirement = UserVerificationRequirement.REQUIRED
    ) -> Dict[str, Any]:
        """Begin WebAuthn credential registration process"""
        
        try:
            # Get existing credentials for this user
            existing_credentials = self.db.query(WebAuthnCredential).filter(
                WebAuthnCredential.user_id == user.id,
                WebAuthnCredential.status == CredentialStatus.ACTIVE
            ).all()
            
            # Convert existing credentials to exclude list
            exclude_credentials = [
                PublicKeyCredentialDescriptor(
                    id=base64.b64decode(cred.credential_id),
                    type="public-key"
                )
                for cred in existing_credentials
            ]
            
            # Configure authenticator selection criteria
            authenticator_selection = AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM 
                    if authenticator_type == AuthenticatorType.PLATFORM 
                    else AuthenticatorAttachment.CROSS_PLATFORM 
                    if authenticator_type == AuthenticatorType.CROSS_PLATFORM
                    else None,
                resident_key=ResidentKeyRequirement.REQUIRED,
                user_verification=user_verification
            )
            
            # Generate registration options
            options = generate_registration_options(
                rp_id=self.rp_id,
                rp_name=self.rp_name,
                user_id=str(user.id).encode(),
                user_name=user.username,
                user_display_name=f"{user.first_name} {user.last_name}",
                exclude_credentials=exclude_credentials,
                authenticator_selection=authenticator_selection,
                attestation=AttestationConveyancePreference.DIRECT,
                supported_pub_key_algs=[
                    COSEAlgorithmIdentifier.ECDSA_SHA_256,
                    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
                    COSEAlgorithmIdentifier.EdDSA,
                ]
            )
            
            # Store challenge for verification
            challenge_data = WebAuthnChallenge(
                challenge=base64.b64encode(options.challenge).decode(),
                user_id=user.id,
                challenge_type="registration",
                expires_at=datetime.utcnow() + timedelta(minutes=5),
                origin=self.origin,
                rp_id=self.rp_id
            )
            
            challenge_key = f"reg_{user.id}_{secrets.token_urlsafe(16)}"
            self._challenges[challenge_key] = challenge_data
            
            # Log registration attempt
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.USER_LOGIN,
                    user_id=user.id,
                    resource_type="webauthn_credential",
                    resource_id=None,
                    action="begin_registration",
                    details={
                        "authenticator_type": authenticator_type.value,
                        "challenge_key": challenge_key,
                        "existing_credentials_count": len(existing_credentials)
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.MEDIUM
                )
            )
            
            return {
                "options": json.loads(options.json()),
                "challenge_key": challenge_key,
                "expires_at": challenge_data.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to begin WebAuthn registration", user_id=user.id, error=str(e))
            raise
    
    async def complete_registration(
        self,
        challenge_key: str,
        credential_response: Dict[str, Any],
        credential_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Complete WebAuthn credential registration"""
        
        try:
            # Get and validate challenge
            if challenge_key not in self._challenges:
                raise ValueError("Invalid or expired challenge")
            
            challenge_data = self._challenges[challenge_key]
            
            if challenge_data.expires_at < datetime.utcnow():
                del self._challenges[challenge_key]
                raise ValueError("Challenge expired")
            
            if challenge_data.challenge_type != "registration":
                raise ValueError("Invalid challenge type")
            
            # Get user
            user = self.db.query(User).filter(User.id == challenge_data.user_id).first()
            if not user:
                raise ValueError("User not found")
            
            # Verify registration response
            verification = verify_registration_response(
                credential=credential_response,
                expected_challenge=base64.b64decode(challenge_data.challenge),
                expected_origin=challenge_data.origin,
                expected_rp_id=challenge_data.rp_id,
                require_user_verification=True
            )
            
            if not verification.verified:
                raise ValueError("Registration verification failed")
            
            # Extract credential data
            credential_data = verification.credential_id
            public_key = verification.credential_public_key
            sign_count = verification.sign_count
            aaguid = verification.aaguid
            
            # Generate credential name if not provided
            if not credential_name:
                credential_count = self.db.query(WebAuthnCredential).filter(
                    WebAuthnCredential.user_id == user.id
                ).count()
                credential_name = f"Authenticator {credential_count + 1}"
            
            # Store credential in database
            webauthn_credential = WebAuthnCredential(
                user_id=user.id,
                credential_id=base64.b64encode(credential_data).decode(),
                public_key=base64.b64encode(public_key).decode(),
                sign_count=sign_count,
                aaguid=aaguid.hex() if aaguid else None,
                credential_name=credential_name,
                authenticator_type=self._detect_authenticator_type(credential_response),
                status=CredentialStatus.ACTIVE,
                last_used=datetime.utcnow(),
                created_from_ip="",  # Extract from request context
                created_from_user_agent=""  # Extract from request context
            )
            
            self.db.add(webauthn_credential)
            self.db.commit()
            
            # Clean up challenge
            del self._challenges[challenge_key]
            
            # Log successful registration
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.SYSTEM_CONFIG,
                    user_id=user.id,
                    resource_type="webauthn_credential",
                    resource_id=str(webauthn_credential.id),
                    action="complete_registration",
                    details={
                        "credential_name": credential_name,
                        "authenticator_type": webauthn_credential.authenticator_type,
                        "aaguid": webauthn_credential.aaguid
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.HIGH
                )
            )
            
            logger.info(
                "WebAuthn credential registered successfully",
                user_id=user.id,
                credential_id=webauthn_credential.credential_id[:8] + "..."
            )
            
            return {
                "success": True,
                "credential_id": webauthn_credential.credential_id,
                "credential_name": credential_name,
                "created_at": webauthn_credential.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to complete WebAuthn registration", error=str(e))
            raise
    
    async def begin_authentication(
        self,
        username: Optional[str] = None,
        user_verification: UserVerificationRequirement = UserVerificationRequirement.REQUIRED
    ) -> Dict[str, Any]:
        """Begin WebAuthn authentication process"""
        
        try:
            # Get user credentials (if username provided)
            allowed_credentials = []
            user_id = None
            
            if username:
                user = self.db.query(User).filter(User.username == username).first()
                if user:
                    user_id = user.id
                    credentials = self.db.query(WebAuthnCredential).filter(
                        WebAuthnCredential.user_id == user.id,
                        WebAuthnCredential.status == CredentialStatus.ACTIVE
                    ).all()
                    
                    allowed_credentials = [
                        PublicKeyCredentialDescriptor(
                            id=base64.b64decode(cred.credential_id),
                            type="public-key"
                        )
                        for cred in credentials
                    ]
            
            # Generate authentication options
            options = generate_authentication_options(
                rp_id=self.rp_id,
                allow_credentials=allowed_credentials,
                user_verification=user_verification
            )
            
            # Store challenge for verification
            challenge_data = WebAuthnChallenge(
                challenge=base64.b64encode(options.challenge).decode(),
                user_id=user_id,
                challenge_type="authentication",
                expires_at=datetime.utcnow() + timedelta(minutes=5),
                origin=self.origin,
                rp_id=self.rp_id
            )
            
            challenge_key = f"auth_{secrets.token_urlsafe(16)}"
            self._challenges[challenge_key] = challenge_data
            
            # Log authentication attempt
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.USER_LOGIN,
                    user_id=user_id,
                    resource_type="webauthn_credential",
                    resource_id=None,
                    action="begin_authentication",
                    details={
                        "username": username,
                        "challenge_key": challenge_key,
                        "allowed_credentials_count": len(allowed_credentials)
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.MEDIUM
                )
            )
            
            return {
                "options": json.loads(options.json()),
                "challenge_key": challenge_key,
                "expires_at": challenge_data.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to begin WebAuthn authentication", error=str(e))
            raise
    
    async def complete_authentication(
        self,
        challenge_key: str,
        credential_response: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete WebAuthn authentication"""
        
        try:
            # Get and validate challenge
            if challenge_key not in self._challenges:
                raise ValueError("Invalid or expired challenge")
            
            challenge_data = self._challenges[challenge_key]
            
            if challenge_data.expires_at < datetime.utcnow():
                del self._challenges[challenge_key]
                raise ValueError("Challenge expired")
            
            if challenge_data.challenge_type != "authentication":
                raise ValueError("Invalid challenge type")
            
            # Get credential from database
            credential_id = credential_response["id"]
            webauthn_credential = self.db.query(WebAuthnCredential).filter(
                WebAuthnCredential.credential_id == credential_id,
                WebAuthnCredential.status == CredentialStatus.ACTIVE
            ).first()
            
            if not webauthn_credential:
                raise ValueError("Credential not found or inactive")
            
            # Get user
            user = self.db.query(User).filter(User.id == webauthn_credential.user_id).first()
            if not user or not user.is_active:
                raise ValueError("User not found or inactive")
            
            # Verify authentication response
            verification = verify_authentication_response(
                credential=credential_response,
                expected_challenge=base64.b64decode(challenge_data.challenge),
                expected_origin=challenge_data.origin,
                expected_rp_id=challenge_data.rp_id,
                credential_public_key=base64.b64decode(webauthn_credential.public_key),
                credential_current_sign_count=webauthn_credential.sign_count,
                require_user_verification=True
            )
            
            if not verification.verified:
                # Log failed authentication
                await self.audit_service.log_event(
                    AuditEvent(
                        event_type=AuditEventType.USER_FAILED_LOGIN,
                        user_id=user.id,
                        resource_type="webauthn_credential",
                        resource_id=str(webauthn_credential.id),
                        action="authentication_failed",
                        details={
                            "credential_id": credential_id[:8] + "...",
                            "reason": "verification_failed"
                        },
                        ip_address="",  # Extract from request context
                        user_agent="",  # Extract from request context
                        severity=AuditSeverity.HIGH
                    )
                )
                raise ValueError("Authentication verification failed")
            
            # Update credential sign count and last used
            webauthn_credential.sign_count = verification.new_sign_count
            webauthn_credential.last_used = datetime.utcnow()
            
            # Update user last login
            user.last_login = datetime.utcnow()
            user.failed_login_attempts = 0
            user.locked_until = None
            
            self.db.commit()
            
            # Clean up challenge
            del self._challenges[challenge_key]
            
            # Log successful authentication
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.USER_LOGIN,
                    user_id=user.id,
                    resource_type="webauthn_credential",
                    resource_id=str(webauthn_credential.id),
                    action="authentication_success",
                    details={
                        "credential_name": webauthn_credential.credential_name,
                        "authenticator_type": webauthn_credential.authenticator_type,
                        "sign_count": verification.new_sign_count
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.MEDIUM
                )
            )
            
            logger.info(
                "WebAuthn authentication successful",
                user_id=user.id,
                credential_id=credential_id[:8] + "..."
            )
            
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
                "credential_name": webauthn_credential.credential_name,
                "last_used": webauthn_credential.last_used.isoformat()
            }
            
        except Exception as e:
            logger.error("Failed to complete WebAuthn authentication", error=str(e))
            raise
    
    async def list_user_credentials(self, user_id: int) -> List[Dict[str, Any]]:
        """List all WebAuthn credentials for a user"""
        
        credentials = self.db.query(WebAuthnCredential).filter(
            WebAuthnCredential.user_id == user_id
        ).all()
        
        return [
            {
                "id": cred.id,
                "credential_name": cred.credential_name,
                "authenticator_type": cred.authenticator_type,
                "status": cred.status,
                "created_at": cred.created_at.isoformat(),
                "last_used": cred.last_used.isoformat() if cred.last_used else None,
                "sign_count": cred.sign_count,
                "aaguid": cred.aaguid
            }
            for cred in credentials
        ]
    
    async def revoke_credential(
        self,
        user_id: int,
        credential_id: str,
        reason: str = "user_requested"
    ) -> bool:
        """Revoke a WebAuthn credential"""
        
        try:
            credential = self.db.query(WebAuthnCredential).filter(
                WebAuthnCredential.user_id == user_id,
                WebAuthnCredential.credential_id == credential_id,
                WebAuthnCredential.status == CredentialStatus.ACTIVE
            ).first()
            
            if not credential:
                return False
            
            credential.status = CredentialStatus.REVOKED
            credential.revoked_at = datetime.utcnow()
            credential.revocation_reason = reason
            
            self.db.commit()
            
            # Log credential revocation
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.SYSTEM_CONFIG,
                    user_id=user_id,
                    resource_type="webauthn_credential",
                    resource_id=str(credential.id),
                    action="revoke_credential",
                    details={
                        "credential_name": credential.credential_name,
                        "reason": reason
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.HIGH
                )
            )
            
            return True
            
        except Exception as e:
            logger.error("Failed to revoke WebAuthn credential", error=str(e))
            return False
    
    def _detect_authenticator_type(self, credential_response: Dict[str, Any]) -> str:
        """Detect authenticator type from registration response"""
        
        # This is a simplified detection based on response characteristics
        # In practice, you might want to use the AAGUID or other metadata
        
        if credential_response.get("response", {}).get("clientDataJSON"):
            # Parse client data to get more information
            # For now, return platform as default for biometric authenticators
            return AuthenticatorType.PLATFORM.value
        
        return AuthenticatorType.CROSS_PLATFORM.value
    
    async def cleanup_expired_challenges(self):
        """Clean up expired challenges (should be run periodically)"""
        
        current_time = datetime.utcnow()
        expired_keys = [
            key for key, challenge in self._challenges.items()
            if challenge.expires_at < current_time
        ]
        
        for key in expired_keys:
            del self._challenges[key]
        
        logger.info("Cleaned up expired challenges", count=len(expired_keys))
