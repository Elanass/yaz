"""
OIDC Federation Schemas
Pydantic models for OIDC authentication API requests and responses
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class OIDCProviderInfo(BaseModel):
    """Basic OIDC provider information"""
    provider_id: str = Field(..., description="Unique provider identifier")
    name: str = Field(..., description="Human-readable provider name")
    issuer: str = Field(..., description="OIDC issuer URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider_id": "google",
                "name": "Google Workspace",
                "issuer": "https://accounts.google.com"
            }
        }

class OIDCLoginRequest(BaseModel):
    """Request to initiate OIDC login"""
    provider_id: str = Field(..., description="OIDC provider identifier")
    redirect_uri: str = Field(..., description="Callback URI after authentication")
    state: Optional[str] = Field(None, description="Optional state parameter")
    
    @validator('redirect_uri')
    def validate_redirect_uri(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Redirect URI must be a valid URL')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider_id": "google",
                "redirect_uri": "https://adci.health/auth/callback",
                "state": "optional_state_value"
            }
        }

class OIDCLoginResponse(BaseModel):
    """Response with OIDC authorization URL"""
    authorization_url: str = Field(..., description="URL to redirect user for authentication")
    state: str = Field(..., description="State parameter for verification")
    nonce: str = Field(..., description="Nonce for token validation")
    provider_id: str = Field(..., description="Provider identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "authorization_url": "https://accounts.google.com/oauth/authorize?client_id=...",
                "state": "abc123def456",
                "nonce": "xyz789uvw012",
                "provider_id": "google"
            }
        }

class OIDCCallbackRequest(BaseModel):
    """OIDC callback request with authorization code"""
    code: str = Field(..., description="Authorization code from provider")
    state: str = Field(..., description="State parameter for verification")
    redirect_uri: str = Field(..., description="Original redirect URI")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "4/0Adeu5BW...",
                "state": "abc123def456",
                "redirect_uri": "https://adci.health/auth/callback"
            }
        }

class OIDCUserInfo(BaseModel):
    """OIDC user information"""
    subject: str = Field(..., description="OIDC subject identifier")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="Username")
    first_name: str = Field(..., description="First name")
    last_name: str = Field(..., description="Last name")
    provider_id: str = Field(..., description="OIDC provider")
    verified: bool = Field(..., description="Whether email is verified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "subject": "1234567890",
                "email": "dr.smith@hospital.com",
                "username": "dr.smith",
                "first_name": "John",
                "last_name": "Smith",
                "provider_id": "google",
                "verified": True
            }
        }

class OIDCAuthenticationResponse(BaseModel):
    """Response from successful OIDC authentication"""
    success: bool = Field(..., description="Whether authentication was successful")
    user_id: int = Field(..., description="Authenticated user ID")
    user_info: OIDCUserInfo = Field(..., description="User information from OIDC")
    access_token: str = Field(..., description="Access token for API calls")
    refresh_token: Optional[str] = Field(None, description="Refresh token if available")
    token_type: str = Field("Bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "user_id": 12345,
                "user_info": {
                    "subject": "1234567890",
                    "email": "dr.smith@hospital.com",
                    "username": "dr.smith",
                    "first_name": "John",
                    "last_name": "Smith",
                    "provider_id": "google",
                    "verified": True
                },
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...",
                "refresh_token": "1//04...",
                "token_type": "Bearer",
                "expires_in": 3600
            }
        }

class OIDCProviderListResponse(BaseModel):
    """List of available OIDC providers"""
    providers: List[OIDCProviderInfo] = Field(..., description="Available OIDC providers")
    total_count: int = Field(..., description="Total number of providers")
    
    class Config:
        json_schema_extra = {
            "example": {
                "providers": [
                    {
                        "provider_id": "google",
                        "name": "Google Workspace",
                        "issuer": "https://accounts.google.com"
                    },
                    {
                        "provider_id": "azure",
                        "name": "Microsoft Azure AD",
                        "issuer": "https://login.microsoftonline.com/common/v2.0"
                    }
                ],
                "total_count": 2
            }
        }

# Provider Configuration Schemas (Admin only)
class OIDCProviderConfigRequest(BaseModel):
    """Request to configure OIDC provider"""
    provider_id: str = Field(..., description="Unique provider identifier")
    name: str = Field(..., description="Human-readable provider name")
    issuer: str = Field(..., description="OIDC issuer URL")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    scopes: List[str] = Field(["openid", "profile", "email"], description="OAuth scopes")
    
    # Attribute mapping
    username_claim: str = Field("preferred_username", description="Claim for username")
    email_claim: str = Field("email", description="Claim for email")
    first_name_claim: str = Field("given_name", description="Claim for first name")
    last_name_claim: str = Field("family_name", description="Claim for last name")
    
    # Security settings
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    require_https: bool = Field(True, description="Require HTTPS")
    token_validation: bool = Field(True, description="Validate ID tokens")
    auto_create_users: bool = Field(False, description="Automatically create users")
    
    @validator('issuer')
    def validate_issuer(cls, v):
        if not v.startswith('https://'):
            raise ValueError('Issuer must use HTTPS')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "provider_id": "hospital_ad",
                "name": "Hospital Active Directory",
                "issuer": "https://login.hospital.com/adfs",
                "client_id": "your_client_id",
                "client_secret": "your_client_secret",
                "scopes": ["openid", "profile", "email"],
                "username_claim": "preferred_username",
                "email_claim": "email",
                "first_name_claim": "given_name",
                "last_name_claim": "family_name",
                "verify_ssl": True,
                "require_https": True,
                "token_validation": True,
                "auto_create_users": False
            }
        }

class OIDCProviderConfigResponse(BaseModel):
    """Response from provider configuration"""
    success: bool = Field(..., description="Whether configuration was successful")
    provider_id: str = Field(..., description="Provider identifier")
    message: str = Field(..., description="Result message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "provider_id": "hospital_ad",
                "message": "OIDC provider configured successfully"
            }
        }

class OIDCUserMappingInfo(BaseModel):
    """Information about OIDC user mapping"""
    user_id: int = Field(..., description="Local user ID")
    provider_id: str = Field(..., description="OIDC provider")
    provider_subject: str = Field(..., description="Provider subject ID")
    provider_email: Optional[str] = Field(None, description="Provider email")
    provider_username: Optional[str] = Field(None, description="Provider username")
    first_login: datetime = Field(..., description="First login timestamp")
    last_login: datetime = Field(..., description="Last login timestamp")
    login_count: int = Field(..., description="Total login count")
    is_active: bool = Field(..., description="Whether mapping is active")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "user_id": 12345,
                "provider_id": "google",
                "provider_subject": "1234567890",
                "provider_email": "dr.smith@hospital.com",
                "provider_username": "dr.smith",
                "first_login": "2024-01-15T10:30:00Z",
                "last_login": "2024-01-15T14:45:00Z",
                "login_count": 25,
                "is_active": True
            }
        }

class OIDCUserMappingListResponse(BaseModel):
    """List of user's OIDC mappings"""
    mappings: List[OIDCUserMappingInfo] = Field(..., description="OIDC provider mappings")
    total_count: int = Field(..., description="Total number of mappings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mappings": [
                    {
                        "user_id": 12345,
                        "provider_id": "google",
                        "provider_subject": "1234567890",
                        "provider_email": "dr.smith@hospital.com",
                        "provider_username": "dr.smith",
                        "first_login": "2024-01-15T10:30:00Z",
                        "last_login": "2024-01-15T14:45:00Z",
                        "login_count": 25,
                        "is_active": True
                    }
                ],
                "total_count": 1
            }
        }

# Error Schemas
class OIDCErrorResponse(BaseModel):
    """OIDC error response"""
    error: str = Field(..., description="Error type")
    error_description: str = Field(..., description="Human-readable error description")
    error_uri: Optional[str] = Field(None, description="URI with error information")
    state: Optional[str] = Field(None, description="State parameter if available")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "invalid_request",
                "error_description": "The request is missing a required parameter",
                "error_uri": "https://tools.ietf.org/html/rfc6749#section-4.1.2.1",
                "state": "abc123def456"
            }
        }
