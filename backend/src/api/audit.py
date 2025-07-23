"""
Audit Trail Explorer API Endpoints
HIPAA-compliant audit log access and analysis
"""

from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from ..db.database import get_db
from ..core.deps import get_current_user, get_current_active_user
from ..core.rbac import RBACMatrix, Resource, Action, Role
from ..services.audit_service import (
    AuditService, 
    AuditEventType, 
    AuditSeverity,
    AuditEvent
)
from ..schemas.user import User
from ..schemas.audit import (
    AuditLogResponse,
    AuditTrailResponse,
    AuditStatisticsResponse,
    AuditIntegrityResponse,
    AuditEventCreate
)

router = APIRouter(prefix="/audit", tags=["audit"])

# RBAC instance
rbac = RBACMatrix()

class AuditQueryParams(BaseModel):
    """Audit trail query parameters"""
    user_id: Optional[int] = Field(None, description="Filter by user ID")
    resource_type: Optional[str] = Field(None, description="Filter by resource type")
    resource_id: Optional[str] = Field(None, description="Filter by resource ID")
    event_type: Optional[AuditEventType] = Field(None, description="Filter by event type")
    severity: Optional[AuditSeverity] = Field(None, description="Filter by severity")
    start_date: Optional[datetime] = Field(None, description="Start date for filtering")
    end_date: Optional[datetime] = Field(None, description="End date for filtering")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(50, ge=1, le=1000, description="Items per page")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", pattern="^(asc|desc)$", description="Sort order")

@router.get("/logs", response_model=AuditTrailResponse)
async def get_audit_logs(
    params: AuditQueryParams = Depends(),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get filtered audit logs with pagination
    Requires AUDIT permission on AUDIT_LOG resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role, 
        Resource.AUDIT_LOG, 
        Action.AUDIT,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access audit logs"
        )
    
    audit_service = AuditService(db)
    
    try:
        result = await audit_service.get_audit_trail(
            user_id=params.user_id,
            resource_type=params.resource_type,
            resource_id=params.resource_id,
            event_type=params.event_type,
            severity=params.severity,
            start_date=params.start_date,
            end_date=params.end_date,
            page=params.page,
            per_page=params.per_page,
            sort_by=params.sort_by,
            sort_order=params.sort_order
        )
        
        # Log the audit access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="audit_log",
                resource_id=None,
                action="view_audit_trail",
                details={
                    "filters": params.dict(exclude_none=True),
                    "total_results": result["pagination"]["total"]
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        return AuditTrailResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit logs: {str(e)}"
        )

@router.get("/logs/{log_id}", response_model=AuditLogResponse)
async def get_audit_log_detail(
    log_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed audit log entry
    Requires AUDIT permission on AUDIT_LOG resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.AUDIT_LOG,
        Action.READ,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access audit log details"
        )
    
    # Get specific audit log
    from ..db.models import AuditLog
    audit_log = db.query(AuditLog).filter(AuditLog.id == log_id).first()
    
    if not audit_log:
        raise HTTPException(
            status_code=404,
            detail="Audit log not found"
        )
    
    # Log the access
    audit_service = AuditService(db)
    await audit_service.log_event(
        AuditEvent(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=current_user.id,
            resource_type="audit_log",
            resource_id=str(log_id),
            action="view_audit_detail",
            details={"accessed_log_id": log_id},
            ip_address="",  # Extract from request
            user_agent="",  # Extract from request
            severity=AuditSeverity.LOW
        )
    )
    
    return AuditLogResponse(
        id=audit_log.id,
        event_type=audit_log.event_type,
        user_id=audit_log.user_id,
        username=audit_log.user.username if audit_log.user else None,
        resource_type=audit_log.resource_type,
        resource_id=audit_log.resource_id,
        action=audit_log.action,
        details=audit_log.details,
        ip_address=audit_log.ip_address,
        user_agent=audit_log.user_agent,
        severity=audit_log.severity,
        session_id=audit_log.session_id,
        hash=audit_log.hash,
        context=audit_log.context,
        created_at=audit_log.created_at
    )

