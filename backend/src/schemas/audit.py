"""
Audit Trail Pydantic Schemas
Data models for audit logging API responses
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

class AuditEventType(str, Enum):
    """Types of auditable events"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_FAILED_LOGIN = "user_failed_login"
    DATA_ACCESS = "data_access"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DECISION_CREATE = "decision_create"
    DECISION_APPROVE = "decision_approve"
    PROTOCOL_CREATE = "protocol_create"
    PROTOCOL_UPDATE = "protocol_update"
    PROTOCOL_FORK = "protocol_fork"
    EVIDENCE_CREATE = "evidence_create"
    EVIDENCE_UPDATE = "evidence_update"
    SYSTEM_CONFIG = "system_config"
    PERMISSION_CHANGE = "permission_change"
    EMERGENCY_ACCESS = "emergency_access"

class AuditSeverity(str, Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AuditEventCreate(BaseModel):
    """Schema for creating audit events"""
    event_type: AuditEventType
    resource_type: str = Field(..., description="Type of resource affected")
    resource_id: Optional[str] = Field(None, description="ID of specific resource")
    action: str = Field(..., description="Action performed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional event details")
    severity: AuditSeverity = AuditSeverity.MEDIUM
    session_id: Optional[str] = Field(None, description="User session ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "data_access",
                "resource_type": "patient",
                "resource_id": "12345",
                "action": "view_patient_record",
                "details": {
                    "fields_accessed": ["name", "diagnosis", "treatment_plan"],
                    "access_reason": "treatment_review"
                },
                "severity": "medium",
                "session_id": "sess_abc123"
            }
        }

class AuditLogResponse(BaseModel):
    """Schema for audit log entry response"""
    id: int
    event_type: str
    user_id: Optional[int]
    username: Optional[str] = Field(None, description="Username of the user who performed the action")
    resource_type: str
    resource_id: Optional[str]
    action: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    severity: str
    session_id: Optional[str]
    hash: str = Field(..., description="Tamper-proof cryptographic hash")
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 12345,
                "event_type": "data_access",
                "user_id": 67890,
                "username": "dr.smith",
                "resource_type": "patient",
                "resource_id": "patient_123",
                "action": "view_patient_record",
                "details": {
                    "fields_accessed": ["diagnosis", "treatment_plan"],
                    "duration_seconds": 45
                },
                "ip_address": "192.168.1.100",
                "user_agent": "Mozilla/5.0...",
                "severity": "medium",
                "session_id": "sess_abc123",
                "hash": "a1b2c3d4e5f6...",
                "context": {"department": "oncology"},
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

class PaginationResponse(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    total: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

class AuditTrailResponse(BaseModel):
    """Schema for paginated audit trail response"""
    events: List[AuditLogResponse]
    pagination: PaginationResponse
    
    class Config:
        json_schema_extra = {
            "example": {
                "events": [
                    {
                        "id": 12345,
                        "event_type": "data_access",
                        "user_id": 67890,
                        "username": "dr.smith",
                        "resource_type": "patient",
                        "resource_id": "patient_123",
                        "action": "view_patient_record",
                        "details": {"fields_accessed": ["diagnosis"]},
                        "ip_address": "192.168.1.100",
                        "user_agent": "Mozilla/5.0...",
                        "severity": "medium",
                        "session_id": "sess_abc123",
                        "hash": "a1b2c3d4e5f6...",
                        "context": {},
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "pagination": {
                    "page": 1,
                    "per_page": 50,
                    "total": 150,
                    "total_pages": 3
                }
            }
        }

class AuditStatisticsResponse(BaseModel):
    """Schema for audit statistics response"""
    total_events: int = Field(..., description="Total number of audit events")
    event_type_distribution: Dict[str, int] = Field(..., description="Count by event type")
    severity_distribution: Dict[str, int] = Field(..., description="Count by severity level")
    top_users: List[tuple] = Field(..., description="Most active users (user_id, count)")
    date_range: Dict[str, Optional[datetime]] = Field(..., description="Date range of analysis")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_events": 1250,
                "event_type_distribution": {
                    "data_access": 650,
                    "data_create": 200,
                    "data_update": 300,
                    "user_login": 100
                },
                "severity_distribution": {
                    "low": 400,
                    "medium": 700,
                    "high": 130,
                    "critical": 20
                },
                "top_users": [
                    [67890, 125],
                    [67891, 98],
                    [67892, 87]
                ],
                "date_range": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-31T23:59:59Z"
                }
            }
        }

