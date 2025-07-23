"""
Authentication and authorization endpoints
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from ...core.security import (
    password_manager, 
    jwt_manager, 
    rbac_manager, 
    get_current_user
)
from ...core.logging import security_logger, clinical_logger
from ...db.database import get_async_session
from ...services.user_service import UserService

router = APIRouter()


class UserRegistration(BaseModel):
    """User registration model"""
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str
    role: str = "patient"
    license_number: str = None
    institution: str = None
    specialization: str = None


class LoginResponse(BaseModel):
    """Login response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class PasswordReset(BaseModel):
    """Password reset model"""
    email: EmailStr


class PasswordChange(BaseModel):
    """Password change model"""
    current_password: str
    new_password: str


@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserRegistration,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Register a new user"""
    try:
        user_service = UserService(db)
        
        # Validate role
        if user_data.role not in ["patient", "practitioner", "researcher"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role specified"
            )
        
        # Check if user already exists
        existing_user = await user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        existing_username = await user_service.get_user_by_username(user_data.username)
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        new_user = await user_service.create_user(user_data.dict())
        
        # Log registration
        security_logger.log_authentication_attempt(
            user_id=str(new_user.id),
            success=True,
            ip_address=request.client.host
        )
        
        clinical_logger.log_patient_access(
            user_id=str(new_user.id),
            patient_id=str(new_user.id) if user_data.role == "patient" else None,
            operation="registration",
            details={"role": user_data.role}
        )
        
        return {
            "message": "User registered successfully",
            "user_id": str(new_user.id),
            "email": new_user.email,
            "role": new_user.role.value
        }
        
    except HTTPException:
        raise
    except Exception as e:
        security_logger.log_suspicious_activity(
            user_id="unknown",
            activity="registration_failure",
            details={"error": str(e), "email": user_data.email}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: AsyncSession = Depends(get_async_session)
):
    """Authenticate user and return tokens"""
    try:
        user_service = UserService(db)
        
        # Authenticate user
        user = await user_service.authenticate_user(form_data.username, form_data.password)
        if not user:
            security_logger.log_authentication_attempt(
                user_id=form_data.username,
                success=False,
                ip_address=request.client.host if request else "unknown"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.is_active:
            security_logger.log_authentication_attempt(
                user_id=str(user.id),
                success=False,
                ip_address=request.client.host if request else "unknown"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
        
        # Create tokens
        access_token_expires = timedelta(minutes=jwt_manager.expire_minutes)
        access_token = jwt_manager.create_access_token(
            data={"sub": str(user.id), "role": user.role.value},
            expires_delta=access_token_expires
        )
        refresh_token = jwt_manager.create_refresh_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        
        # Update last login
        await user_service.update_last_login(user.id)
        
        # Log successful login
        security_logger.log_authentication_attempt(
            user_id=str(user.id),
            success=True,
            ip_address=request.client.host if request else "unknown"
        )
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=jwt_manager.expire_minutes * 60,
            user={
                "id": str(user.id),
                "email": user.email,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": user.role.value,
                "is_verified": user.is_verified
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        security_logger.log_suspicious_activity(
            user_id="unknown",
            activity="login_failure",
            details={"error": str(e), "username": form_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh")
async def refresh_token(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Refresh access token"""
    try:
        # Verify this is a refresh token
        if current_user.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_service = UserService(db)
        user = await user_service.get_user_by_id(current_user["sub"])
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=jwt_manager.expire_minutes)
        access_token = jwt_manager.create_access_token(
            data={"sub": str(user.id), "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": jwt_manager.expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    request: Request = None
):
    """Logout user (invalidate token)"""
    try:
        # In a production system, you would add the token to a blacklist
        # For now, we just log the logout
        security_logger.log_authentication_attempt(
            user_id=current_user["sub"],
            success=True,  # Successful logout
            ip_address=request.client.host if request else "unknown"
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_async_session)
):
    """Request password reset"""
    try:
        user_service = UserService(db)
        
        # Check if user exists
        user = await user_service.get_user_by_email(reset_data.email)
        if not user:
            # Don't reveal if user exists or not
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token (in production, send email)
        reset_token = jwt_manager.create_access_token(
            data={"sub": str(user.id), "type": "password_reset"},
            expires_delta=timedelta(hours=1)  # 1 hour expiry
        )
        
        # Log password reset request
        security_logger.log_suspicious_activity(
            user_id=str(user.id),
            activity="password_reset_requested",
            details={"email": reset_data.email}
        )
        
        # In production, send email with reset link
        # For now, return the token (for testing)
        return {
            "message": "If the email exists, a reset link has been sent",
            "reset_token": reset_token  # Remove in production
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Change user password"""
    try:
        user_service = UserService(db)
        
        # Get user
        user = await user_service.get_user_by_id(current_user["sub"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not password_manager.verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        await user_service.update_password(user.id, password_data.new_password)
        
        # Log password change
        security_logger.log_suspicious_activity(
            user_id=str(user.id),
            activity="password_changed",
            details={"user_id": str(user.id)}
        )
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/me")
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get current user information"""
    try:
        user_service = UserService(db)
        user = await user_service.get_user_by_id(current_user["sub"])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "license_number": user.license_number,
            "institution": user.institution,
            "specialization": user.specialization,
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "permissions": rbac_manager.get_user_permissions(user.role.value)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )
