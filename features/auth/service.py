"""
Authentication Feature Module
Centralized authentication and authorization functionality
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from core.config.settings import get_feature_config
from core.models.base import BaseEntity, Domain, Scope, UserRole
from core.services.base import BaseService
from core.utils.helpers import DateUtils, HashUtils

# Schemas
class UserCreate(BaseModel):
    """User creation schema"""
    
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: str = Field(..., description="Full name")
    role: UserRole = Field(default=UserRole.CLINICIAN, description="User role")
    organization: Optional[str] = Field(None, description="Organization")


class UserLogin(BaseModel):
    """User login schema"""
    
    email: str = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """User response schema"""
    
    id: str
    email: str
    full_name: str
    role: UserRole
    organization: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


class TokenResponse(BaseModel):
    """JWT token response"""
    
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class Permission(BaseModel):
    """Permission schema"""
    
    domain: Domain
    scope: Scope
    
    def __str__(self) -> str:
        return f"{self.domain}:{self.scope}"


# Models
class User(BaseEntity):
    """User entity"""
    
    email: str
    password_hash: str
    full_name: str
    role: UserRole
    organization: Optional[str] = None
    is_active: bool = True
    last_login: Optional[datetime] = None
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    
    def check_password(self, password: str) -> bool:
        """Check if password is correct"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def set_password(self, password: str) -> None:
        """Set user password"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until and datetime.utcnow() < self.locked_until:
            return True
        return False
    
    def get_permissions(self) -> List[Permission]:
        """Get user permissions based on role"""
        permissions = []
        
        if self.role == UserRole.ADMIN:
            # Admin has all permissions
            for domain in Domain:
                for scope in Scope:
                    permissions.append(Permission(domain=domain, scope=scope))
        
        elif self.role == UserRole.CLINICIAN:
            # Clinicians have healthcare access
            permissions.extend([
                Permission(domain=Domain.HEALTHCARE, scope=Scope.READ),
                Permission(domain=Domain.HEALTHCARE, scope=Scope.WRITE),
                Permission(domain=Domain.LOGISTICS, scope=Scope.READ),
            ])
        
        elif self.role == UserRole.RESEARCHER:
            # Researchers have research and read access
            permissions.extend([
                Permission(domain=Domain.RESEARCH, scope=Scope.READ),
                Permission(domain=Domain.RESEARCH, scope=Scope.WRITE),
                Permission(domain=Domain.HEALTHCARE, scope=Scope.READ),
                Permission(domain=Domain.LOGISTICS, scope=Scope.READ),
            ])
        
        elif self.role == UserRole.PATIENT:
            # Patients have limited access
            permissions.extend([
                Permission(domain=Domain.HEALTHCARE, scope=Scope.READ),
            ])
        
        return permissions


# Services
class AuthService(BaseService):
    """Authentication service"""
    
    def __init__(self):
        super().__init__()
        self.config = get_feature_config("auth")
        self.users: Dict[str, User] = {}  # In-memory store for MVP
        
        # Create default admin user
        self._create_default_admin()
    
    def _create_default_admin(self):
        """Create default admin user for development"""
        admin_email = "admin@gastric-adci.com"
        if admin_email not in self.users:
            # Hash the default password
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), salt).decode('utf-8')
            
            admin = User(
                email=admin_email,
                password_hash=password_hash,
                full_name="System Administrator",
                role=UserRole.ADMIN,
                organization="Gastric ADCI Platform"
            )
            self.users[admin_email] = admin
            self.logger.info("Created default admin user")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create new user"""
        
        # Check if user already exists
        if user_data.email in self.users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
        
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            organization=user_data.organization,
            password_hash=hashed_password
        )
        
        # Store user
        self.users[user.email] = user
        
        self.logger.info(f"Created user: {user.email}")
        return user
    
    async def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        
        user = self.users.get(email)
        if not user:
            return None
        
        # Check if account is locked
        if user.is_locked():
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked due to failed login attempts"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        # Verify password
        if not user.check_password(password):
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                self.logger.warning(f"Account locked for user: {email}")
            
            return None
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        
        self.logger.info(f"User authenticated: {email}")
        return user
    
    def create_access_token(self, user: User) -> str:
        """Create JWT access token"""
        
        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": datetime.utcnow() + timedelta(minutes=self.config["token_expire_minutes"]),
            "iat": datetime.utcnow(),
        }
        
        return jwt.encode(
            payload,
            self.config["secret_key"],
            algorithm=self.config["algorithm"]
        )
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify JWT token and return payload"""
        
        try:
            payload = jwt.decode(
                token,
                self.config["secret_key"],
                algorithms=[self.config["algorithm"]]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        for user in self.users.values():
            if str(user.id) == user_id:
                return user
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.users.get(email)


# Dependencies
security = HTTPBearer()
auth_service = AuthService()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    
    payload = auth_service.verify_token(credentials.credentials)
    user = await auth_service.get_user_by_id(payload["sub"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def require_role(required_role: UserRole):
    """Dependency to require specific user role"""
    
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_role.value} required"
            )
        return current_user
    
    return role_checker


def require_permission(domain: Domain, scope: Scope):
    """Dependency to require specific permission"""
    
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        user_permissions = current_user.get_permissions()
        required_permission = Permission(domain=domain, scope=scope)
        
        # Check if user has the specific permission or admin access
        has_permission = any(
            perm.domain == domain and perm.scope == scope
            for perm in user_permissions
        )
        
        is_admin = any(
            perm.domain == Domain.ADMIN and perm.scope == Scope.ADMIN
            for perm in user_permissions
        )
        
        if not (has_permission or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission {domain}:{scope} required"
            )
        
        return current_user
    
    return permission_checker
