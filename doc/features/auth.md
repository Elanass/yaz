# Authentication Feature

## Overview
The Authentication feature handles user authentication, authorization, and session management for the YAZ platform.

## Components

### AuthService (`service.py`)
Core authentication service that manages user login, registration, and session handling.

**Key Methods**:
- `authenticate_user()` - Validates user credentials
- `create_access_token()` - Generates JWT tokens
- `verify_token()` - Validates JWT tokens
- `get_current_user()` - Retrieves authenticated user

## Security Features

### Token Management
- JWT (JSON Web Tokens) for stateless authentication
- Configurable token expiration
- Secure token refresh mechanism

### Password Security
- bcrypt hashing for password storage
- Password strength validation
- Salt-based hashing for enhanced security

### Authorization
- Role-based access control (RBAC)
- Permission-based endpoint protection
- User context management

## Usage Examples

```python
from feature.auth.service import AuthService

# Initialize service
auth_service = AuthService()

# Authenticate user
user = await auth_service.authenticate_user(username, password)

# Create access token
token = auth_service.create_access_token(user.id)

# Verify token
is_valid = auth_service.verify_token(token)
```

## API Endpoints

- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/refresh` - Token refresh
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

## Configuration

```python
# Environment variables
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Testing
Tests located in `test/unit/auth/`

## Dependencies
- PyJWT (JWT handling)
- passlib[bcrypt] (password hashing)
- cryptography (encryption utilities)
