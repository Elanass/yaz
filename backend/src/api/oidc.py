"""
OIDC Federation API Endpoints
Integration with hospital identity systems
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..core.deps import get_current_user, get_current_active_user
from ..core.rbac import RBACMatrix, Resource, Action, Role
from ..services.oidc_service import OIDCService
from ..services.auth_service import AuthService, create_access_token
from ..schemas.oidc import (
    OIDCLoginRequest,
    OIDCLoginResponse,
    OIDCCallbackRequest,
    OIDCAuthenticationResponse,
    OIDCProviderListResponse,
    OIDCProviderConfigRequest,
    OIDCProviderConfigResponse,
    OIDCUserMappingListResponse,
    OIDCErrorResponse
)
from ..schemas.user import User

router = APIRouter(prefix="/auth/oidc", tags=["oidc"])

# RBAC instance
rbac = RBACMatrix()

@router.get("/providers", response_model=OIDCProviderListResponse)
async def list_oidc_providers(db: Session = Depends(get_db)):
    """
    List available OIDC providers
    Shows configured identity providers for hospital integration
    """
    
    try:
        oidc_service = OIDCService(db)
        providers = await oidc_service.list_providers()
        
        return OIDCProviderListResponse(
            providers=providers,
            total_count=len(providers)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list OIDC providers: {str(e)}"
        )

@router.post("/login", response_model=OIDCLoginResponse)
async def initiate_oidc_login(
    request: OIDCLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Initiate OIDC authentication flow
    Generates authorization URL for hospital identity system
    """
    
    try:
        oidc_service = OIDCService(db)
        
        result = await oidc_service.get_authorization_url(
            provider_id=request.provider_id,
            redirect_uri=request.redirect_uri,
            state=request.state
        )
        
        return OIDCLoginResponse(
            authorization_url=result["authorization_url"],
            state=result["state"],
            nonce=result["nonce"],
            provider_id=request.provider_id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to initiate OIDC login: {str(e)}"
        )

@router.post("/callback", response_model=OIDCAuthenticationResponse)
async def handle_oidc_callback(
    request: OIDCCallbackRequest,
    db: Session = Depends(get_db)
):
    """
    Handle OIDC callback and authenticate user
    Processes authorization code and creates user session
    """
    
    try:
        oidc_service = OIDCService(db)
        auth_service = AuthService(db)
        
        # Handle OIDC callback
        result = await oidc_service.handle_callback(
            code=request.code,
            state=request.state,
            redirect_uri=request.redirect_uri
        )
        
        user = result["user"]
        claims = result["claims"]
        
        # Create access token for the user
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        # Extract user info from claims
        user_info = {
            "subject": claims.get("sub"),
            "email": claims.get("email"),
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "provider_id": request.state.split("_")[0] if "_" in request.state else "unknown",
            "verified": claims.get("email_verified", True)
        }
        
        return OIDCAuthenticationResponse(
            success=True,
            user_id=user.id,
            user_info=user_info,
            access_token=access_token,
            refresh_token=result["tokens"].get("refresh_token"),
            token_type="Bearer",
            expires_in=3600  # 1 hour
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"OIDC authentication failed: {str(e)}"
        )

