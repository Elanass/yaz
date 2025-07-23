"""
Evidence Storage API Endpoints
Tamper-proof evidence logging and retrieval
"""

from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import io

from ..db.database import get_db
from ..core.deps import get_current_user, get_current_active_user
from ..core.rbac import RBACMatrix, Resource, Action, Role
from ..services.evidence_service import (
    TamperProofEvidenceService,
    EvidenceRecord
)
from ..services.audit_service import AuditService, AuditEvent, AuditEventType, AuditSeverity
from ..schemas.user import User
from ..schemas.evidence import (
    EvidenceType,
    EvidenceCreate,
    EvidenceResponse,
    EvidenceDetailResponse,
    EvidenceSearchRequest,
    EvidenceSearchResponse,
    EvidenceVerificationRequest,
    EvidenceVerificationResponse,
    EvidenceStatsResponse,
    FileUploadResponse,
    EvidenceMetadata
)

router = APIRouter(prefix="/evidence", tags=["evidence"])

# RBAC instance
rbac = RBACMatrix()

@router.post("/", response_model=dict)
async def create_evidence(
    evidence_data: EvidenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create new tamper-proof evidence record
    Requires CREATE permission on EVIDENCE resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.EVIDENCE,
        Action.CREATE,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to create evidence"
        )
    
    try:
        evidence_service = TamperProofEvidenceService(db)
        audit_service = AuditService(db)
        
        # Create evidence record
        evidence_record = EvidenceRecord(
            evidence_id="",  # Will be auto-generated
            evidence_type=evidence_data.evidence_type,
            title=evidence_data.title,
            description=evidence_data.description,
            content=evidence_data.content,
            metadata=evidence_data.metadata,
            source=evidence_data.source,
            created_by=current_user.id,
            tags=evidence_data.tags,
            clinical_context=evidence_data.clinical_context
        )
        
        # Store evidence with tamper-proof guarantees
        result = await evidence_service.store_evidence(evidence_record)
        
        # Log the creation
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.EVIDENCE_CREATE,
                user_id=current_user.id,
                resource_type="evidence",
                resource_id=result["evidence_id"],
                action="create_evidence",
                details={
                    "evidence_type": evidence_data.evidence_type.value,
                    "title": evidence_data.title,
                    "ipfs_hash": result["ipfs_hash"],
                    "content_hash": result["content_hash"]
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        return {
            "message": "Evidence created successfully",
            "evidence_id": result["evidence_id"],
            "ipfs_hash": result["ipfs_hash"],
            "verification_status": result["verification_status"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create evidence: {str(e)}"
        )

@router.post("/upload", response_model=FileUploadResponse)
async def upload_evidence_file(
    file: UploadFile = File(...),
    evidence_type: EvidenceType = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    source: str = Form(...),
    tags: str = Form(""),  # Comma-separated tags
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Upload evidence file with metadata
    Requires CREATE permission on EVIDENCE resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.EVIDENCE,
        Action.CREATE,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to upload evidence"
        )
    
    try:
        # Validate file size (max 100MB)
        MAX_FILE_SIZE = 100 * 1024 * 1024
        file_content = await file.read()
        
        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size is 100MB"
            )
        
        # Validate file type
        allowed_types = {
            "application/pdf", "image/jpeg", "image/png", "image/dicom",
            "text/plain", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed"
            )
        
        evidence_service = TamperProofEvidenceService(db)
        audit_service = AuditService(db)
        
        # Parse tags
        tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []
        
        # Create evidence record with file
        evidence_record = EvidenceRecord(
            evidence_id="",  # Will be auto-generated
            evidence_type=evidence_type,
            title=title,
            description=description,
            content=f"File attachment: {file.filename}",
            metadata=EvidenceMetadata(),  # Basic metadata for file upload
            source=source,
            created_by=current_user.id,
            tags=tag_list,
            clinical_context={"file_upload": True, "filename": file.filename}
        )
        
        # Store evidence with file content
        result = await evidence_service.store_evidence(evidence_record, file_content)
        
        # Log the upload
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.EVIDENCE_CREATE,
                user_id=current_user.id,
                resource_type="evidence",
                resource_id=result["evidence_id"],
                action="upload_evidence_file",
                details={
                    "filename": file.filename,
                    "file_size": len(file_content),
                    "content_type": file.content_type,
                    "evidence_type": evidence_type.value,
                    "ipfs_hash": result["ipfs_hash"],
                    "file_ipfs_hash": result["file_ipfs_hash"]
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        return FileUploadResponse(
            filename=file.filename,
            file_size=len(file_content),
            content_type=file.content_type,
            ipfs_hash=result["file_ipfs_hash"],
            upload_timestamp=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload evidence file: {str(e)}"
        )

@router.get("/{evidence_id}", response_model=EvidenceDetailResponse)
async def get_evidence(
    evidence_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve evidence with integrity verification
    Requires READ permission on EVIDENCE resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.EVIDENCE,
        Action.READ,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access evidence"
        )
    
    try:
        evidence_service = TamperProofEvidenceService(db)
        audit_service = AuditService(db)
        
        # Retrieve evidence with verification
        result = await evidence_service.retrieve_evidence(evidence_id)
        
        # Log the access
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="evidence",
                resource_id=evidence_id,
                action="view_evidence",
                details={
                    "verification_status": {
                        "signature_valid": result["verification"]["signature_valid"],
                        "hash_valid": result["verification"]["hash_valid"]
                    }
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        evidence_data = result["evidence_data"]
        verification = result["verification"]
        
        return EvidenceDetailResponse(
            evidence_id=evidence_data["evidence_id"],
            evidence_type=evidence_data["evidence_type"],
            title=evidence_data["title"],
            description=evidence_data["description"],
            content=evidence_data["content"],
            metadata=EvidenceMetadata(**evidence_data["metadata"]),
            source=evidence_data["source"],
            tags=evidence_data["tags"],
            clinical_context=evidence_data["clinical_context"],
            created_by=evidence_data["created_by"],
            created_at=datetime.fromisoformat(evidence_data["timestamp"]),
            verification_status="verified" if verification["signature_valid"] and verification["hash_valid"] else "failed",
            ipfs_hash=verification["ipfs_hash"],
            content_hash=verification["content_hash"],
            has_file=result["file_content"] is not None,
            digital_signature="[REDACTED]",  # Don't expose full signature
            verification=verification
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evidence: {str(e)}"
        )

@router.get("/{evidence_id}/file")
async def download_evidence_file(
    evidence_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Download evidence file attachment
    Requires READ permission on EVIDENCE resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.EVIDENCE,
        Action.READ,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to download evidence file"
        )
    
    try:
        evidence_service = TamperProofEvidenceService(db)
        audit_service = AuditService(db)
        
        # Retrieve evidence with file content
        result = await evidence_service.retrieve_evidence(evidence_id)
        
        if not result["file_content"]:
            raise HTTPException(
                status_code=404,
                detail="No file attachment found for this evidence"
            )
        
        # Log the download
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="evidence",
                resource_id=evidence_id,
                action="download_evidence_file",
                details={"file_size": len(result["file_content"])},
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.MEDIUM
            )
        )
        
        # Get filename from evidence data
        evidence_data = result["evidence_data"]
        filename = evidence_data["clinical_context"].get("filename", f"evidence_{evidence_id}")
        
        # Create streaming response
        file_stream = io.BytesIO(result["file_content"])
        
        return StreamingResponse(
            io.BytesIO(result["file_content"]),
            media_type="application/octet-stream",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download evidence file: {str(e)}"
        )

@router.post("/search", response_model=EvidenceSearchResponse)
async def search_evidence(
    search_request: EvidenceSearchRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Search evidence with advanced filtering
    Requires READ permission on EVIDENCE resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.EVIDENCE,
        Action.READ,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to search evidence"
        )
    
    try:
        evidence_service = TamperProofEvidenceService(db)
        audit_service = AuditService(db)
        
        # Perform search
        start_time = datetime.utcnow()
        
        result = await evidence_service.search_evidence(
            query=search_request.query,
            evidence_type=search_request.evidence_type,
            tags=search_request.tags,
            created_by=search_request.created_by,
            start_date=search_request.start_date,
            end_date=search_request.end_date,
            page=search_request.page,
            per_page=search_request.per_page
        )
        
        search_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        
        # Log the search
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_ACCESS,
                user_id=current_user.id,
                resource_type="evidence",
                resource_id=None,
                action="search_evidence",
                details={
                    "search_params": search_request.dict(exclude_none=True),
                    "results_count": len(result["evidence"]),
                    "search_time_ms": search_time
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.LOW
            )
        )
        
        # Convert to response format
        evidence_responses = [
            EvidenceResponse(
                evidence_id=item["evidence_id"],
                evidence_type=item["evidence_type"],
                title=item["title"],
                description=item["description"],
                metadata=EvidenceMetadata(),  # Would need to populate from DB
                source=item["source"],
                tags=item["tags"],
                clinical_context={},
                created_by=None,
                created_at=datetime.fromisoformat(item["created_at"]),
                verification_status=item["verification_status"],
                ipfs_hash=item["ipfs_hash"],
                content_hash="",  # Would need to get from DB
                has_file=item["has_file"]
            )
            for item in result["evidence"]
        ]
        
        return EvidenceSearchResponse(
            evidence=evidence_responses,
            pagination=result["pagination"],
            search_metadata={
                "query": search_request.query,
                "search_time_ms": search_time,
                "filters_applied": [
                    key for key, value in search_request.dict(exclude_none=True).items()
                    if value is not None and key not in ["page", "per_page", "sort_by", "sort_order"]
                ]
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to search evidence: {str(e)}"
        )

@router.post("/verify", response_model=EvidenceVerificationResponse)
async def verify_evidence_integrity(
    verification_request: EvidenceVerificationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verify cryptographic integrity of evidence records
    Requires AUDIT permission on EVIDENCE resource
    """
    
    # Check permissions - only certain roles can verify integrity
    if current_user.role not in [Role.ADMINISTRATOR, Role.SUPER_ADMIN, Role.AUDITOR, Role.RESEARCHER]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to verify evidence integrity"
        )
    
    try:
        evidence_service = TamperProofEvidenceService(db)
        audit_service = AuditService(db)
        
        # Verify evidence chain
        result = await evidence_service.verify_evidence_chain(
            verification_request.evidence_ids
        )
        
        # Log the verification
        await audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.AUDIT,
                user_id=current_user.id,
                resource_type="evidence",
                resource_id=None,
                action="verify_evidence_integrity",
                details={
                    "evidence_count": len(verification_request.evidence_ids),
                    "overall_valid": result["overall_valid"],
                    "valid_count": result["valid_count"]
                },
                ip_address="",  # Extract from request
                user_agent="",  # Extract from request
                severity=AuditSeverity.HIGH
            )
        )
        
        return EvidenceVerificationResponse(
            overall_valid=result["overall_valid"],
            total_evidence=result["total_evidence"],
            valid_count=result["valid_count"],
            verification_results=result["verification_results"],
            verification_timestamp=datetime.fromisoformat(result["verification_timestamp"])
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify evidence integrity: {str(e)}"
        )

@router.get("/stats/overview", response_model=EvidenceStatsResponse)
async def get_evidence_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get evidence repository statistics
    Requires READ permission on EVIDENCE resource
    """
    
    # Check permissions
    if not rbac.has_permission(
        current_user.role,
        Resource.EVIDENCE,
        Action.READ,
        context={"user_id": current_user.id}
    ):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to access evidence statistics"
        )
    
    try:
        # Implementation would query database for statistics
        # For now, return placeholder
        
        return EvidenceStatsResponse(
            total_evidence=0,
            evidence_by_type={},
            evidence_by_quality={},
            evidence_by_month={},
            top_tags=[],
            verification_status={}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve evidence statistics: {str(e)}"
        )
