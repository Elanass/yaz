"""
Core dependencies for API endpoints
"""
from typing import Dict, Any, Optional
from enum import Enum
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class Domain(Enum):
    """Security domains"""
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"

class Scope(Enum):
    """Permission scopes"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Get current user from token - returns None if no auth"""
    if not credentials:
        return None
    # Simplified for MVP - replace with proper JWT validation
    return {"id": "test_user", "role": "clinician"}

async def optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Optional user authentication"""
    return await get_current_user(credentials)

async def require_auth(current_user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authentication"""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    return current_user

def require_role(domain: Domain = None, scope: Scope = None, required_role: str = "clinician"):
    """Require specific user role and permissions"""
    def role_checker(current_user: Dict[str, Any] = Depends(require_auth)):
        if current_user.get("role") != required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        # Simplified permission check - in real implementation, check domain/scope permissions
        return current_user
    return role_checker

class AuthService:
    """Authentication service for dependency injection"""
    
    def __init__(self):
        self.security = security
    
    async def get_current_user(self, credentials: Optional[HTTPAuthorizationCredentials] = None) -> Optional[Dict[str, Any]]:
        """Get current user from token"""
        return await get_current_user(credentials)
    
    async def require_auth(self, current_user: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Require authentication"""
        return await require_auth(current_user)
