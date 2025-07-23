"""
User service for managing user operations.
Handles user CRUD, authentication, and profile management.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, delete
from sqlalchemy.orm import selectinload
from passlib.context import CryptContext
import uuid

from ..db.models import User, AuditLog
from ..core.security import create_access_token, verify_password, get_password_hash
from ..core.logging import get_logger

logger = get_logger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """Service class for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        try:
            # Hash password
            if "password" in user_data:
                user_data["password"] = get_password_hash(user_data["password"])
            
            # Generate user ID
            user_data["id"] = uuid.uuid4()
            
            # Set default values
            user_data.setdefault("is_active", True)
            user_data.setdefault("role", "patient")
            user_data.setdefault("preferences", {})
            user_data.setdefault("permissions", [])
            
            user = User(**user_data)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            logger.info(f"Created user: {user.email}")
            return user
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        try:
            result = await self.db.execute(
                select(User).where(
                    and_(User.id == user_id, User.deleted_at.is_(None))
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        try:
            result = await self.db.execute(
                select(User).where(
                    and_(User.email == email, User.deleted_at.is_(None))
                )
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            raise
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            if not verify_password(password, user.password):
                return None
            
            if not user.is_active:
                return None
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            await self.db.commit()
            
            return user
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {str(e)}")
            raise
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 50,
        role: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[User], int]:
        """List users with filtering and pagination."""
        try:
            query = select(User).where(User.deleted_at.is_(None))
            
            # Apply filters
            if role:
                query = query.where(User.role == role)
            
            if status:
                if status == "active":
                    query = query.where(User.is_active == True)
                elif status == "inactive":
                    query = query.where(User.is_active == False)
            
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        User.first_name.ilike(search_term),
                        User.last_name.ilike(search_term),
                        User.email.ilike(search_term)
                    )
                )
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = count_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            query = query.order_by(User.created_at.desc())
            
            result = await self.db.execute(query)
            users = result.scalars().all()
            
            return list(users), total
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            raise
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> User:
        """Update user information."""
        try:
            # Hash password if provided
            if "password" in update_data:
                update_data["password"] = get_password_hash(update_data["password"])
            
            update_data["updated_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(User)
                .where(and_(User.id == user_id, User.deleted_at.is_(None)))
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_user_by_id(user_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating user {user_id}: {str(e)}")
            raise
    
    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> User:
        """Update user profile information."""
        try:
            # Only allow certain fields to be updated in profile
            allowed_fields = [
                "first_name", "last_name", "phone", "date_of_birth",
                "gender", "address", "emergency_contact"
            ]
            
            filtered_data = {
                k: v for k, v in profile_data.items() 
                if k in allowed_fields
            }
            
            if not filtered_data:
                return await self.get_user_by_id(user_id)
            
            return await self.update_user(user_id, filtered_data)
        except Exception as e:
            logger.error(f"Error updating user profile {user_id}: {str(e)}")
            raise
    
    async def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> User:
        """Update user preferences."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Merge with existing preferences
            current_prefs = user.preferences or {}
            current_prefs.update(preferences)
            
            return await self.update_user(user_id, {"preferences": current_prefs})
        except Exception as e:
            logger.error(f"Error updating user preferences {user_id}: {str(e)}")
            raise
    
    async def update_user_role(
        self, 
        user_id: str, 
        new_role: str, 
        permissions: List[str] = None
    ) -> User:
        """Update user role and permissions."""
        try:
            update_data = {"role": new_role}
            if permissions is not None:
                update_data["permissions"] = permissions
            
            return await self.update_user(user_id, update_data)
        except Exception as e:
            logger.error(f"Error updating user role {user_id}: {str(e)}")
            raise
    
    async def update_user_status(
        self, 
        user_id: str, 
        new_status: str, 
        reason: Optional[str] = None
    ) -> User:
        """Update user status."""
        try:
            is_active = new_status == "active"
            update_data = {"is_active": is_active}
            
            if reason:
                user = await self.get_user_by_id(user_id)
                metadata = user.metadata or {}
                metadata["status_history"] = metadata.get("status_history", [])
                metadata["status_history"].append({
                    "status": new_status,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat()
                })
                update_data["metadata"] = metadata
            
            return await self.update_user(user_id, update_data)
        except Exception as e:
            logger.error(f"Error updating user status {user_id}: {str(e)}")
            raise
    
    async def soft_delete_user(self, user_id: str) -> None:
        """Soft delete user."""
        try:
            await self.db.execute(
                update(User)
                .where(and_(User.id == user_id, User.deleted_at.is_(None)))
                .values(
                    deleted_at=datetime.utcnow(),
                    is_active=False
                )
            )
            await self.db.commit()
            
            logger.info(f"Soft deleted user: {user_id}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error soft deleting user {user_id}: {str(e)}")
            raise
    
    async def change_password(
        self, 
        user_id: str, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password."""
        try:
            user = await self.get_user_by_id(user_id)
            if not user:
                return False
            
            if not verify_password(current_password, user.password):
                return False
            
            new_password_hash = get_password_hash(new_password)
            await self.update_user(user_id, {"password": new_password_hash})
            
            logger.info(f"Password changed for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error changing password for user {user_id}: {str(e)}")
            raise
    
    async def reset_password(self, email: str) -> Optional[str]:
        """Generate password reset token."""
        try:
            user = await self.get_user_by_email(email)
            if not user:
                return None
            
            # Generate reset token (valid for 1 hour)
            reset_token = create_access_token(
                data={"sub": str(user.id), "type": "password_reset"},
                expires_delta=timedelta(hours=1)
            )
            
            # Store reset token hash in user metadata
            metadata = user.metadata or {}
            metadata["reset_token"] = get_password_hash(reset_token)
            metadata["reset_token_expires"] = (
                datetime.utcnow() + timedelta(hours=1)
            ).isoformat()
            
            await self.update_user(str(user.id), {"metadata": metadata})
            
            logger.info(f"Password reset token generated for user: {email}")
            return reset_token
        except Exception as e:
            logger.error(f"Error generating reset token for {email}: {str(e)}")
            raise
    
    async def get_user_audit_log(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 50,
        action: Optional[str] = None
    ) -> Tuple[List[Dict], int]:
        """Get audit log for a user."""
        try:
            query = select(AuditLog).where(AuditLog.user_id == user_id)
            
            if action:
                query = query.where(AuditLog.action.ilike(f"%{action}%"))
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = count_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            query = query.order_by(AuditLog.timestamp.desc())
            
            result = await self.db.execute(query)
            audit_logs = result.scalars().all()
            
            # Convert to dict format
            logs_data = []
            for log in audit_logs:
                logs_data.append({
                    "id": str(log.id),
                    "action": log.action,
                    "resource_type": log.resource_type,
                    "resource_id": log.resource_id,
                    "timestamp": log.timestamp.isoformat(),
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "details": log.details
                })
            
            return logs_data, total
        except Exception as e:
            logger.error(f"Error getting audit log for user {user_id}: {str(e)}")
            raise
    
    async def log_audit(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log audit event."""
        try:
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            # Don't raise - audit logging should not break the main flow
