"""
Patient management API endpoints.
Handles patient data, medical records, and clinical information.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ...core.security import get_current_user, require_permissions
from ...core.logging import get_logger
from ...db.database import get_db
from ...db.models import User, Patient
from ...services.patient_service import PatientService
from ...schemas.patient import (
    PatientCreate, PatientUpdate, PatientResponse, PatientList,
    PatientDetailResponse, MedicalHistoryUpdate, TreatmentPlanResponse
)

router = APIRouter(prefix="/patients", tags=["patients"])
logger = get_logger(__name__)
security = HTTPBearer()

@router.get("/", response_model=PatientList)
async def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    practitioner_id: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions(["patients:read"])),
    db: AsyncSession = Depends(get_db)
):
    """List patients with filtering and pagination."""
    try:
        service = PatientService(db)
        
        # Filter by practitioner if user is a practitioner
        if current_user.role == "practitioner" and not practitioner_id:
            practitioner_id = str(current_user.id)
        
        patients, total = await service.list_patients(
            skip=skip,
            limit=limit,
            search=search,
            stage=stage,
            status=status,
            practitioner_id=practitioner_id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="patients.list",
            resource_type="patient",
            details={
                "filters": {
                    "search": search,
                    "stage": stage,
                    "status": status,
                    "practitioner_id": practitioner_id
                }
            }
        )
        
        return PatientList(
            patients=[PatientResponse.from_orm(patient) for patient in patients],
            total=total,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        logger.error(f"Error listing patients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patients"
        )

@router.get("/{patient_id}", response_model=PatientDetailResponse)
async def get_patient(
    patient_id: str,
    current_user: User = Depends(require_permissions(["patients:read"])),
    db: AsyncSession = Depends(get_db)
):
    """Get patient by ID with full details."""
    try:
        service = PatientService(db)
        patient = await service.get_patient_by_id(patient_id)
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check if user has access to this patient
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        # Patient can only access their own record
        if current_user.role == "patient" and patient.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.read",
            resource_type="patient",
            resource_id=patient_id
        )
        
        return PatientDetailResponse.from_orm(patient)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient"
        )

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient_data: PatientCreate,
    current_user: User = Depends(require_permissions(["patients:create"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new patient record."""
    try:
        service = PatientService(db)
        
        # Set practitioner_id if user is a practitioner
        if current_user.role == "practitioner":
            patient_data.practitioner_id = current_user.id
        
        new_patient = await service.create_patient(patient_data.dict())
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.create",
            resource_type="patient",
            resource_id=str(new_patient.id),
            details={"patient_name": f"{patient_data.first_name} {patient_data.last_name}"}
        )
        
        return PatientResponse.from_orm(new_patient)
    except Exception as e:
        logger.error(f"Error creating patient: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient"
        )

@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    patient_id: str,
    patient_update: PatientUpdate,
    current_user: User = Depends(require_permissions(["patients:update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update patient information."""
    try:
        service = PatientService(db)
        
        patient = await service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check access permissions
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        updated_patient = await service.update_patient(
            patient_id=patient_id,
            update_data=patient_update.dict(exclude_unset=True)
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.update",
            resource_type="patient",
            resource_id=patient_id,
            details={"updated_fields": list(patient_update.dict(exclude_unset=True).keys())}
        )
        
        return PatientResponse.from_orm(updated_patient)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient"
        )

@router.put("/{patient_id}/medical-history")
async def update_medical_history(
    patient_id: str,
    history_update: MedicalHistoryUpdate,
    current_user: User = Depends(require_permissions(["patients:update"])),
    db: AsyncSession = Depends(get_db)
):
    """Update patient's medical history."""
    try:
        service = PatientService(db)
        
        patient = await service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check access permissions
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        updated_patient = await service.update_medical_history(
            patient_id=patient_id,
            history_data=history_update.dict()
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.medical_history_update",
            resource_type="patient",
            resource_id=patient_id,
            details={"updated_sections": list(history_update.dict().keys())}
        )
        
        return {"message": "Medical history updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating medical history for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update medical history"
        )

@router.get("/{patient_id}/treatment-plans", response_model=List[TreatmentPlanResponse])
async def get_patient_treatment_plans(
    patient_id: str,
    current_user: User = Depends(require_permissions(["patients:read"])),
    db: AsyncSession = Depends(get_db)
):
    """Get all treatment plans for a patient."""
    try:
        service = PatientService(db)
        
        patient = await service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check access permissions
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        if current_user.role == "patient" and patient.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        treatment_plans = await service.get_patient_treatment_plans(patient_id)
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.treatment_plans_read",
            resource_type="patient",
            resource_id=patient_id
        )
        
        return [TreatmentPlanResponse.from_orm(plan) for plan in treatment_plans]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting treatment plans for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve treatment plans"
        )

@router.post("/{patient_id}/documents")
async def upload_patient_document(
    patient_id: str,
    file: UploadFile = File(...),
    document_type: str = Query(..., description="Type of document (lab_result, imaging, report, etc.)"),
    description: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions(["patients:update"])),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document for a patient."""
    try:
        service = PatientService(db)
        
        patient = await service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check access permissions
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        # Validate file size and type
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10MB"
            )
        
        allowed_types = [
            'application/pdf', 'image/jpeg', 'image/png', 'image/tiff',
            'application/dicom', 'text/plain', 'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ]
        
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type"
            )
        
        document = await service.upload_patient_document(
            patient_id=patient_id,
            file=file,
            document_type=document_type,
            description=description,
            uploaded_by=current_user.id
        )
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.document_upload",
            resource_type="patient",
            resource_id=patient_id,
            details={
                "document_type": document_type,
                "filename": file.filename,
                "file_size": file.size
            }
        )
        
        return {"message": "Document uploaded successfully", "document_id": str(document.id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document"
        )

@router.get("/{patient_id}/documents")
async def get_patient_documents(
    patient_id: str,
    document_type: Optional[str] = Query(None),
    current_user: User = Depends(require_permissions(["patients:read"])),
    db: AsyncSession = Depends(get_db)
):
    """Get all documents for a patient."""
    try:
        service = PatientService(db)
        
        patient = await service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check access permissions
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        if current_user.role == "patient" and patient.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        documents = await service.get_patient_documents(patient_id, document_type)
        
        return {"documents": documents}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting documents for patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: str,
    current_user: User = Depends(require_permissions(["patients:delete"])),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete patient record."""
    try:
        service = PatientService(db)
        
        patient = await service.get_patient_by_id(patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Check access permissions
        if current_user.role == "practitioner" and patient.practitioner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this patient"
            )
        
        await service.soft_delete_patient(patient_id)
        
        await service.log_audit(
            user_id=current_user.id,
            action="patient.delete",
            resource_type="patient",
            resource_id=patient_id,
            details={"patient_name": f"{patient.first_name} {patient.last_name}"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete patient"
        )
