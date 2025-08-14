"""Shared Authentication Service
Common authentication functionality for all apps.
"""

from datetime import datetime, timedelta
from typing import Any

import bcrypt
import jwt

from src.shared.core.config import get_shared_config
from src.shared.core.exceptions import PermissionError
from src.shared.core.logger import get_logger
from src.shared.models import UserRole


class AuthService:
    """Shared authentication service."""

    def __init__(self, app_name: str = "yaz") -> None:
        self.app_name = app_name
        self.config = get_shared_config()
        self.logger = get_logger(f"{app_name}.auth")

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash."""
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception as e:
            self.logger.exception(f"Password verification error: {e}")
            return False

    def create_access_token(
        self, user_id: str, role: str, expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT access token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)

        payload = {
            "sub": user_id,
            "role": role,
            "app": self.app_name,
            "exp": expire,
            "iat": datetime.utcnow(),
        }

        return jwt.encode(payload, self.config.secret_key, algorithm="HS256")

    def verify_token(self, token: str) -> dict[str, Any] | None:
        """Verify and decode JWT token."""
        try:
            return jwt.decode(token, self.config.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {e}")
            return None

    def check_permission(self, user_role: str, required_role: str) -> bool:
        """Check if user has required permission."""
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.PATIENT: 1,
            UserRole.TECHNICIAN: 2,
            UserRole.NURSE: 3,
            UserRole.DOCTOR: 4,
            UserRole.ADMIN: 5,
        }

        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)

        return user_level >= required_level

    def require_permission(
        self, user_role: str, required_role: str, action: str = "access resource"
    ) -> None:
        """Require specific permission or raise exception."""
        if not self.check_permission(user_role, required_role):
            raise PermissionError(action, f"requires {required_role} role")

    def create_api_key(self, user_id: str, name: str) -> str:
        """Create API key for user."""
        payload = {
            "type": "api_key",
            "user_id": user_id,
            "name": name,
            "app": self.app_name,
            "created": datetime.utcnow().isoformat(),
        }

        return jwt.encode(payload, self.config.secret_key, algorithm="HS256")

    def verify_api_key(self, api_key: str) -> dict[str, Any] | None:
        """Verify API key."""
        try:
            payload = jwt.decode(api_key, self.config.secret_key, algorithms=["HS256"])
            if payload.get("type") != "api_key":
                return None
            return payload
        except jwt.InvalidTokenError:
            return None