class AuditIntegrityResponse(BaseModel):
    """Schema for audit integrity verification response"""
    is_valid: bool = Field(..., description="Whether the audit chain is valid")
    total_events: int = Field(..., description="Number of events verified")
    verification_timestamp: datetime = Field(..., description="When verification was performed")
    date_range: Dict[str, Optional[datetime]] = Field(..., description="Date range verified")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "total_events": 1250,
                "verification_timestamp": "2024-01-15T10:30:00Z",
                "date_range": {
                    "start": "2024-01-01T00:00:00Z",
                    "end": "2024-01-31T23:59:59Z"
                }
            }
        }

class AuditSearchResponse(BaseModel):
    """Schema for audit search results"""
    results: List[AuditLogResponse]
    total_matches: int = Field(..., description="Total number of matching events")
    search_query: str = Field(..., description="The search query used")
    search_field: str = Field(..., description="The field that was searched")
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": 12345,
                        "event_type": "data_access",
                        "user_id": 67890,
                        "username": "dr.smith",
                        "resource_type": "patient",
                        "resource_id": "patient_123",
                        "action": "view_patient_record",
                        "details": {"search_term_found": "diagnosis"},
                        "ip_address": "192.168.1.100",
                        "user_agent": "Mozilla/5.0...",
                        "severity": "medium",
                        "session_id": "sess_abc123",
                        "hash": "a1b2c3d4e5f6...",
                        "context": {},
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ],
                "total_matches": 15,
                "search_query": "diagnosis",
                "search_field": "details"
            }
        }

class AuditExportRequest(BaseModel):
    """Schema for audit export requests"""
    format: str = Field(..., regex="^(csv|json|xlsx)$", description="Export format")
    start_date: Optional[datetime] = Field(None, description="Start date for export")
    end_date: Optional[datetime] = Field(None, description="End date for export")
    event_types: Optional[List[AuditEventType]] = Field(None, description="Event types to include")
    include_hash: bool = Field(True, description="Include cryptographic hashes in export")
    include_details: bool = Field(True, description="Include event details in export")
    
    class Config:
        json_schema_extra = {
            "example": {
                "format": "csv",
                "start_date": "2024-01-01T00:00:00Z",
                "end_date": "2024-01-31T23:59:59Z",
                "event_types": ["data_access", "data_update"],
                "include_hash": True,
                "include_details": True
            }
        }

class AuditDashboardMetrics(BaseModel):
    """Schema for audit dashboard real-time metrics"""
    recent_activity: List[AuditLogResponse] = Field(..., description="Most recent audit events")
    hourly_stats: Dict[str, int] = Field(..., description="Event counts by hour")
    critical_alerts: List[AuditLogResponse] = Field(..., description="Critical severity events")
    user_activity_summary: Dict[str, Any] = Field(..., description="Summary of user activity")
    security_events: List[AuditLogResponse] = Field(..., description="Security-related events")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recent_activity": [],
                "hourly_stats": {
                    "00": 45, "01": 23, "02": 12,
                    "09": 150, "10": 180, "11": 165
                },
                "critical_alerts": [],
                "user_activity_summary": {
                    "active_users_today": 25,
                    "total_sessions": 45,
                    "avg_session_duration": 120
                },
                "security_events": []
            }
        }
