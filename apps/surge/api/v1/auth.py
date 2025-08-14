"""Enhanced Authentication API - JWT + WebAuthn + OAuth2
Modern PWA authentication with security best practices.
"""

import base64
import secrets
from datetime import datetime, timedelta
from typing import Any

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response, Security
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

# Import AuthService
from src.surge.core.services.auth_service import AuthService


# Enhanced security scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
security = HTTPBearer(auto_error=False)

router = APIRouter(prefix="/auth", tags=["authentication"])

# Security configuration
SECRET_KEY = "surgify-jwt-secret-key-change-in-production"  # Use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Enhanced user storage (replace with database in production)
users_db = {}
active_sessions = {}
webauthn_challenges = {}


class User(BaseModel):
    """Enhanced user model."""

    id: str
    username: str
    email: EmailStr
    full_name: str | None = None
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = datetime.now()
    last_login: datetime | None = None


class UserInDB(User):
    """User model with hashed password."""

    hashed_password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: dict[str, Any] | None = None


class RefreshRequest(BaseModel):
    refresh_token: str


class WebAuthnRegistrationRequest(BaseModel):
    email: EmailStr
    display_name: str


class WebAuthnAuthRequest(BaseModel):
    email: EmailStr


# Utility functions
def hash_password(password: str) -> str:
    """Hash password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return payload
    except JWTError:
        return None


def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user."""
    if not token:
        return None

    payload = verify_token(token.credentials)
    if not payload:
        return None

    user_id = payload.get("sub")
    if user_id in users_db:
        return users_db[user_id]
    return None


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """Create JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    """Verify and decode JWT token."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> User:
    """Dependency to get current user from JWT token."""
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(status_code=401, detail="Invalid token")

        # Get user from store
        if user_id in registered_users:
            user_data = registered_users[user_id]
            return User(**user_data)
        raise HTTPException(status_code=401, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Dependency
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login endpoint with JWT."""
    # Validate input
    if not request.password:
        raise HTTPException(status_code=422, detail="Password is required")

    if not request.username and not request.email:
        raise HTTPException(status_code=422, detail="Username or email is required")

    # Find user
    login_identifier = request.username or request.email
    user_found = None

    for user_data in registered_users.values():
        if (
            user_data["username"] == login_identifier
            or user_data["email"] == login_identifier
        ):
            user_found = user_data
            break

    if user_found and verify_password(request.password, user_found["hashed_password"]):
        # Create tokens
        access_token = create_access_token({"sub": user_found["id"]})
        refresh_token = create_refresh_token({"sub": user_found["id"]})

        # Track session
        session_id = f"session_{user_found['id']}_{datetime.now().timestamp()}"
        active_sessions[session_id] = {
            "user_id": user_found["id"],
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
        }

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user={
                "id": user_found["id"],
                "username": user_found["username"],
                "email": user_found["email"],
                "full_name": user_found.get("full_name"),
                "display_name": user_found.get("full_name") or user_found["username"],
            },
        )

    # Demo user fallback
    if login_identifier == "demo" and request.password == "demo":
        demo_user_id = "demo-user-id"
        access_token = create_access_token({"sub": demo_user_id})
        refresh_token = create_refresh_token({"sub": demo_user_id})

        user_data = {
            "id": demo_user_id,
            "email": "demo@surgify.com",
            "username": "demo",
            "full_name": "Demo User",
            "display_name": "Demo User",
        }

        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, user=user_data
        )

    raise HTTPException(status_code=401, detail="Invalid credentials")


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token."""
    try:
        payload = verify_token(request.refresh_token)
        user_id = payload.get("sub")
        token_type = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Find user
        if user_id in registered_users:
            user_data = registered_users[user_id]

            # Create new tokens
            new_access_token = create_access_token({"sub": user_id})
            new_refresh_token = create_refresh_token({"sub": user_id})

            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                user={
                    "id": user_data["id"],
                    "username": user_data["username"],
                    "email": user_data["email"],
                    "full_name": user_data.get("full_name"),
                    "display_name": user_data.get("full_name") or user_data["username"],
                },
            )
        raise HTTPException(status_code=401, detail="User not found")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, response: Response):
    """Enhanced user registration with security checks."""
    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(
            status_code=422, detail="Password must be at least 8 characters"
        )

    # Check if user exists
    for user_data in users_db.values():
        if user_data.username == request.username or user_data.email == request.email:
            raise HTTPException(status_code=409, detail="User already exists")

    # Create user
    user_id = f"user_{secrets.token_urlsafe(16)}"
    hashed_password = hash_password(request.password)

    user = UserInDB(
        id=user_id,
        username=request.username,
        email=request.email,
        full_name=request.full_name,
        hashed_password=hashed_password,
        created_at=datetime.now(),
    )

    users_db[user_id] = user

    # Create tokens
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})

    # Set secure HTTP-only cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        },
    )


