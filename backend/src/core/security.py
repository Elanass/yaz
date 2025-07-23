"""
Security middleware and utilities for HIPAA/GDPR compliance
"""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
import bcrypt

from .config import get_settings


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for HIPAA/GDPR compliance"""
    
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        
        # Add security headers
        response = await call_next(request)
        
        # Security headers for healthcare compliance
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' cdn.jsdelivr.net unpkg.com; "
            "style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; "
            "img-src 'self' data: blob:; "
            "connect-src 'self' ws: wss:; "
            "frame-ancestors 'none';"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Remove server information
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class PasswordManager:
    """Secure password management for clinical users"""
    
    def __init__(self):
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # HIPAA-compliant rounds
        )
    
    def hash_password(self, password: str) -> str:
        """Hash password with bcrypt"""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_secure_password(self, length: int = 16) -> str:
        """Generate a secure password for system accounts"""
        alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))


class JWTManager:
    """JWT token management for session handling"""
    
    def __init__(self):
        self.settings = get_settings()
        self.algorithm = self.settings.jwt_algorithm
        self.secret_key = self.settings.jwt_secret
        self.expire_minutes = self.settings.jwt_expire_minutes
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token (longer expiry)"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=30)  # 30 days for refresh
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


class ClinicalDataEncryption:
    """Encryption utilities for clinical data (HIPAA compliance)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.key = self.settings.clinical_data_encryption_key.encode()
    
    def encrypt_clinical_data(self, data: str) -> str:
        """Encrypt sensitive clinical data"""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        # Generate salt
        salt = secrets.token_bytes(16)
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.key))
        
        # Encrypt
        f = Fernet(key)
        encrypted_data = f.encrypt(data.encode())
        
        # Return salt + encrypted data (base64 encoded)
        return base64.b64encode(salt + encrypted_data).decode()
    
    def decrypt_clinical_data(self, encrypted_data: str) -> str:
        """Decrypt clinical data"""
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        import base64
        
        # Decode the data
        data = base64.b64decode(encrypted_data.encode())
        
        # Extract salt and encrypted data
        salt = data[:16]
        encrypted_data = data[16:]
        
        # Derive key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.key))
        
        # Decrypt
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data)
        
        return decrypted_data.decode()


class RBACManager:
    """Role-Based Access Control for clinical users"""
    
    ROLES = {
        "patient": {
            "permissions": [
                "view_own_data",
                "update_own_profile",
                "view_treatment_options"
            ]
        },
        "practitioner": {
            "permissions": [
                "view_patient_data",
                "update_patient_data",
                "access_decision_engines",
                "view_protocols",
                "update_protocols"
            ]
        },
        "researcher": {
            "permissions": [
                "view_anonymized_data",
                "export_research_data",
                "contribute_evidence",
                "access_analytics"
            ]
        },
        "admin": {
            "permissions": [
                "manage_users",
                "manage_system",
                "view_audit_logs",
                "configure_engines"
            ]
        }
    }
    
    def has_permission(self, user_role: str, permission: str) -> bool:
        """Check if user role has specific permission"""
        if user_role not in self.ROLES:
            return False
        
        return permission in self.ROLES[user_role]["permissions"]
    
    def get_user_permissions(self, user_role: str) -> list:
        """Get all permissions for a user role"""
        if user_role not in self.ROLES:
            return []
        
        return self.ROLES[user_role]["permissions"]


# Security utility instances
password_manager = PasswordManager()
jwt_manager = JWTManager()
clinical_encryption = ClinicalDataEncryption()
rbac_manager = RBACManager()


# Authentication dependency
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    """Get current authenticated user"""
    try:
        payload = jwt_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
