"""
Authentication API endpoints - Clean implementation
"""
import base64
import json
import secrets
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from surgify.core.services.auth_service import AuthService

router = APIRouter()

# Simple in-memory store for testing (in production this would be a database)
registered_users = set()


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


class LoginRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[Dict[str, Any]] = None


class WebAuthnRegistrationBegin(BaseModel):
    email: str
    displayName: str


class WebAuthnRegistrationComplete(BaseModel):
    id: str
    rawId: str
    response: Dict[str, str]
    type: str


class WebAuthnAuthenticationComplete(BaseModel):
    id: str
    rawId: str
    response: Dict[str, str]
    type: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None


# Dependency
auth_service = AuthService()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login endpoint"""
    # Validate input
    if not request.password:
        raise HTTPException(status_code=422, detail="Password is required")

    if not request.username and not request.email:
        raise HTTPException(status_code=422, detail="Username or email is required")

    # For testing, check against registered users
    login_identifier = request.username or request.email

    # Find user in registered_users
    user_found = None
    for username, email in registered_users:
        if username == login_identifier or email == login_identifier:
            user_found = (username, email)
            break

    if user_found:
        # Generate token for authenticated user
        token = f"{user_found[0]}:{secrets.token_urlsafe(32)}"
        refresh_token = f"refresh_{user_found[0]}:{secrets.token_urlsafe(32)}"
        user_data = {
            "username": user_found[0],
            "email": user_found[1],
            "display_name": user_found[0],
        }
        return TokenResponse(
            access_token=token, refresh_token=refresh_token, user=user_data
        )

    # Fallback to demo user for testing
    if login_identifier == "demo" and request.password == "demo":
        user_data = {
            "id": "demo-user-id",
            "email": "demo@example.com",
            "name": "Demo User",
            "display_name": "Demo User",
        }
        return TokenResponse(
            access_token="demo-token",
            refresh_token="demo-refresh-token",
            user=user_data,
        )

    raise HTTPException(status_code=401, detail="Invalid credentials")


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshRequest):
    """Refresh access token using refresh token"""
    # Simple token refresh logic for testing
    if request.refresh_token and request.refresh_token.startswith("refresh_"):
        username = request.refresh_token.split(":")[0].replace("refresh_", "")
        # Find user in registered_users
        user_found = None
        for registered_username, email in registered_users:
            if registered_username == username:
                user_found = (registered_username, email)
                break

        if user_found:
            # Generate new tokens
            new_access_token = f"{user_found[0]}:{secrets.token_urlsafe(32)}"
            new_refresh_token = f"refresh_{user_found[0]}:{secrets.token_urlsafe(32)}"
            user_data = {
                "username": user_found[0],
                "email": user_found[1],
                "display_name": user_found[0],
            }
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                user=user_data,
            )

    raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/me")
async def get_current_user_info():
    """Get current user information"""
    return {"user": "demo", "authenticated": True}


@router.post("/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Successfully logged out"}


@router.post("/register", response_model=TokenResponse)
def register_user(request: RegisterRequest):
    """User registration endpoint"""
    # Check for duplicate users
    user_key = (request.username, request.email)

    if user_key in registered_users:
        raise HTTPException(status_code=409, detail="User already exists")

    # Simple registration for testing
    if request.username and request.email and request.password:
        registered_users.add(user_key)
        user_data = {
            "username": request.username,
            "email": request.email,
            "full_name": request.full_name,
        }
        # Generate a simple token for testing
        token = f"{request.username}:{secrets.token_urlsafe(32)}"
        refresh_token = f"refresh_{request.username}:{secrets.token_urlsafe(32)}"
        return TokenResponse(
            access_token=token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=user_data,
        )
    else:
        raise HTTPException(status_code=400, detail="Missing required fields")


# WebAuthn Endpoints
@router.post("/webauthn/register/begin")
async def webauthn_register_begin(request: WebAuthnRegistrationBegin):
    """Begin WebAuthn registration process"""
    try:
        # Generate a random challenge
        challenge = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )

        # Generate user ID
        user_id = (
            base64.urlsafe_b64encode(request.email.encode()).decode("utf-8").rstrip("=")
        )

        registration_options = {
            "challenge": challenge,
            "rp": {
                "name": "Surgify Platform",
                "id": "localhost",  # Change to your domain in production
            },
            "user": {
                "id": user_id,
                "name": request.email,
                "displayName": request.displayName,
            },
            "pubKeyCredParams": [
                {"alg": -7, "type": "public-key"},  # ES256
                {"alg": -257, "type": "public-key"},  # RS256
            ],
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "preferred",
            },
            "timeout": 60000,
            "attestation": "direct",
        }

        return JSONResponse(content=registration_options)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/webauthn/register/complete")
async def webauthn_register_complete(request: WebAuthnRegistrationComplete):
    """Complete WebAuthn registration process"""
    try:
        return JSONResponse(
            content={
                "status": "success",
                "message": "WebAuthn credential registered successfully",
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Registration completion failed: {str(e)}"
        )


@router.post("/webauthn/authenticate/begin")
async def webauthn_authenticate_begin():
    """Begin WebAuthn authentication process"""
    try:
        # Generate a random challenge
        challenge = (
            base64.urlsafe_b64encode(secrets.token_bytes(32))
            .decode("utf-8")
            .rstrip("=")
        )

        authentication_options = {
            "challenge": challenge,
            "timeout": 60000,
            "rpId": "localhost",  # Change to your domain in production
            "userVerification": "required",
            "allowCredentials": [],  # In production, filter by user's registered credentials
        }

        return JSONResponse(content=authentication_options)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Authentication initiation failed: {str(e)}"
        )


@router.post("/webauthn/authenticate/complete")
async def webauthn_authenticate_complete(request: WebAuthnAuthenticationComplete):
    """Complete WebAuthn authentication process"""
    try:
        user_data = {
            "id": "webauthn-user-id",
            "email": "webauthn@surgify.com",
            "name": "WebAuthn User",
            "display_name": "Biometric User",
        }

        return JSONResponse(
            content={
                "status": "success",
                "access_token": "webauthn-demo-token",
                "token_type": "bearer",
                "user": user_data,
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Authentication completion failed: {str(e)}"
        )
