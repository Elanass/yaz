"""
Cohort Management API endpoints for batch clinical decision support
Handles cohort upload, validation, batch processing, and result management
"""

from typing import List, Dict, Any, Optional
from fastapi import (
    APIRouter, Depends, HTTPException, status, BackgroundTasks, 
    UploadFile, File, Form, Query
)
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
import json
import uuid
import io

from ...core.security import get_current_user, rbac_manager
from ...core.logging import clinical_logger, performance_logger
from ...db.database import get_async_session
from ...services.cohort_service import CohortService
from ...schemas.cohort import (
    CohortStudyCreate, CohortStudyResponse, CohortPatientCreate,
    InferenceSessionCreate, InferenceSessionResponse,
    PatientDecisionResultResponse, CohortExportRequest,
    CohortHypothesisCreate, CohortHypothesisResponse
)

router = APIRouter()


class CohortUploadRequest(BaseModel):
    """Cohort upload request model"""
    study_name: str
    description: Optional[str] = None
    format_type: str = "manual"  # manual, csv, json, fhir
    engine_name: str = "adci"
    include_alternatives: bool = True
    confidence_threshold: float = 0.75


@router.post("/upload", response_model=CohortStudyResponse)
async def upload_cohort(
    upload_request: CohortUploadRequest = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Upload and create a new cohort study"""
    
    # Check permissions
    if not rbac_manager.has_permission(current_user.get("role"), "manage_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to manage cohorts"
        )
    
    try:
        cohort_service = CohortService(db)
        
        # Parse upload request from form data
        if isinstance(upload_request, str):
            upload_data = json.loads(upload_request)
            upload_request = CohortUploadRequest(**upload_data)
        
        # Create cohort study
        cohort_data = CohortStudyCreate(
            study_name=upload_request.study_name,
            description=upload_request.description,
            uploaded_by=current_user["sub"],
            format_type=upload_request.format_type,
            engine_name=upload_request.engine_name,
            include_alternatives=upload_request.include_alternatives,
            confidence_threshold=upload_request.confidence_threshold
        )
        
        cohort_study = await cohort_service.create_cohort_study(cohort_data)
        
        # Process file if provided
        if file:
            file_content = await file.read()
            
            # Validate and process file based on format
            if upload_request.format_type == "csv":
                patients = await cohort_service.process_csv_file(
                    file_content, cohort_study.id
                )
            elif upload_request.format_type == "json":
                patients = await cohort_service.process_json_file(
                    file_content, cohort_study.id
                )
            elif upload_request.format_type == "fhir":
                patients = await cohort_service.process_fhir_file(
                    file_content, cohort_study.id
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Unsupported file format: {upload_request.format_type}"
                )
            
            # Log successful upload
            clinical_logger.log_cohort_upload(
                user_id=current_user["sub"],
                cohort_id=str(cohort_study.id),
                patient_count=len(patients),
                format_type=upload_request.format_type
            )
        
        return cohort_study
        
    except Exception as e:
        clinical_logger.log_error(
            "cohort_upload_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"study_name": upload_request.study_name}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload cohort"
        )


@router.post("/{cohort_id}/patients", response_model=List[CohortPatientCreate])
async def add_patients_to_cohort(
    cohort_id: uuid.UUID,
    patients: List[CohortPatientCreate],
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Add patients manually to an existing cohort"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "manage_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to manage cohorts"
        )
    
    try:
        cohort_service = CohortService(db)
        
        # Verify cohort exists and user has access
        cohort = await cohort_service.get_cohort_study(cohort_id)
        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohort study not found"
            )
        
        # Add patients to cohort
        added_patients = []
        for patient_data in patients:
            patient_data.cohort_study_id = cohort_id
            patient = await cohort_service.add_patient_to_cohort(patient_data)
            added_patients.append(patient)
        
        clinical_logger.log_cohort_update(
            user_id=current_user["sub"],
            cohort_id=str(cohort_id),
            action="add_patients",
            patient_count=len(added_patients)
        )
        
        return added_patients
        
    except HTTPException:
        raise
    except Exception as e:
        clinical_logger.log_error(
            "cohort_patient_add_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"cohort_id": str(cohort_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add patients to cohort"
        )


@router.post("/{cohort_id}/process", response_model=InferenceSessionResponse)
async def process_cohort_batch(
    cohort_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    session_data: Optional[InferenceSessionCreate] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Start batch processing of a cohort through decision engines"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "access_decision_engines"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to access decision engines"
        )
    
    try:
        cohort_service = CohortService(db)
        
        # Verify cohort exists
        cohort = await cohort_service.get_cohort_study(cohort_id)
        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohort study not found"
            )
        
        # Create inference session
        if not session_data:
            session_data = InferenceSessionCreate(
                cohort_study_id=cohort_id,
                session_name=f"Batch Processing - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                processed_by=current_user["sub"]
            )
        else:
            session_data.cohort_study_id = cohort_id
            session_data.processed_by = current_user["sub"]
        
        session = await cohort_service.create_inference_session(session_data)
        
        # Start background processing
        background_tasks.add_task(
            cohort_service.process_cohort_batch,
            session.id,
            current_user["sub"]
        )
        
        clinical_logger.log_cohort_processing_start(
            user_id=current_user["sub"],
            cohort_id=str(cohort_id),
            session_id=str(session.id)
        )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        clinical_logger.log_error(
            "cohort_batch_process_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"cohort_id": str(cohort_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start batch processing"
        )


@router.get("/{cohort_id}/sessions", response_model=List[InferenceSessionResponse])
async def get_cohort_sessions(
    cohort_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get all inference sessions for a cohort"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "view_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view cohorts"
        )
    
    try:
        cohort_service = CohortService(db)
        sessions = await cohort_service.get_cohort_sessions(cohort_id)
        return sessions
        
    except Exception as e:
        clinical_logger.log_error(
            "cohort_sessions_fetch_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"cohort_id": str(cohort_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cohort sessions"
        )


@router.get("/sessions/{session_id}/results", response_model=List[PatientDecisionResultResponse])
async def get_session_results(
    session_id: uuid.UUID,
    risk_threshold: Optional[float] = Query(None, ge=0.0, le=1.0),
    confidence_threshold: Optional[float] = Query(None, ge=0.0, le=1.0),
    protocol_filter: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get paginated results from an inference session with filtering"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "view_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view results"
        )
    
    try:
        cohort_service = CohortService(db)
        
        # Build filters
        filters = {}
        if risk_threshold is not None:
            filters["risk_threshold"] = risk_threshold
        if confidence_threshold is not None:
            filters["confidence_threshold"] = confidence_threshold
        if protocol_filter:
            filters["protocol_filter"] = protocol_filter
        
        results = await cohort_service.get_session_results(
            session_id, filters, limit, offset
        )
        
        return results
        
    except Exception as e:
        clinical_logger.log_error(
            "session_results_fetch_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"session_id": str(session_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session results"
        )


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get comprehensive summary of session results"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "view_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view results"
        )
    
    try:
        cohort_service = CohortService(db)
        summary = await cohort_service.get_session_summary(session_id)
        return summary
        
    except Exception as e:
        clinical_logger.log_error(
            "session_summary_fetch_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"session_id": str(session_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session summary"
        )


@router.post("/sessions/{session_id}/export", response_model=Dict[str, str])
async def export_session_results(
    session_id: uuid.UUID,
    export_request: CohortExportRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Export session results in various formats"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "export_data"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to export data"
        )
    
    try:
        cohort_service = CohortService(db)
        
        # Create export task
        export_task = await cohort_service.create_export_task(
            session_id=session_id,
            export_format=export_request.export_format,
            filters=export_request.filters,
            requested_by=current_user["sub"]
        )
        
        # Start background export
        background_tasks.add_task(
            cohort_service.process_export_task,
            export_task.id
        )
        
        clinical_logger.log_export_request(
            user_id=current_user["sub"],
            session_id=str(session_id),
            export_format=export_request.export_format
        )
        
        return {
            "export_id": str(export_task.id),
            "status": "processing",
            "message": "Export task created successfully"
        }
        
    except Exception as e:
        clinical_logger.log_error(
            "export_request_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"session_id": str(session_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create export task"
        )


@router.get("/exports/{export_id}/download")
async def download_export(
    export_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Download completed export file"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "export_data"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to download exports"
        )
    
    try:
        cohort_service = CohortService(db)
        
        # Get export task
        export_task = await cohort_service.get_export_task(export_id)
        if not export_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Export not found"
            )
        
        if export_task.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Export not ready. Status: {export_task.status}"
            )
        
        # Get file content from IPFS
        file_content = await cohort_service.get_export_file_content(export_task.ipfs_hash)
        
        # Determine content type
        content_type = {
            "csv": "text/csv",
            "pdf": "application/pdf",
            "fhir": "application/fhir+json",
            "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }.get(export_task.export_format, "application/octet-stream")
        
        # Create filename
        filename = f"cohort_export_{export_id}.{export_task.export_format}"
        
        clinical_logger.log_export_download(
            user_id=current_user["sub"],
            export_id=str(export_id)
        )
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=content_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        clinical_logger.log_error(
            "export_download_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"export_id": str(export_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download export"
        )


@router.post("/sessions/{session_id}/hypotheses", response_model=CohortHypothesisResponse)
async def create_hypothesis(
    session_id: uuid.UUID,
    hypothesis_data: CohortHypothesisCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new hypothesis for cohort analysis"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "analyze_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to analyze cohorts"
        )
    
    try:
        cohort_service = CohortService(db)
        
        hypothesis_data.session_id = session_id
        hypothesis_data.created_by = current_user["sub"]
        
        hypothesis = await cohort_service.create_hypothesis(hypothesis_data)
        
        clinical_logger.log_hypothesis_creation(
            user_id=current_user["sub"],
            session_id=str(session_id),
            hypothesis_id=str(hypothesis.id)
        )
        
        return hypothesis
        
    except Exception as e:
        clinical_logger.log_error(
            "hypothesis_creation_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"session_id": str(session_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create hypothesis"
        )


@router.get("", response_model=List[CohortStudyResponse])
async def list_cohorts(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """List cohort studies with pagination and filtering"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "view_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view cohorts"
        )
    
    try:
        cohort_service = CohortService(db)
        
        filters = {}
        if status:
            filters["status"] = status
        
        cohorts = await cohort_service.list_cohort_studies(
            filters=filters,
            limit=limit,
            offset=offset,
            user_id=current_user["sub"]
        )
        
        return cohorts
        
    except Exception as e:
        clinical_logger.log_error(
            "cohort_list_error",
            error=str(e),
            user_id=current_user["sub"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cohort list"
        )


@router.get("/{cohort_id}", response_model=CohortStudyResponse)
async def get_cohort(
    cohort_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_session)
):
    """Get detailed information about a specific cohort"""
    
    if not rbac_manager.has_permission(current_user.get("role"), "view_cohorts"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to view cohorts"
        )
    
    try:
        cohort_service = CohortService(db)
        cohort = await cohort_service.get_cohort_study(cohort_id)
        
        if not cohort:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cohort study not found"
            )
        
        return cohort
        
    except HTTPException:
        raise
    except Exception as e:
        clinical_logger.log_error(
            "cohort_get_error",
            error=str(e),
            user_id=current_user["sub"],
            context={"cohort_id": str(cohort_id)}
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch cohort details"
        )
