"""
FastAPI Dependencies for Gastric ADCI Platform

This module provides dependency injection for database sessions, authentication,
and other services throughout the application.
"""

from typing import Optional, Annotated, AsyncGenerator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from core.config.platform_config import config
from data.database.electric import ElectricSQLManager as ElectricManager
from core.services.encryption import encryption_service
from core.services.logger import get_logger
from services.event_logger.service import event_logger, EventCategory, EventSeverity

# Initialize logger
logger = get_logger(__name__)

# HTTP Bearer for JWT token authentication
security = HTTPBearer()

# ElectricSQL Manager (singleton)
electric_manager = ElectricManager()


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get an async database session
    
    Returns:
        AsyncSession: SQLAlchemy async session
    """
    async with electric_manager.get_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def get_electric_manager() -> ElectricManager:
    """
    Dependency to get the ElectricSQL manager
    
    Returns:
        ElectricManager: ElectricSQL manager instance
    """
    return electric_manager


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_database_session)]
):
    """
    Dependency to get current authenticated user
    
    Args:
        credentials: JWT token from Authorization header
        session: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            config.jwt_secret,
            algorithms=[config.jwt_algorithm]
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Log authentication attempt
        await event_logger.log_event(
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.INFO,
            message=f"User authentication: {user_id}",
            metadata={"user_id": user_id}
        )
    
    except jwt.PyJWTError as e:
        # Log failed authentication
        await event_logger.log_event(
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.WARNING,
            message=f"Authentication failed: {str(e)}",
            metadata={"error": str(e)}
        )
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Get user from database using user_id
    # For now, return a mock user
    from data.models import User
    user = User(
        id=user_id,
        email=payload.get("email", "unknown@example.com"),
        role=payload.get("role", "clinician"),
        is_active=True
    )
    
    return user


# ReportGenerator DI
from features.export.report_generator import IntelligentReportGenerator

# Singleton report generator instance
report_generator_instance = IntelligentReportGenerator()

async def get_report_generator() -> IntelligentReportGenerator:
    """Dependency to retrieve the IntelligentReportGenerator instance"""
    return report_generator_instance


# Cohorts service DI
from features.cohorts import CohortsService

# Singleton cohort service instance
cohorts_service_instance = CohortsService()

async def get_cohorts_service() -> CohortsService:
    """Dependency to retrieve the CohortsService instance"""
    return cohorts_service_instance


async def get_current_active_user(
    current_user: Annotated[dict, Depends(get_current_user)]
):
    """
    Dependency to get current active user
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        # Log inactive user attempt
        await event_logger.log_event(
            category=EventCategory.AUTHENTICATION,
            severity=EventSeverity.WARNING,
            message=f"Inactive user login attempt: {current_user.id}",
            metadata={"user_id": current_user.id}
        )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_encryption_service():
    """
    Dependency to get the encryption service
    
    Returns:
        EncryptionService: Encryption service instance
    """
    return encryption_service


def require_role(required_role: str):
    """
    Dependency factory to require specific user role
    
    Args:
        required_role: Required user role (e.g., 'admin', 'clinician', 'researcher')
        
    Returns:
        Function: Dependency function that checks user role
    """
    async def role_checker(
        current_user: Annotated[dict, Depends(get_current_active_user)]
    ):
        if current_user.role != required_role:
            # Log unauthorized access attempt
            await event_logger.log_event(
                category=EventCategory.AUTHORIZATION,
                severity=EventSeverity.WARNING,
                message=f"Unauthorized role access attempt: {current_user.id}",
                metadata={
                    "user_id": current_user.id,
                    "user_role": current_user.role,
                    "required_role": required_role
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role} role"
            )
        return current_user
    
    return role_checker


def require_permissions(required_permissions: list[str]):
    """
    Dependency factory to require specific permissions
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Function: Dependency function that checks user permissions
    """
    async def permission_checker(
        current_user: Annotated[dict, Depends(get_current_active_user)]
    ):
        # TODO: Implement proper permission checking
        # For now, just check if user is active
        if not current_user.is_active:
            # Log unauthorized permission attempt
            await event_logger.log_event(
                category=EventCategory.AUTHORIZATION,
                severity=EventSeverity.WARNING,
                message=f"Insufficient permissions: {current_user.id}",
                metadata={
                    "user_id": current_user.id,
                    "required_permissions": required_permissions
                }
            )
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    
    return permission_checker


# Type aliases for common dependencies
DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]
ElectricManagerDep = Annotated[ElectricManager, Depends(get_electric_manager)]
CurrentUser = Annotated[dict, Depends(get_current_active_user)]
EncryptionService = Annotated[object, Depends(get_encryption_service)]
ReportGenerator = Annotated[IntelligentReportGenerator, Depends(get_report_generator)]
CohortsServiceDep = Annotated[CohortsService, Depends(get_cohorts_service)]
