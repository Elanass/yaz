"""
OIDC Federation Service
Integration with hospital identity systems (Google Workspace, Azure AD, eHealth)
"""

import json
import secrets
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from urllib.parse import urlencode, urlparse
import jwt
from jwt import PyJWKClient
import httpx
from pydantic import BaseModel, validator
from sqlalchemy.orm import Session
import structlog

from ..core.config import settings
from ..db.models import User, OIDCProvider, OIDCUserMapping
from ..schemas.auth import OIDCLoginRequest, OIDCCallbackRequest
from ..services.audit_service import AuditService, AuditEvent, AuditEventType, AuditSeverity

logger = structlog.get_logger(__name__)

class OIDCProviderConfig(BaseModel):
    """OIDC provider configuration"""
    provider_id: str
    name: str
    issuer: str
    client_id: str
    client_secret: str
    scopes: List[str] = ["openid", "profile", "email"]
    response_type: str = "code"
    response_mode: str = "query"
    
    # Discovery endpoints (auto-discovered if not specified)
    authorization_endpoint: Optional[str] = None
    token_endpoint: Optional[str] = None
    userinfo_endpoint: Optional[str] = None
    jwks_uri: Optional[str] = None
    
    # Attribute mapping
    username_claim: str = "preferred_username"
    email_claim: str = "email"
    first_name_claim: str = "given_name"
    last_name_claim: str = "family_name"
    
    # Security settings
    verify_ssl: bool = True
    require_https: bool = True
    token_validation: bool = True
    
    @validator('issuer')
    def validate_issuer(cls, v):
        if not v.startswith('https://'):
            raise ValueError('Issuer must use HTTPS')
        return v

class OIDCProviderManager:
    """Manages OIDC provider configurations"""
    
    def __init__(self):
        self.providers: Dict[str, OIDCProviderConfig] = {}
        self._load_default_providers()
    
    def _load_default_providers(self):
        """Load default OIDC provider configurations"""
        
        # Google Workspace
        if settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET:
            self.providers["google"] = OIDCProviderConfig(
                provider_id="google",
                name="Google Workspace",
                issuer="https://accounts.google.com",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                scopes=["openid", "profile", "email"],
                username_claim="email",
                email_claim="email"
            )
        
        # Microsoft Azure AD
        if settings.AZURE_CLIENT_ID and settings.AZURE_CLIENT_SECRET:
            tenant_id = settings.AZURE_TENANT_ID or "common"
            self.providers["azure"] = OIDCProviderConfig(
                provider_id="azure",
                name="Microsoft Azure AD",
                issuer=f"https://login.microsoftonline.com/{tenant_id}/v2.0",
                client_id=settings.AZURE_CLIENT_ID,
                client_secret=settings.AZURE_CLIENT_SECRET,
                scopes=["openid", "profile", "email"],
                username_claim="preferred_username",
                email_claim="email"
            )
    
    def get_provider(self, provider_id: str) -> Optional[OIDCProviderConfig]:
        """Get OIDC provider configuration"""
        return self.providers.get(provider_id)
    
    def list_providers(self) -> List[Dict[str, str]]:
        """List available OIDC providers"""
        return [
            {
                "provider_id": provider.provider_id,
                "name": provider.name,
                "issuer": provider.issuer
            }
            for provider in self.providers.values()
        ]
    
    def add_provider(self, config: OIDCProviderConfig):
        """Add custom OIDC provider"""
        self.providers[config.provider_id] = config

class OIDCDiscovery:
    """OIDC discovery and metadata handling"""
    
    @staticmethod
    async def discover_endpoints(issuer: str) -> Dict[str, Any]:
        """Discover OIDC endpoints from issuer"""
        
        discovery_url = f"{issuer.rstrip('/')}/.well-known/openid_configuration"
        
        try:
            async with httpx.AsyncClient(verify=True) as client:
                response = await client.get(discovery_url, timeout=10.0)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error("Failed to discover OIDC endpoints", issuer=issuer, error=str(e))
            raise ValueError(f"OIDC discovery failed for {issuer}: {str(e)}")
    
    @staticmethod
    async def get_jwks(jwks_uri: str) -> Dict[str, Any]:
        """Get JSON Web Key Set from provider"""
        
        try:
            async with httpx.AsyncClient(verify=True) as client:
                response = await client.get(jwks_uri, timeout=10.0)
                response.raise_for_status()
                return response.json()
                
        except Exception as e:
            logger.error("Failed to get JWKS", jwks_uri=jwks_uri, error=str(e))
            raise ValueError(f"Failed to get JWKS: {str(e)}")

