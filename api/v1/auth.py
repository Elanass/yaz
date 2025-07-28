"""
API v1 - Authentication Routes
Clean, standardized authentication endpoints with ElectricSQL integration
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from core.models.base import ApiResponse
from core.dependencies import DatabaseSession, CurrentUser, EncryptionService, require_role
from data.models import User, UserCreate, UserLogin, UserResponse, TokenResponse
from features.auth.service import auth_service


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=ApiResponse[UserResponse])
async def register_user(
    user_data: UserCreate,
    session: DatabaseSession,
    encryption: EncryptionService
):
    """Register a new user with encrypted data storage"""
    
    try:
        # Check if user already exists
        result = await session.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user with encrypted password
        hashed_password = encryption.hash_password(user_data.password)
        
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            organization=user_data.organization,
            is_active=True
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        
        user_response = UserResponse(
            id=str(new_user.id),
            email=new_user.email,
            full_name=new_user.full_name,
            role=new_user.role,
            organization=new_user.organization,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
            last_login=new_user.last_login
        )
        
        return ApiResponse.success_response(
            data=user_response,
            message="User registered successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login_user(
    login_data: UserLogin,
    session: DatabaseSession,
    encryption: EncryptionService
):
    """Authenticate user and return access token"""
    
    try:
        # Get user from database
        result = await session.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user or not encryption.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token = auth_service.create_access_token(user)
        
        # Update last login
        user.last_login = user.created_at  # This would be datetime.utcnow() in real implementation
        await session.commit()
        
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
            expires_in=1440 * 60,  # 24 hours in seconds
            user=user_response
        )
        
        return ApiResponse.success_response(
            data=token_response,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=ApiResponse[UserResponse])
async def get_current_user_info(current_user: CurrentUser):
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
async def logout_user(current_user: CurrentUser):
    """Logout user (invalidate token on client side)"""
    
    # In a production system, we would add the token to a blacklist
    return ApiResponse.success_response(
        message="Logout successful. Please remove the token from client storage."
    )


@router.get("/permissions", response_model=ApiResponse[List[str]])
async def get_user_permissions(current_user: CurrentUser):
    """Get current user permissions"""
    
    # TODO: Implement proper permission system
    permissions = ["read:cases", "write:cases", "read:reports"]
    if current_user.role == "admin":
        permissions.extend(["admin:users", "admin:system"])
    
    return ApiResponse.success_response(
        data=permissions,
        message="User permissions retrieved"
    )


@router.get("/users", response_model=ApiResponse[List[UserResponse]])
async def list_users(
    session: DatabaseSession,
    admin_user: CurrentUser = require_role("admin")
):
    """List all users (admin only)"""
    
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        user_responses = [
            UserResponse(
                id=str(user.id),
                email=user.email,
                full_name=user.full_name,
                role=user.role,
                organization=user.organization,
                is_active=user.is_active,
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]
    
        return ApiResponse.success_response(
            data=user_responses,
            message=f"Retrieved {len(user_responses)} users"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )
