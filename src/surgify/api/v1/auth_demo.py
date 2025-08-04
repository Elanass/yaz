"""
Mock Authentication endpoints for demo purposes
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Mock secret for demo (use proper secrets in production)
SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class UserLogin(BaseModel):
    username: str
    password: str

class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    first_name: str
    last_name: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool = True
    role: str = "surgeon"

# Mock users for demo
MOCK_USERS = {
    "demo": {
        "id": 1,
        "username": "demo",
        "email": "demo@surgify.com",
        "password": "demo123",  # In production, use hashed passwords
        "first_name": "Demo",
        "last_name": "User",
        "role": "surgeon"
    },
    "admin": {
        "id": 2,
        "username": "admin",
        "email": "admin@surgify.com",
        "password": "admin123",
        "first_name": "Admin",
        "last_name": "User",
        "role": "admin"
    }
}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """
    Mock login endpoint for demo
    """
    user = MOCK_USERS.get(user_data.username)
    if not user or user["password"] != user_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=dict)
async def register(user_data: UserRegister):
    """
    Mock registration endpoint for demo
    """
    # Check if username already exists
    if user_data.username in MOCK_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # In a real application, you would hash the password and save to database
    new_user = {
        "id": len(MOCK_USERS) + 1,
        "username": user_data.username,
        "email": user_data.email,
        "password": user_data.password,  # Should be hashed in production
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": "surgeon"
    }
    
    MOCK_USERS[user_data.username] = new_user
    
    return {"message": "User registered successfully", "username": user_data.username}

@router.get("/me", response_model=User)
async def get_current_user(username: str = Depends(verify_token)):
    """
    Get current user information
    """
    user = MOCK_USERS.get(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(
        id=user["id"],
        username=user["username"],
        email=user["email"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        role=user["role"]
    )

@router.post("/logout")
async def logout():
    """
    Mock logout endpoint
    """
    return {"message": "Logged out successfully"}

@router.get("/check")
async def check_auth_status():
    """
    Check authentication status
    """
    return {
        "authenticated": False,
        "message": "No active session",
        "demo_credentials": {
            "username": "demo",
            "password": "demo123"
        }
    }