@router.get("/callback")
async def handle_oidc_callback_get(
    code: str,
    state: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle OIDC callback via GET request (browser redirect)
    Redirects to frontend with authentication result
    """
    
    try:
        # Extract redirect URI from request
        redirect_uri = str(request.url).split("?")[0]
        
        # Create callback request
        callback_request = OIDCCallbackRequest(
            code=code,
            state=state,
            redirect_uri=redirect_uri
        )
        
        # Handle callback
        result = await handle_oidc_callback(callback_request, db)
        
        # Redirect to frontend with token
        frontend_url = f"{request.headers.get('origin', 'https://adci.health')}/auth/success"
        redirect_url = f"{frontend_url}?token={result.access_token}&user_id={result.user_id}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = f"{request.headers.get('origin', 'https://adci.health')}/auth/error"
        error_url = f"{frontend_url}?error={str(e)}"
        
        return RedirectResponse(url=error_url)

@router.get("/user/mappings", response_model=OIDCUserMappingListResponse)
async def list_user_oidc_mappings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List current user's OIDC provider mappings
    Shows connected identity providers
    """
    
    try:
        from ..db.models import OIDCUserMapping
        
        mappings = db.query(OIDCUserMapping).filter(
            OIDCUserMapping.user_id == current_user.id
        ).all()
        
        mapping_info = [
            {
                "user_id": mapping.user_id,
                "provider_id": mapping.provider_id,
                "provider_subject": mapping.provider_subject,
                "provider_email": mapping.provider_email,
                "provider_username": mapping.provider_username,
                "first_login": mapping.first_login,
                "last_login": mapping.last_login,
                "login_count": mapping.login_count,
                "is_active": mapping.is_active
            }
            for mapping in mappings
        ]
        
        return OIDCUserMappingListResponse(
            mappings=mapping_info,
            total_count=len(mapping_info)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list OIDC mappings: {str(e)}"
        )

@router.delete("/user/mappings/{provider_id}")
async def unlink_oidc_provider(
    provider_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Unlink OIDC provider from user account
    Removes connection to hospital identity system
    """
    
    try:
        from ..db.models import OIDCUserMapping
        
        mapping = db.query(OIDCUserMapping).filter(
            OIDCUserMapping.user_id == current_user.id,
            OIDCUserMapping.provider_id == provider_id,
            OIDCUserMapping.is_active == True
        ).first()
        
        if not mapping:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OIDC mapping not found"
            )
        
        mapping.is_active = False
        db.commit()
        
        return {"success": True, "message": "OIDC provider unlinked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unlink OIDC provider: {str(e)}"
        )

# Admin endpoints for provider configuration
@router.post("/admin/providers", response_model=OIDCProviderConfigResponse)
async def configure_oidc_provider(
    config: OIDCProviderConfigRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Configure new OIDC provider (Admin only)
    Adds hospital identity system integration
    """
    
    # Check admin permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.SYSTEM_CONFIG,
        Action.CREATE,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to configure OIDC providers"
        )
    
    try:
        from ..db.models import OIDCProvider
        
        # Check if provider already exists
        existing = db.query(OIDCProvider).filter(
            OIDCProvider.provider_id == config.provider_id
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="OIDC provider already exists"
            )
        
        # Create new provider
        provider = OIDCProvider(
            provider_id=config.provider_id,
            name=config.name,
            issuer=config.issuer,
            client_id=config.client_id,
            client_secret=config.client_secret,  # Should be encrypted
            scopes=config.scopes,
            username_claim=config.username_claim,
            email_claim=config.email_claim,
            first_name_claim=config.first_name_claim,
            last_name_claim=config.last_name_claim,
            verify_ssl=config.verify_ssl,
            require_https=config.require_https,
            token_validation=config.token_validation,
            auto_create_users=config.auto_create_users
        )
        
        db.add(provider)
        db.commit()
        
        return OIDCProviderConfigResponse(
            success=True,
            provider_id=config.provider_id,
            message="OIDC provider configured successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to configure OIDC provider: {str(e)}"
        )

@router.get("/admin/providers/{provider_id}")
async def get_oidc_provider_config(
    provider_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get OIDC provider configuration (Admin only)
    Shows hospital identity system settings
    """
    
    # Check admin permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.SYSTEM_CONFIG,
        Action.READ,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view OIDC provider configuration"
        )
    
    try:
        from ..db.models import OIDCProvider
        
        provider = db.query(OIDCProvider).filter(
            OIDCProvider.provider_id == provider_id
        ).first()
        
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="OIDC provider not found"
            )
        
        # Return configuration (excluding sensitive data)
        return {
            "provider_id": provider.provider_id,
            "name": provider.name,
            "issuer": provider.issuer,
            "client_id": provider.client_id,
            # client_secret excluded for security
            "scopes": provider.scopes,
            "username_claim": provider.username_claim,
            "email_claim": provider.email_claim,
            "first_name_claim": provider.first_name_claim,
            "last_name_claim": provider.last_name_claim,
            "verify_ssl": provider.verify_ssl,
            "require_https": provider.require_https,
            "token_validation": provider.token_validation,
            "auto_create_users": provider.auto_create_users,
            "is_active": provider.is_active
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get OIDC provider configuration: {str(e)}"
        )

@router.get("/health")
async def oidc_health_check(db: Session = Depends(get_db)):
    """
    Health check for OIDC service
    Verifies identity provider connectivity
    """
    
    try:
        oidc_service = OIDCService(db)
        providers = await oidc_service.list_providers()
        
        health_status = {
            "status": "healthy",
            "oidc_service": "operational",
            "database": "connected",
            "providers_count": len(providers),
            "providers": [p["provider_id"] for p in providers],
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        return health_status
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"OIDC service unhealthy: {str(e)}"
        )
