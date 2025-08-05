from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..models.user import User


class AuthService:
    SECRET_KEY = "your_secret_key"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7

    def __init__(self):
        self.security = HTTPBearer()

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def register_user(self, username: str, email: str, password: str):
        hashed_password = self.hash_password(password)
        # Save user to database (pseudo-code)
        user = User(
            username=username, email=email, hashed_password=hashed_password, role="User"
        )
        # db_session.add(user)
        # db_session.commit()
        return {
            "access_token": self.create_access_token({"sub": user.email}),
            "refresh_token": self.create_refresh_token({"sub": user.email}),
        }

    def login_user(self, email: str, password: str):
        # Fetch user from database (pseudo-code)
        user = None  # Replace with actual DB query
        if user and self.verify_password(password, user.hashed_password):
            return {
                "access_token": self.create_access_token({"sub": user.email}),
                "refresh_token": self.create_refresh_token({"sub": user.email}),
            }
        raise Exception("Invalid credentials")

    def refresh_token(self, refresh_token: str):
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            email = payload.get("sub")
            if email:
                return {
                    "access_token": self.create_access_token({"sub": email}),
                    "refresh_token": self.create_refresh_token({"sub": email}),
                }
        except jwt.ExpiredSignatureError:
            raise Exception("Refresh token expired")
        except jwt.InvalidTokenError:
            raise Exception("Invalid refresh token")

    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    def get_current_user_from_token(self, token: str) -> Optional[User]:
        """Get current user from JWT token"""
        payload = self.verify_token(token)
        if payload is None:
            return None

        email = payload.get("sub")
        if email is None:
            return None

        # In a real implementation, this would query the database
        # For now, return a mock user for testing
        return User(
            id=1,
            username="test_user",
            email=email,
            hashed_password="hashed",
            role="surgeon",
            is_active=True,
        )


# Create auth service instance
auth_service = AuthService()


# FastAPI dependency functions
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(auth_service.security),
) -> User:
    """
    FastAPI dependency to get current authenticated user
    Used by research endpoints and enhanced existing endpoints
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = auth_service.get_current_user_from_token(credentials.credentials)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token - wrapper for compatibility"""
    return auth_service.verify_token(token)
