"""
Clean Authentication Routes for API
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import secrets
import base64
from typing import Optional, Dict, Any

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
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

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login endpoint"""
    if request.username == "demo" and request.password == "demo":
        user_data = {
            "id": "demo-user-id",
            "email": request.username,
            "name": "Demo User",
            "display_name": "Demo User"
        }
        return TokenResponse(
            access_token="demo-token",
            user=user_data
        )
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/me")
async def get_current_user_info():
    """Get current user information"""
    return {"user": "demo", "authenticated": True}

@router.post("/logout")
async def logout():
    """User logout endpoint"""
    return {"message": "Successfully logged out"}

# WebAuthn Endpoints
@router.post("/webauthn/register/begin")
async def webauthn_register_begin(request: WebAuthnRegistrationBegin):
    """Begin WebAuthn registration process"""
    try:
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        user_id = base64.urlsafe_b64encode(request.email.encode()).decode('utf-8').rstrip('=')
        
        registration_options = {
            "challenge": challenge,
            "rp": {
                "name": "Surgify Platform",
                "id": "localhost"
            },
            "user": {
                "id": user_id,
                "name": request.email,
                "displayName": request.displayName
            },
            "pubKeyCredParams": [
                {"alg": -7, "type": "public-key"},
                {"alg": -257, "type": "public-key"}
            ],
            "authenticatorSelection": {
                "authenticatorAttachment": "platform",
                "userVerification": "required",
                "residentKey": "preferred"
            },
            "timeout": 60000,
            "attestation": "direct"
        }
        
        return JSONResponse(content=registration_options)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/webauthn/register/complete")
async def webauthn_register_complete(request: WebAuthnRegistrationComplete):
    """Complete WebAuthn registration process"""
    try:
        return JSONResponse(content={
            "status": "success",
            "message": "WebAuthn credential registered successfully"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration completion failed: {str(e)}")

@router.post("/webauthn/authenticate/begin")
async def webauthn_authenticate_begin():
    """Begin WebAuthn authentication process"""
    try:
        challenge = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
        
        authentication_options = {
            "challenge": challenge,
            "timeout": 60000,
            "rpId": "localhost",
            "userVerification": "required",
            "allowCredentials": []
        }
        
        return JSONResponse(content=authentication_options)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication initiation failed: {str(e)}")

@router.post("/webauthn/authenticate/complete")
async def webauthn_authenticate_complete(request: WebAuthnAuthenticationComplete):
    """Complete WebAuthn authentication process"""
    try:
        user_data = {
            "id": "webauthn-user-id",
            "email": "webauthn@surgify.com",
            "name": "WebAuthn User",
            "display_name": "Biometric User"
        }
        
        return JSONResponse(content={
            "status": "success",
            "access_token": "webauthn-demo-token",
            "token_type": "bearer",
            "user": user_data
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication completion failed: {str(e)}")