@router.post("/login/enhanced", response_model=TokenResponse)
async def enhanced_login(request: LoginRequest, response: Response):
    """Enhanced login with security features."""
    # Find user
    user = None
    for u in users_db.values():
        if (request.username and u.username == request.username) or (
            request.email and u.email == request.email
        ):
            user = u
            break

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account disabled")

    # Update last login
    user.last_login = datetime.now()

    # Create tokens with extended expiry if remember_me
    expires_delta = timedelta(days=30) if request.remember_me else None
    access_token = create_access_token({"sub": user.id}, expires_delta)
    refresh_token = create_refresh_token({"sub": user.id})

    # Store session
    session_id = f"session_{user.id}_{secrets.token_urlsafe(16)}"
    active_sessions[session_id] = {
        "user_id": user.id,
        "created_at": datetime.now(),
        "expires_at": datetime.now()
        + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)),
    }

    # Set secure cookie for refresh token
    if request.remember_me:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=30 * 24 * 60 * 60,  # 30 days
        )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user={
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        },
    )


@router.post("/webauthn/registration/begin")
async def webauthn_registration_begin(request: WebAuthnRegistrationRequest):
    """Begin WebAuthn registration process."""
    # Generate challenge
    challenge = secrets.token_urlsafe(32)
    webauthn_challenges[request.email] = {
        "challenge": challenge,
        "created_at": datetime.now(),
        "type": "registration",
    }

    # WebAuthn registration options
    return {
        "challenge": challenge,
        "rp": {"name": "Surgify", "id": "localhost"},  # Change to your domain
        "user": {
            "id": base64.urlsafe_b64encode(request.email.encode()).decode(),
            "name": request.email,
            "displayName": request.display_name,
        },
        "pubKeyCredParams": [
            {"type": "public-key", "alg": -7},  # ES256
            {"type": "public-key", "alg": -257},  # RS256
        ],
        "authenticatorSelection": {
            "authenticatorAttachment": "platform",
            "userVerification": "required",
        },
        "timeout": 60000,
        "attestation": "direct",
    }


@router.post("/webauthn/authentication/begin")
async def webauthn_authentication_begin(request: WebAuthnAuthRequest):
    """Begin WebAuthn authentication process."""
    # Generate challenge
    challenge = secrets.token_urlsafe(32)
    webauthn_challenges[request.email] = {
        "challenge": challenge,
        "created_at": datetime.now(),
        "type": "authentication",
    }

    return {
        "challenge": challenge,
        "timeout": 60000,
        "userVerification": "required",
        "allowCredentials": [],  # Would contain registered credentials
    }


@router.post("/logout")
async def logout(
    response: Response, current_user: User | None = Depends(get_current_user)
):
    """Enhanced logout with session cleanup."""
    if current_user:
        # Remove user sessions
        sessions_to_remove = []
        for session_id, session_data in active_sessions.items():
            if session_data["user_id"] == current_user.id:
                sessions_to_remove.append(session_id)

        for session_id in sessions_to_remove:
            del active_sessions[session_id]

    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "last_login": current_user.last_login,
    }


@router.post("/verify-token")
async def verify_user_token(token: str):
    """Verify if a token is valid."""
    try:
        payload = verify_token(token)
        return {"valid": True, "payload": payload}
    except:
        return {"valid": False}
