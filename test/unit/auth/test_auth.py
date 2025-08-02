"""
Unit tests for Authentication feature
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import jwt

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

from feature.auth.service import AuthService
from core.models.users import User


class TestAuthService:
    """Test cases for AuthService"""
    
    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing"""
        return AuthService()
    
    @pytest.fixture
    def sample_user(self):
        """Sample user for testing"""
        return User(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="$2b$12$hashedpassword",
            is_active=True,
            roles=["user"]
        )
    
    @pytest.mark.asyncio
    async def test_authenticate_user_valid_credentials(self, auth_service, sample_user):
        """Test user authentication with valid credentials"""
        with patch('feature.auth.service.verify_password') as mock_verify:
            with patch('feature.auth.service.get_user_by_username') as mock_get_user:
                mock_verify.return_value = True
                mock_get_user.return_value = sample_user
                
                result = await auth_service.authenticate_user("testuser", "password123")
                
                assert result is not None
                assert result.username == "testuser"
                assert result.email == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_credentials(self, auth_service):
        """Test user authentication with invalid credentials"""
        with patch('feature.auth.service.verify_password') as mock_verify:
            with patch('feature.auth.service.get_user_by_username') as mock_get_user:
                mock_verify.return_value = False
                mock_get_user.return_value = None
                
                result = await auth_service.authenticate_user("invalid", "wrong")
                
                assert result is None
    
    def test_create_access_token_valid_user(self, auth_service, sample_user):
        """Test JWT token creation for valid user"""
        token = auth_service.create_access_token(sample_user.id)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token can be decoded
        with patch('feature.auth.service.JWT_SECRET_KEY', 'test-secret'):
            decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
            assert decoded['user_id'] == sample_user.id
            assert 'exp' in decoded
    
    def test_create_access_token_custom_expiry(self, auth_service, sample_user):
        """Test JWT token creation with custom expiration"""
        expires_delta = timedelta(hours=2)
        token = auth_service.create_access_token(
            sample_user.id, 
            expires_delta=expires_delta
        )
        
        assert token is not None
        
        with patch('feature.auth.service.JWT_SECRET_KEY', 'test-secret'):
            decoded = jwt.decode(token, 'test-secret', algorithms=['HS256'])
            exp_time = datetime.fromtimestamp(decoded['exp'])
            expected_time = datetime.utcnow() + expires_delta
            
            # Allow for small time differences in testing
            assert abs((exp_time - expected_time).total_seconds()) < 10
    
    def test_verify_token_valid(self, auth_service):
        """Test token verification with valid token"""
        test_payload = {'user_id': 1, 'exp': datetime.utcnow() + timedelta(hours=1)}
        
        with patch('feature.auth.service.JWT_SECRET_KEY', 'test-secret'):
            token = jwt.encode(test_payload, 'test-secret', algorithm='HS256')
            
            result = auth_service.verify_token(token)
            
            assert result is not None
            assert result['user_id'] == 1
    
    def test_verify_token_expired(self, auth_service):
        """Test token verification with expired token"""
        test_payload = {'user_id': 1, 'exp': datetime.utcnow() - timedelta(hours=1)}
        
        with patch('feature.auth.service.JWT_SECRET_KEY', 'test-secret'):
            token = jwt.encode(test_payload, 'test-secret', algorithm='HS256')
            
            result = auth_service.verify_token(token)
            
            assert result is None
    
    def test_verify_token_invalid_signature(self, auth_service):
        """Test token verification with invalid signature"""
        test_payload = {'user_id': 1, 'exp': datetime.utcnow() + timedelta(hours=1)}
        
        # Create token with different secret
        token = jwt.encode(test_payload, 'wrong-secret', algorithm='HS256')
        
        with patch('feature.auth.service.JWT_SECRET_KEY', 'test-secret'):
            result = auth_service.verify_token(token)
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self, auth_service, sample_user):
        """Test getting current user with valid token"""
        test_payload = {'user_id': sample_user.id}
        
        with patch('feature.auth.service.verify_token') as mock_verify:
            with patch('feature.auth.service.get_user_by_id') as mock_get_user:
                mock_verify.return_value = test_payload
                mock_get_user.return_value = sample_user
                
                result = await auth_service.get_current_user("valid_token")
                
                assert result is not None
                assert result.id == sample_user.id
                assert result.username == sample_user.username
    
    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, auth_service):
        """Test getting current user with invalid token"""
        with patch('feature.auth.service.verify_token') as mock_verify:
            mock_verify.return_value = None
            
            result = await auth_service.get_current_user("invalid_token")
            
            assert result is None
    
    @pytest.mark.asyncio
    async def test_register_user_new_user(self, auth_service):
        """Test user registration with new user"""
        user_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'securepassword123'
        }
        
        with patch('feature.auth.service.get_user_by_username') as mock_get_by_username:
            with patch('feature.auth.service.get_user_by_email') as mock_get_by_email:
                with patch('feature.auth.service.create_user') as mock_create:
                    with patch('feature.auth.service.hash_password') as mock_hash:
                        mock_get_by_username.return_value = None
                        mock_get_by_email.return_value = None
                        mock_hash.return_value = "hashed_password"
                        mock_create.return_value = User(
                            id=2,
                            username="newuser",
                            email="new@example.com",
                            hashed_password="hashed_password"
                        )
                        
                        result = await auth_service.register_user(user_data)
                        
                        assert result is not None
                        assert result.username == "newuser"
                        assert result.email == "new@example.com"
    
    @pytest.mark.asyncio
    async def test_register_user_existing_username(self, auth_service, sample_user):
        """Test user registration with existing username"""
        user_data = {
            'username': 'testuser',  # Same as sample_user
            'email': 'different@example.com',
            'password': 'password123'
        }
        
        with patch('feature.auth.service.get_user_by_username') as mock_get_user:
            mock_get_user.return_value = sample_user
            
            with pytest.raises(ValueError, match="Username already exists"):
                await auth_service.register_user(user_data)
    
    @pytest.mark.asyncio
    async def test_register_user_existing_email(self, auth_service, sample_user):
        """Test user registration with existing email"""
        user_data = {
            'username': 'differentuser',
            'email': 'test@example.com',  # Same as sample_user
            'password': 'password123'
        }
        
        with patch('feature.auth.service.get_user_by_username') as mock_get_by_username:
            with patch('feature.auth.service.get_user_by_email') as mock_get_by_email:
                mock_get_by_username.return_value = None
                mock_get_by_email.return_value = sample_user
                
                with pytest.raises(ValueError, match="Email already exists"):
                    await auth_service.register_user(user_data)
    
    def test_validate_password_strength_valid(self, auth_service):
        """Test password strength validation with valid password"""
        valid_passwords = [
            "SecurePass123!",
            "MyStr0ngP@ssw0rd",
            "C0mpl3x!P@ssw0rd"
        ]
        
        for password in valid_passwords:
            is_valid = auth_service.validate_password_strength(password)
            assert is_valid is True
    
    def test_validate_password_strength_invalid(self, auth_service):
        """Test password strength validation with invalid passwords"""
        invalid_passwords = [
            "weak",           # Too short
            "password",       # No numbers/special chars
            "PASSWORD123",    # No lowercase
            "password123",    # No uppercase
            "Password",       # No numbers/special chars
        ]
        
        for password in invalid_passwords:
            is_valid = auth_service.validate_password_strength(password)
            assert is_valid is False
    
    @pytest.mark.asyncio
    async def test_refresh_token_valid(self, auth_service, sample_user):
        """Test token refresh with valid refresh token"""
        refresh_token_payload = {
            'user_id': sample_user.id,
            'type': 'refresh',
            'exp': datetime.utcnow() + timedelta(days=30)
        }
        
        with patch('feature.auth.service.verify_token') as mock_verify:
            with patch('feature.auth.service.get_user_by_id') as mock_get_user:
                mock_verify.return_value = refresh_token_payload
                mock_get_user.return_value = sample_user
                
                result = await auth_service.refresh_token("valid_refresh_token")
                
                assert result is not None
                assert 'access_token' in result
                assert 'token_type' in result
    
    @pytest.mark.asyncio
    async def test_check_user_permissions(self, auth_service, sample_user):
        """Test user permission checking"""
        # Test user with admin role
        admin_user = User(
            id=2,
            username="admin",
            email="admin@example.com",
            roles=["admin", "user"]
        )
        
        # Test regular user permissions
        has_user_perm = auth_service.check_user_permissions(sample_user, "user")
        assert has_user_perm is True
        
        has_admin_perm = auth_service.check_user_permissions(sample_user, "admin")
        assert has_admin_perm is False
        
        # Test admin user permissions
        has_admin_perm = auth_service.check_user_permissions(admin_user, "admin")
        assert has_admin_perm is True


if __name__ == '__main__':
    pytest.main([__file__])
