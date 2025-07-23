"""
User management API endpoints.
Handles user CRUD operations, profile management, and role assignments.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from ...core.security import get_current_user, require_permissions
from ...core.logging import get_logger
from ...db.database import get_db
from ...db.models import User, AuditLog
from ...services.user_service import UserService
from ...schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserList,
    UserRoleUpdate, UserProfile, UserPreferences
)

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger(__name__)
security = HTTPBearer()

@router.get("/", response_model=UserList)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions(["users:read"])),
    db: AsyncSession = Depends(get_db)
):
    """List users with filtering and pagination."""
    try:
        service = UserService(db)
        users, total = await service.list_users(
            skip=skip,
            limit=limit,
            role=role,
            status=status,
            search=search
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="users.list",
            resource_type="user",
            details={"filters": {"role": role, "status": status, "search": search}}
        )
        
        return UserList(
            users=[UserResponse.from_orm(user) for user in users],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve users"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile."""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserProfile,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's profile."""
    try:
        service = UserService(db)
        updated_user = await service.update_user_profile(
            user_id=current_user.id,
            profile_data=user_update.dict(exclude_unset=True)
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="profile.update",
            resource_type="user",
            resource_id=str(current_user.id),
            details={"updated_fields": list(user_update.dict(exclude_unset=True).keys())}
        )
        
        return UserResponse.from_orm(updated_user)
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )

@router.get("/me/preferences", response_model=UserPreferences)
async def get_user_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get current user's preferences."""
    return UserPreferences(
        theme=current_user.preferences.get("theme", "light"),
        language=current_user.preferences.get("language", "en"),
        notifications=current_user.preferences.get("notifications", {}),
        dashboard_layout=current_user.preferences.get("dashboard_layout", "default")
    )

@router.put("/me/preferences", response_model=UserPreferences)
async def update_user_preferences(
    preferences: UserPreferences,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's preferences."""
    try:
        service = UserService(db)
        updated_user = await service.update_user_preferences(
            user_id=current_user.id,
            preferences=preferences.dict()
        )
        
        return UserPreferences(
            theme=updated_user.preferences.get("theme", "light"),
            language=updated_user.preferences.get("language", "en"),
            notifications=updated_user.preferences.get("notifications", {}),
            dashboard_layout=updated_user.preferences.get("dashboard_layout", "default")
        )
    except Exception as e:
        logger.error(f"Error updating user preferences: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_permissions(["users:read"])),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID."""
    try:
        service = UserService(db)
        user = await service.get_user_by_id(user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        await service.log_audit(
            user_id=current_user.id,
            action="user.read",
            resource_type="user",
            resource_id=user_id
        )
        
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user"
        )

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(require_permissions(["users:create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user."""
    try:
        service = UserService(db)
        
        # Check if user already exists
        existing_user = await service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
        
        new_user = await service.create_user(user_data.dict())
        
        await service.log_audit(
            user_id=current_user.id,
            action="user.create",
            resource_type="user",
            resource_id=str(new_user.id),
            details={"email": user_data.email, "role": user_data.role}
        )
        
        return UserResponse.from_orm(new_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_permissions(["users:update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update user by ID."""
    try:
        service = UserService(db)
        
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        updated_user = await service.update_user(
            user_id=user_id,
            update_data=user_update.dict(exclude_unset=True)
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="user.update",
            resource_type="user",
            resource_id=user_id,
            details={"updated_fields": list(user_update.dict(exclude_unset=True).keys())}
        )
        
        return UserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: str,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_permissions(["users:update_role"])),
    db: AsyncSession = Depends(get_db)
):
    """Update user's role."""
    try:
        service = UserService(db)
        
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        updated_user = await service.update_user_role(
            user_id=user_id,
            new_role=role_update.role,
            permissions=role_update.permissions
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="user.role_update",
            resource_type="user",
            resource_id=user_id,
            details={"old_role": user.role, "new_role": role_update.role}
        )
        
        return UserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user role"
        )

@router.put("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    status_update: dict,
    current_user: User = Depends(require_permissions(["users:update_status"])),
    db: AsyncSession = Depends(get_db)
):
    """Update user's status (active/inactive/suspended)."""
    try:
        service = UserService(db)
        
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        new_status = status_update.get("status")
        if new_status not in ["active", "inactive", "suspended"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status. Must be 'active', 'inactive', or 'suspended'"
            )
        
        updated_user = await service.update_user_status(
            user_id=user_id,
            new_status=new_status,
            reason=status_update.get("reason")
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="user.status_update",
            resource_type="user",
            resource_id=user_id,
            details={
                "old_status": user.is_active,
                "new_status": new_status,
                "reason": status_update.get("reason")
            }
        )
        
        return UserResponse.from_orm(updated_user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user status {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user status"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_permissions(["users:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete user by ID."""
    try:
        service = UserService(db)
        
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deletion
        if user_id == str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        await service.soft_delete_user(user_id)
        
        await service.log_audit(
            user_id=current_user.id,
            action="user.delete",
            resource_type="user",
            resource_id=user_id,
            details={"email": user.email}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/{user_id}/audit-log")
async def get_user_audit_log(
    user_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    action: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions(["audit:read"])),
    db: AsyncSession = Depends(get_db)
):
    """Get user's audit log."""
    try:
        service = UserService(db)
        
        # Verify user exists
        user = await service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        audit_logs, total = await service.get_user_audit_log(
            user_id=user_id,
            skip=skip,
            limit=limit,
            action=action
        )
        
        return {
            "audit_logs": audit_logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve audit log"
        )