@router.get("/statistics", response_model=AuditStatisticsResponse)
async def get_audit_statistics(
    start_date: Optional[datetime] = Query(None, description="Start date for statistics"),
    end_date: Optional[datetime] = Query(None, description="End date for statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get audit trail statistics and analytics
    Requires AUDIT permission on AUDIT_LOG resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.AUDIT_LOG,
        Action.AUDIT,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access audit statistics"
        )
    
    audit_service = AuditService(db)
    
    try:
        stats = await audit_service.get_audit_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        # Log the statistics access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="audit_log",
                resource_id=None,
                action="view_audit_statistics",
                details={
                    "date_range": {
                        "start": start_date.isoformat() if start_date else None,
                        "end": end_date.isoformat() if end_date else None
                    }
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        return AuditStatisticsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve audit statistics: {str(e)}"
        )

@router.post("/verify-integrity", response_model=AuditIntegrityResponse)
async def verify_audit_integrity(
    start_date: Optional[datetime] = Query(None, description="Start date for verification"),
    end_date: Optional[datetime] = Query(None, description="End date for verification"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verify the cryptographic integrity of audit logs
    Requires AUDIT permission on AUDIT_LOG resource
    """
    
    # Check permissions - only admins and auditors can verify integrity
    if current_user.role not in [Role.ADMINISTRATOR, Role.SUPER_ADMIN, Role.AUDITOR]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to verify audit integrity"
        )
    
    audit_service = AuditService(db)
    
    try:
        integrity_result = await audit_service.verify_audit_integrity(
            start_date=start_date,
            end_date=end_date
        )
        
        # Log the integrity verification
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.AUDIT,
                user_id=current_user.id,
                resource_type="audit_log",
                resource_id=None,
                action="verify_integrity",
                details={
                    "integrity_check": integrity_result,
                    "date_range": {
                        "start": start_date.isoformat() if start_date else None,
                        "end": end_date.isoformat() if end_date else None
                    }
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.HIGH
            )
        )
        
        return AuditIntegrityResponse(**integrity_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify audit integrity: {str(e)}"
        )

@router.get("/export")
async def export_audit_logs(
    format: str = Query("csv", regex="^(csv|json|xlsx)$"),
    start_date: Optional[datetime] = Query(None, description="Start date for export"),
    end_date: Optional[datetime] = Query(None, description="End date for export"),
    event_types: Optional[List[AuditEventType]] = Query(None, description="Event types to include"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Export audit logs in various formats
    Requires EXPORT permission on AUDIT_LOG resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.AUDIT_LOG,
        Action.EXPORT,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to export audit logs"
        )
    
    # Implementation for export functionality
    # This would generate the requested format and return it
    # For now, return placeholder
    
    audit_service = AuditService(db)
    
    # Log the export action
    await audit_service.log_event(
        AuditEvent(
            event_type=AuditEventType.DATA_EXPORT,
            user_id=current_user.id,
            resource_type="audit_log",
            resource_id=None,
            action="export_audit_logs",
            details={
                "format": format,
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                },
                "event_types": [et.value for et in event_types] if event_types else None
            },
            ip_address="",  # Extract from request
            user_agent="",  # Extract from request
            severity=AuditSeverity.HIGH
        )
    )
    
    return {"message": "Export functionality to be implemented"}

@router.get("/search")
async def search_audit_logs(
    query: str = Query(..., min_length=3, description="Search query"),
    field: str = Query("details", regex="^(details|action|resource_type|user_agent)$"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Full-text search through audit logs
    Requires AUDIT permission on AUDIT_LOG resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.AUDIT_LOG,
        Action.AUDIT,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to search audit logs"
        )
    
    # Implementation for full-text search
    # This would perform the actual search based on the field and query
    
    audit_service = AuditService(db)
    
    # Log the search action
    await audit_service.log_event(
        AuditEvent(
            event_type=AuditEventType.DATA_ACCESS,
            user_id=current_user.id,
            resource_type="audit_log",
            resource_id=None,
            action="search_audit_logs",
            details={
                "search_query": query,
                "search_field": field
            },
            ip_address="",  # Extract from request
            user_agent="",  # Extract from request
            severity=AuditSeverity.MEDIUM
        )
    )
    
    return {"message": "Search functionality to be implemented", "query": query, "field": field}
