"""
WebAuthn Authentication Schemas
Pydantic models for WebAuthn/FIDO2 API requests and responses
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class AuthenticatorType(str, Enum):
    """Types of authenticators"""
    PLATFORM = "platform"
    CROSS_PLATFORM = "cross-platform"
    HYBRID = "hybrid"

class CredentialStatus(str, Enum):
    """WebAuthn credential status"""
    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"
    COMPROMISED = "compromised"

class UserVerificationRequirement(str, Enum):
    """User verification requirements"""
    REQUIRED = "required"
    PREFERRED = "preferred"
    DISCOURAGED = "discouraged"

# Registration Schemas
class WebAuthnRegistrationBeginRequest(BaseModel):
    """Request to begin WebAuthn registration"""
    authenticator_type: AuthenticatorType = AuthenticatorType.PLATFORM
    user_verification: UserVerificationRequirement = UserVerificationRequirement.REQUIRED
    
    class Config:
        json_schema_extra = {
            "example": {
                "authenticator_type": "platform",
                "user_verification": "required"
            }
        }

class WebAuthnRegistrationBeginResponse(BaseModel):
    """Response from beginning WebAuthn registration"""
    options: Dict[str, Any] = Field(..., description="WebAuthn registration options")
    challenge_key: str = Field(..., description="Challenge key for completing registration")
    expires_at: str = Field(..., description="Challenge expiration time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "options": {
                    "rp": {"id": "example.com", "name": "ADCI Platform"},
                    "user": {"id": "MTIzNDU=", "name": "dr.smith", "displayName": "Dr. Smith"},
                    "challenge": "Y2hhbGxlbmdl",
                    "pubKeyCredParams": [{"alg": -7, "type": "public-key"}],
                    "timeout": 300000,
                    "attestation": "direct"
                },
                "challenge_key": "reg_12345_abc123",
                "expires_at": "2024-01-15T10:35:00Z"
            }
        }

class WebAuthnRegistrationCompleteRequest(BaseModel):
    """Request to complete WebAuthn registration"""
    challenge_key: str = Field(..., description="Challenge key from begin request")
    credential_response: Dict[str, Any] = Field(..., description="WebAuthn credential response")
    credential_name: Optional[str] = Field(None, description="Human-readable name for the credential")
    
    class Config:
        json_schema_extra = {
            "example": {
                "challenge_key": "reg_12345_abc123",
                "credential_response": {
                    "id": "credential_id_base64",
                    "rawId": "credential_id_base64",
                    "response": {
                        "attestationObject": "attestation_object_base64",
                        "clientDataJSON": "client_data_json_base64"
                    },
                    "type": "public-key"
                },
                "credential_name": "iPhone FaceID"
            }
        }

class WebAuthnRegistrationCompleteResponse(BaseModel):
    """Response from completing WebAuthn registration"""
    success: bool = Field(..., description="Whether registration was successful")
    credential_id: str = Field(..., description="The registered credential ID")
    credential_name: str = Field(..., description="Human-readable credential name")
    created_at: str = Field(..., description="When the credential was created")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "credential_id": "Y3JlZGVudGlhbF9pZA==",
                "credential_name": "iPhone FaceID",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

# Authentication Schemas
class WebAuthnAuthenticationBeginRequest(BaseModel):
    """Request to begin WebAuthn authentication"""
    username: Optional[str] = Field(None, description="Username for credential filtering")
    user_verification: UserVerificationRequirement = UserVerificationRequirement.REQUIRED
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "dr.smith",
                "user_verification": "required"
            }
        }

class WebAuthnAuthenticationBeginResponse(BaseModel):
    """Response from beginning WebAuthn authentication"""
    options: Dict[str, Any] = Field(..., description="WebAuthn authentication options")
    challenge_key: str = Field(..., description="Challenge key for completing authentication")
    expires_at: str = Field(..., description="Challenge expiration time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "options": {
                    "challenge": "Y2hhbGxlbmdl",
                    "timeout": 300000,
                    "rpId": "example.com",
                    "allowCredentials": [
                        {
                            "id": "Y3JlZGVudGlhbF9pZA==",
                            "type": "public-key",
                            "transports": ["internal"]
                        }
                    ],
                    "userVerification": "required"
                },
                "challenge_key": "auth_abc123",
                "expires_at": "2024-01-15T10:35:00Z"
            }
        }

class WebAuthnAuthenticationCompleteRequest(BaseModel):
    """Request to complete WebAuthn authentication"""
    challenge_key: str = Field(..., description="Challenge key from begin request")
    credential_response: Dict[str, Any] = Field(..., description="WebAuthn authentication response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "challenge_key": "auth_abc123",
                "credential_response": {
                    "id": "credential_id_base64",
                    "rawId": "credential_id_base64",
                    "response": {
                        "authenticatorData": "authenticator_data_base64",
                        "clientDataJSON": "client_data_json_base64",
                        "signature": "signature_base64",
                        "userHandle": "user_handle_base64"
                    },
                    "type": "public-key"
                }
            }
        }

class WebAuthnAuthenticationCompleteResponse(BaseModel):
    """Response from completing WebAuthn authentication"""
    success: bool = Field(..., description="Whether authentication was successful")
    user_id: int = Field(..., description="Authenticated user ID")
    username: str = Field(..., description="Authenticated username")
    credential_name: str = Field(..., description="Name of credential used")
    last_used: str = Field(..., description="When the credential was last used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "user_id": 12345,
                "username": "dr.smith",
                "credential_name": "iPhone FaceID",
                "last_used": "2024-01-15T10:30:00Z"
            }
        }

# Credential Management Schemas
class WebAuthnCredentialInfo(BaseModel):
    """Information about a WebAuthn credential"""
    id: int = Field(..., description="Credential database ID")
    credential_name: str = Field(..., description="Human-readable credential name")
    authenticator_type: AuthenticatorType = Field(..., description="Type of authenticator")
    status: CredentialStatus = Field(..., description="Credential status")
    created_at: str = Field(..., description="When credential was created")
    last_used: Optional[str] = Field(None, description="When credential was last used")
    sign_count: int = Field(..., description="Signature counter value")
    aaguid: Optional[str] = Field(None, description="Authenticator AAGUID")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 123,
                "credential_name": "iPhone FaceID",
                "authenticator_type": "platform",
                "status": "active",
                "created_at": "2024-01-15T10:30:00Z",
                "last_used": "2024-01-15T14:45:00Z",
                "sign_count": 42,
                "aaguid": "12345678-1234-5678-9012-123456789abc"
            }
        }

class WebAuthnCredentialListResponse(BaseModel):
    """List of user's WebAuthn credentials"""
    credentials: List[WebAuthnCredentialInfo] = Field(..., description="List of credentials")
    total_count: int = Field(..., description="Total number of credentials")
    
    class Config:
        json_schema_extra = {
            "example": {
                "credentials": [
                    {
                        "id": 123,
                        "credential_name": "iPhone FaceID",
                        "authenticator_type": "platform",
                        "status": "active",
                        "created_at": "2024-01-15T10:30:00Z",
                        "last_used": "2024-01-15T14:45:00Z",
                        "sign_count": 42,
                        "aaguid": "12345678-1234-5678-9012-123456789abc"
                    }
                ],
                "total_count": 1
            }
        }

class WebAuthnCredentialRevokeRequest(BaseModel):
    """Request to revoke a WebAuthn credential"""
    credential_id: str = Field(..., description="Credential ID to revoke")
    reason: str = Field("user_requested", description="Reason for revocation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "credential_id": "Y3JlZGVudGlhbF9pZA==",
                "reason": "device_lost"
            }
        }

class WebAuthnCredentialRevokeResponse(BaseModel):
    """Response from revoking a WebAuthn credential"""
    success: bool = Field(..., description="Whether revocation was successful")
    message: str = Field(..., description="Result message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Credential revoked successfully"
            }
        }

# Error Schemas
class WebAuthnErrorResponse(BaseModel):
    """WebAuthn error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "verification_failed",
                "message": "WebAuthn verification failed",
                "details": {
                    "challenge_expired": False,
                    "invalid_signature": True
                }
            }
        }