class OIDCTokenValidator:
    """OIDC token validation"""
    
    def __init__(self, provider_config: OIDCProviderConfig):
        self.provider_config = provider_config
        self.jwks_client = None
        
        if provider_config.jwks_uri:
            self.jwks_client = PyJWKClient(provider_config.jwks_uri)
    
    async def validate_id_token(
        self,
        id_token: str,
        nonce: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate OIDC ID token"""
        
        try:
            # Decode header to get key ID
            header = jwt.get_unverified_header(id_token)
            kid = header.get("kid")
            
            if not kid and self.jwks_client:
                raise ValueError("Token missing key ID")
            
            # Get signing key
            if self.jwks_client:
                signing_key = self.jwks_client.get_signing_key(kid)
                key = signing_key.key
            else:
                # For providers without JWKS, you might need to handle differently
                raise ValueError("JWKS not configured for token validation")
            
            # Validate token
            payload = jwt.decode(
                id_token,
                key,
                algorithms=["RS256", "ES256"],
                audience=self.provider_config.client_id,
                issuer=self.provider_config.issuer
            )
            
            # Validate nonce if provided
            if nonce and payload.get("nonce") != nonce:
                raise ValueError("Invalid nonce in token")
            
            # Validate expiration
            if "exp" in payload and payload["exp"] < datetime.utcnow().timestamp():
                raise ValueError("Token expired")
            
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid ID token", error=str(e))
            raise ValueError(f"Invalid ID token: {str(e)}")
        except Exception as e:
            logger.error("Token validation failed", error=str(e))
            raise

class OIDCService:
    """Main OIDC federation service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.provider_manager = OIDCProviderManager()
        
        # State storage (in production, use Redis)
        self._auth_states: Dict[str, Dict[str, Any]] = {}
    
    async def get_authorization_url(
        self,
        provider_id: str,
        redirect_uri: str,
        state: Optional[str] = None,
        nonce: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate OIDC authorization URL"""
        
        provider_config = self.provider_manager.get_provider(provider_id)
        if not provider_config:
            raise ValueError(f"Unknown OIDC provider: {provider_id}")
        
        # Discover endpoints if not configured
        if not provider_config.authorization_endpoint:
            discovery = await OIDCDiscovery.discover_endpoints(provider_config.issuer)
            provider_config.authorization_endpoint = discovery["authorization_endpoint"]
            provider_config.token_endpoint = discovery["token_endpoint"]
            provider_config.userinfo_endpoint = discovery.get("userinfo_endpoint")
            provider_config.jwks_uri = discovery.get("jwks_uri")
        
        # Generate state and nonce if not provided
        if not state:
            state = secrets.token_urlsafe(32)
        if not nonce:
            nonce = secrets.token_urlsafe(32)
        
        # Store auth state
        auth_state = {
            "provider_id": provider_id,
            "redirect_uri": redirect_uri,
            "nonce": nonce,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(minutes=10)
        }
        self._auth_states[state] = auth_state
        
        # Build authorization URL
        auth_params = {
            "client_id": provider_config.client_id,
            "response_type": provider_config.response_type,
            "scope": " ".join(provider_config.scopes),
            "redirect_uri": redirect_uri,
            "state": state,
            "nonce": nonce
        }
        
        auth_url = f"{provider_config.authorization_endpoint}?{urlencode(auth_params)}"
        
        logger.info(
            "Generated OIDC authorization URL",
            provider_id=provider_id,
            state=state[:8] + "..."
        )
        
        return {
            "authorization_url": auth_url,
            "state": state,
            "nonce": nonce
        }
    
    async def handle_callback(
        self,
        code: str,
        state: str,
        redirect_uri: str
    ) -> Dict[str, Any]:
        """Handle OIDC callback and authenticate user"""
        
        try:
            # Validate and get auth state
            if state not in self._auth_states:
                raise ValueError("Invalid or expired state")
            
            auth_state = self._auth_states[state]
            
            if auth_state["expires_at"] < datetime.utcnow():
                del self._auth_states[state]
                raise ValueError("Authentication state expired")
            
            provider_id = auth_state["provider_id"]
            nonce = auth_state["nonce"]
            
            # Clean up state
            del self._auth_states[state]
            
            # Get provider config
            provider_config = self.provider_manager.get_provider(provider_id)
            if not provider_config:
                raise ValueError(f"Unknown OIDC provider: {provider_id}")
            
            # Exchange code for tokens
            tokens = await self._exchange_code_for_tokens(
                provider_config, code, redirect_uri
            )
            
            # Validate ID token
            validator = OIDCTokenValidator(provider_config)
            id_token_claims = await validator.validate_id_token(
                tokens["id_token"], nonce
            )
            
            # Get user info if needed
            userinfo = {}
            if provider_config.userinfo_endpoint and tokens.get("access_token"):
                userinfo = await self._get_userinfo(
                    provider_config, tokens["access_token"]
                )
            
            # Combine claims
            user_claims = {**id_token_claims, **userinfo}
            
            # Find or create user
            user = await self._find_or_create_user(provider_config, user_claims)
            
            # Log successful authentication
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.USER_LOGIN,
                    user_id=user.id,
                    resource_type="oidc_authentication",
                    resource_id=provider_id,
                    action="oidc_login_success",
                    details={
                        "provider": provider_id,
                        "subject": user_claims.get("sub"),
                        "email": user_claims.get(provider_config.email_claim)
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.MEDIUM
                )
            )
            
            return {
                "user": user,
                "tokens": tokens,
                "claims": user_claims
            }
            
        except Exception as e:
            logger.error("OIDC callback failed", error=str(e))
            
            # Log failed authentication
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.USER_FAILED_LOGIN,
                    user_id=None,
                    resource_type="oidc_authentication",
                    resource_id=provider_id if 'provider_id' in locals() else None,
                    action="oidc_login_failed",
                    details={
                        "error": str(e),
                        "state": state[:8] + "..." if state else None
                    },
                    ip_address="",  # Extract from request context
                    user_agent="",  # Extract from request context
                    severity=AuditSeverity.HIGH
                )
            )
            
            raise
    
    async def _exchange_code_for_tokens(
        self,
        provider_config: OIDCProviderConfig,
        code: str,
        redirect_uri: str
    ) -> Dict[str, str]:
        """Exchange authorization code for tokens"""
        
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": provider_config.client_id,
            "client_secret": provider_config.client_secret
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        
        async with httpx.AsyncClient(verify=provider_config.verify_ssl) as client:
            response = await client.post(
                provider_config.token_endpoint,
                data=token_data,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                raise ValueError(f"Token exchange failed: {response.text}")
            
            return response.json()
    
    async def _get_userinfo(
        self,
        provider_config: OIDCProviderConfig,
        access_token: str
    ) -> Dict[str, Any]:
        """Get user information from userinfo endpoint"""
        
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient(verify=provider_config.verify_ssl) as client:
            response = await client.get(
                provider_config.userinfo_endpoint,
                headers=headers,
                timeout=10.0
            )
            
            if response.status_code != 200:
                logger.warning("Failed to get userinfo", status=response.status_code)
                return {}
            
            return response.json()
    
    async def _find_or_create_user(
        self,
        provider_config: OIDCProviderConfig,
        user_claims: Dict[str, Any]
    ) -> User:
        """Find existing user or create new one from OIDC claims"""
        
        # Extract user attributes
        subject = user_claims.get("sub")
        email = user_claims.get(provider_config.email_claim)
        username = user_claims.get(provider_config.username_claim) or email
        first_name = user_claims.get(provider_config.first_name_claim, "")
        last_name = user_claims.get(provider_config.last_name_claim, "")
        
        if not subject or not email:
            raise ValueError("Missing required user claims (sub, email)")
        
        # Check for existing OIDC mapping
        mapping = self.db.query(OIDCUserMapping).filter(
            OIDCUserMapping.provider_id == provider_config.provider_id,
            OIDCUserMapping.provider_subject == subject
        ).first()
        
        if mapping:
            # Update existing user
            user = mapping.user
            user.last_login = datetime.utcnow()
            self.db.commit()
            return user
        
        # Check for existing user by email
        existing_user = self.db.query(User).filter(User.email == email).first()
        
        if existing_user:
            # Link existing user to OIDC provider
            new_mapping = OIDCUserMapping(
                user_id=existing_user.id,
                provider_id=provider_config.provider_id,
                provider_subject=subject,
                provider_claims=user_claims
            )
            self.db.add(new_mapping)
            existing_user.last_login = datetime.utcnow()
            self.db.commit()
            return existing_user
        
        # Create new user
        new_user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_verified=True,  # OIDC users are pre-verified
            hashed_password="",  # No password for OIDC users
            last_login=datetime.utcnow()
        )
        
        self.db.add(new_user)
        self.db.flush()  # Get user ID
        
        # Create OIDC mapping
        new_mapping = OIDCUserMapping(
            user_id=new_user.id,
            provider_id=provider_config.provider_id,
            provider_subject=subject,
            provider_claims=user_claims
        )
        
        self.db.add(new_mapping)
        self.db.commit()
        
        logger.info(
            "Created new OIDC user",
            user_id=new_user.id,
            provider=provider_config.provider_id,
            email=email
        )
        
        return new_user
    
    async def list_providers(self) -> List[Dict[str, str]]:
        """List available OIDC providers"""
        return self.provider_manager.list_providers()
    
    async def cleanup_expired_states(self):
        """Clean up expired auth states (should be run periodically)"""
        
        current_time = datetime.utcnow()
        expired_states = [
            state for state, data in self._auth_states.items()
            if data["expires_at"] < current_time
        ]
        
        for state in expired_states:
            del self._auth_states[state]
        
        logger.info("Cleaned up expired OIDC states", count=len(expired_states))
