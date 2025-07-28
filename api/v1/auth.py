"""
API v1 - Authentication Routes
Clean, standardized authentication endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from typing import List

from core.models.base import ApiResponse
from features.auth.service import (
    AuthService, User, UserCreate, UserLogin, UserResponse, TokenResponse,
    auth_service, get_current_user, require_role, UserRole
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register_user(user_data: UserCreate):
    """Register a new user"""
    
    try:
        user = await auth_service.create_user(user_data)
        
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            organization=user.organization,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        return ApiResponse.success_response(
            data=user_response,
            message="User registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login_user(login_data: UserLogin):
    """Authenticate user and return access token"""
    
    try:
        user = await auth_service.authenticate_user(login_data.email, login_data.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        
        # Create response
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            organization=user.organization,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
        token_response = TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.config["token_expire_minutes"] * 60,
            user=user_response
        )
        
        return ApiResponse.success_response(
            data=token_response,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    
    user_response = UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        organization=current_user.organization,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )
    
    return ApiResponse.success_response(
        data=user_response,
        message="User information retrieved"
    )


@router.post("/logout", response_model=ApiResponse[None])
async def logout_user(current_user: User = Depends(get_current_user)):
    """Logout user (invalidate token on client side)"""
    
    # In a production system, we would add the token to a blacklist
    return ApiResponse.success_response(
        message="Logout successful. Please remove the token from client storage."
    )


@router.get("/permissions", response_model=ApiResponse[List[str]])
async def get_user_permissions(current_user: User = Depends(get_current_user)):
    """Get current user permissions"""
    
    permissions = [str(perm) for perm in current_user.get_permissions()]
    
    return ApiResponse.success_response(
        data=permissions,
        message="User permissions retrieved"
    )


@router.get("/users", response_model=ApiResponse[List[UserResponse]])
async def list_users(admin_user: User = Depends(require_role(UserRole.ADMIN))):
    """List all users (admin only)"""
    
    users = []
    for user in auth_service.users.values():
        user_response = UserResponse(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            organization=user.organization,
            is_active=user.is_active,
            created_at=user.created_at,
            last_login=user.last_login
        )
        users.append(user_response)
    
    return ApiResponse.success_response(
        data=users,
        message=f"Retrieved {len(users)} users"
    )
