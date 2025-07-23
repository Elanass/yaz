"""
WebAuthn / Passkeys API Endpoints
FIDO2 passwordless authentication for clinical users
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..core.deps import get_current_user, get_current_active_user
from ..services.webauthn_service import WebAuthnService, AuthenticatorType
from ..schemas.webauthn import (
    WebAuthnRegistrationBeginRequest,
    WebAuthnRegistrationBeginResponse,
    WebAuthnRegistrationCompleteRequest,
    WebAuthnRegistrationCompleteResponse,
    WebAuthnAuthenticationBeginRequest,
    WebAuthnAuthenticationBeginResponse,
    WebAuthnAuthenticationCompleteRequest,
    WebAuthnAuthenticationCompleteResponse,
    WebAuthnCredentialListResponse,
    WebAuthnCredentialRevokeRequest,
    WebAuthnCredentialRevokeResponse,
    WebAuthnErrorResponse,
    UserVerificationRequirement
)
from ..schemas.user import User

router = APIRouter(prefix="/auth/webauthn", tags=["webauthn"])

@router.post("/register/begin", response_model=WebAuthnRegistrationBeginResponse)
async def begin_webauthn_registration(
    request: WebAuthnRegistrationBeginRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Begin WebAuthn credential registration process
    Generates challenge and registration options for FIDO2 authenticators
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        result = await webauthn_service.begin_registration(
            user=current_user,
            authenticator_type=request.authenticator_type,
            user_verification=request.user_verification
        )
        
        return WebAuthnRegistrationBeginResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to begin registration: {str(e)}"
        )

@router.post("/register/complete", response_model=WebAuthnRegistrationCompleteResponse)
async def complete_webauthn_registration(
    request: WebAuthnRegistrationCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete WebAuthn credential registration
    Verifies attestation and stores credential
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        result = await webauthn_service.complete_registration(
            challenge_key=request.challenge_key,
            credential_response=request.credential_response,
            credential_name=request.credential_name
        )
        
        return WebAuthnRegistrationCompleteResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to complete registration: {str(e)}"
        )

@router.post("/authenticate/begin", response_model=WebAuthnAuthenticationBeginResponse)
async def begin_webauthn_authentication(
    request: WebAuthnAuthenticationBeginRequest,
    db: Session = Depends(get_db)
):
    """
    Begin WebAuthn authentication process
    Generates challenge and authentication options
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        result = await webauthn_service.begin_authentication(
            username=request.username,
            user_verification=request.user_verification
        )
        
        return WebAuthnAuthenticationBeginResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to begin authentication: {str(e)}"
        )

@router.post("/authenticate/complete", response_model=WebAuthnAuthenticationCompleteResponse)
async def complete_webauthn_authentication(
    request: WebAuthnAuthenticationCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Complete WebAuthn authentication
    Verifies assertion and authenticates user
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        result = await webauthn_service.complete_authentication(
            challenge_key=request.challenge_key,
            credential_response=request.credential_response
        )
        
        return WebAuthnAuthenticationCompleteResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )

@router.get("/credentials", response_model=WebAuthnCredentialListResponse)
async def list_webauthn_credentials(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List user's WebAuthn credentials
    Shows all registered authenticators
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        credentials = await webauthn_service.list_user_credentials(current_user.id)
        
        return WebAuthnCredentialListResponse(
            credentials=credentials,
            total_count=len(credentials)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list credentials: {str(e)}"
        )

@router.post("/credentials/revoke", response_model=WebAuthnCredentialRevokeResponse)
async def revoke_webauthn_credential(
    request: WebAuthnCredentialRevokeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Revoke a WebAuthn credential
    Disables the specified authenticator
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        success = await webauthn_service.revoke_credential(
            user_id=current_user.id,
            credential_id=request.credential_id,
            reason=request.reason
        )
        
        if success:
            return WebAuthnCredentialRevokeResponse(
                success=True,
                message="Credential revoked successfully"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Credential not found or already revoked"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to revoke credential: {str(e)}"
        )

@router.get("/supported")
async def check_webauthn_support():
    """
    Check WebAuthn browser support
    Returns information about available features
    """
    
    return {
        "webauthn_supported": True,
        "features": {
            "platform_authenticator": True,
            "cross_platform_authenticator": True,
            "user_verification": True,
            "resident_key": True,
            "conditional_mediation": True
        },
        "algorithms": [
            {"name": "ECDSA_SHA_256", "id": -7},
            {"name": "RSASSA_PKCS1_v1_5_SHA_256", "id": -257},
            {"name": "EdDSA", "id": -8}
        ],
        "attestation_formats": [
            "packed",
            "tpm",
            "android-key",
            "android-safetynet",
            "fido-u2f",
            "apple",
            "none"
        ]
    }

@router.get("/health")
async def webauthn_health_check(db: Session = Depends(get_db)):
    """
    Health check for WebAuthn service
    Verifies service configuration and dependencies
    """
    
    try:
        webauthn_service = WebAuthnService(db)
        
        # Test basic service initialization
        health_status = {
            "status": "healthy",
            "webauthn_service": "operational",
            "database": "connected",
            "configuration": {
                "rp_id": webauthn_service.rp_id,
                "rp_name": webauthn_service.rp_name,
                "origin": webauthn_service.origin
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"WebAuthn service unhealthy: {str(e)}"
        )

# Error handler for WebAuthn-specific errors
@router.exception_handler(ValueError)
async def webauthn_value_error_handler(request: Request, exc: ValueError):
    """Handle WebAuthn validation errors"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(exc)
    )

@router.exception_handler(TimeoutError)
async def webauthn_timeout_error_handler(request: Request, exc: TimeoutError):
    """Handle WebAuthn timeout errors"""
    return HTTPException(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        detail="WebAuthn operation timed out"
    )
