"""
Test Suite for Authentication Feature
Comprehensive tests for auth functionality
"""

import pytest
from fastapi.testclient import TestClient

from main import create_app
from features.auth.service import UserCreate, UserLogin, UserRole


@pytest.fixture
def client():
    """Test client fixture"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def test_user_data():
    """Test user data fixture"""
    return UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User",
        role=UserRole.CLINICIAN,
        organization="Test Hospital"
    )


class TestAuthAPI:
    """Test authentication API endpoints"""
    
    def test_register_user(self, client, test_user_data):
        """Test user registration"""
        
        response = client.post("/api/v1/auth/register", json=test_user_data.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user_data.email
        assert data["data"]["full_name"] == test_user_data.full_name
        assert data["data"]["role"] == test_user_data.role.value
    
    def test_register_duplicate_user(self, client, test_user_data):
        """Test duplicate user registration fails"""
        
        # Register first user
        client.post("/api/v1/auth/register", json=test_user_data.dict())
        
        # Try to register same user again
        response = client.post("/api/v1/auth/register", json=test_user_data.dict())
        
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]
    
    def test_login_user(self, client, test_user_data):
        """Test user login"""
        
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data.dict())
        
        # Login
        login_data = UserLogin(email=test_user_data.email, password=test_user_data.password)
        response = client.post("/api/v1/auth/login", json=login_data.dict())
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert data["data"]["user"]["email"] == test_user_data.email
    
    def test_login_invalid_credentials(self, client, test_user_data):
        """Test login with invalid credentials"""
        
        # Register user first
        client.post("/api/v1/auth/register", json=test_user_data.dict())
        
        # Try login with wrong password
        login_data = UserLogin(email=test_user_data.email, password="wrongpassword")
        response = client.post("/api/v1/auth/login", json=login_data.dict())
        
        assert response.status_code == 401
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_get_current_user(self, client, test_user_data):
        """Test getting current user info"""
        
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data.dict())
        login_data = UserLogin(email=test_user_data.email, password=test_user_data.password)
        login_response = client.post("/api/v1/auth/login", json=login_data.dict())
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get user info
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["email"] == test_user_data.email
    
    def test_get_user_permissions(self, client, test_user_data):
        """Test getting user permissions"""
        
        # Register and login
        client.post("/api/v1/auth/register", json=test_user_data.dict())
        login_data = UserLogin(email=test_user_data.email, password=test_user_data.password)
        login_response = client.post("/api/v1/auth/login", json=login_data.dict())
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get permissions
        response = client.get("/api/v1/auth/permissions", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0  # Clinician should have some permissions
    
    def test_unauthorized_access(self, client):
        """Test accessing protected endpoint without token"""
        
        response = client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # No Authorization header
    
    def test_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token"""
        
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]


class TestUserModel:
    """Test User model functionality"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        
        from features.auth.service import User, UserRole
        
        user = User(
            email="test@example.com",
            password_hash="",
            full_name="Test User",
            role=UserRole.CLINICIAN
        )
        
        password = "testpassword123"
        user.set_password(password)
        
        # Password should be hashed
        assert user.password_hash != password
        assert len(user.password_hash) > 20  # Bcrypt hash is long
        
        # Should verify correctly
        assert user.check_password(password) is True
        assert user.check_password("wrongpassword") is False
    
    def test_user_permissions(self):
        """Test user permission system"""
        
        from features.auth.service import User, UserRole, Domain, Scope
        
        # Test clinician permissions
        clinician = User(
            email="clinician@example.com",
            password_hash="hash",
            full_name="Dr. Clinician", 
            role=UserRole.CLINICIAN
        )
        
        permissions = clinician.get_permissions()
        permission_strings = [str(p) for p in permissions]
        
        assert "healthcare:read" in permission_strings
        assert "healthcare:write" in permission_strings
        assert "logistics:read" in permission_strings
        
        # Test admin permissions
        admin = User(
            email="admin@example.com",
            password_hash="hash",
            full_name="Admin User",
            role=UserRole.ADMIN
        )
        
        admin_permissions = admin.get_permissions()
        admin_permission_strings = [str(p) for p in admin_permissions]
        
        # Admin should have all permissions
        assert len(admin_permission_strings) > len(permission_strings)
        assert "admin:admin" in admin_permission_strings
    
    def test_account_locking(self):
        """Test account locking mechanism"""
        
        from features.auth.service import User, UserRole
        from datetime import datetime, timedelta
        
        user = User(
            email="test@example.com",
            password_hash="hash",
            full_name="Test User",
            role=UserRole.CLINICIAN
        )
        
        # Initially not locked
        assert user.is_locked() is False
        
        # Lock until future time
        user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        assert user.is_locked() is True
        
        # Lock until past time
        user.locked_until = datetime.utcnow() - timedelta(minutes=30)
        assert user.is_locked() is False


@pytest.mark.asyncio
class TestAuthService:
    """Test AuthService functionality"""
    
    async def test_create_user(self):
        """Test user creation"""
        
        from features.auth.service import AuthService, UserCreate, UserRole
        
        auth_service = AuthService()
        
        user_data = UserCreate(
            email="newuser@example.com",
            password="password123",
            full_name="New User",
            role=UserRole.CLINICIAN
        )
        
        user = await auth_service.create_user(user_data)
        
        assert user.email == user_data.email
        assert user.full_name == user_data.full_name
        assert user.role == user_data.role
        assert user.check_password(user_data.password) is True
    
    async def test_authenticate_user(self):
        """Test user authentication"""
        
        from features.auth.service import AuthService, UserCreate, UserRole
        
        auth_service = AuthService()
        
        # Create user
        user_data = UserCreate(
            email="auth@example.com",
            password="password123",
            full_name="Auth User",
            role=UserRole.CLINICIAN
        )
        
        await auth_service.create_user(user_data)
        
        # Test successful authentication
        user = await auth_service.authenticate_user(user_data.email, user_data.password)
        assert user is not None
        assert user.email == user_data.email
        
        # Test failed authentication
        user = await auth_service.authenticate_user(user_data.email, "wrongpassword")
        assert user is None
    
    async def test_jwt_token_creation_and_verification(self):
        """Test JWT token operations"""
        
        from features.auth.service import AuthService, UserCreate, UserRole
        
        auth_service = AuthService()
        
        # Create user
        user_data = UserCreate(
            email="jwt@example.com",
            password="password123",
            full_name="JWT User",
            role=UserRole.CLINICIAN
        )
        
        user = await auth_service.create_user(user_data)
        
        # Create token
        token = auth_service.create_access_token(user)
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are long
        
        # Verify token
        payload = auth_service.verify_token(token)
        assert payload["sub"] == str(user.id)
        assert payload["email"] == user.email
        assert payload["role"] == user.role.value
