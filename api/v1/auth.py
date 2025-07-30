"""
Authentication API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.dependencies import get_current_user, require_role

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """User login endpoint"""
    # Simplified login for MVP
    if request.username == "demo" and request.password == "demo":
        return TokenResponse(access_token="demo-token")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@router.get("/me")
async def get_current_user_info(current_user=Depends(get_current_user)):
    """Get current user information"""
    return current_user


@router.post("/logout")
async def logout(current_user=Depends(get_current_user)):
    """User logout endpoint"""
    return {"message": "Successfully logged out"}
