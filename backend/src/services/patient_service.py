"""
Patient service for managing patient operations.
Handles patient CRUD, medical records, and clinical data.
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, update, delete
from sqlalchemy.orm import selectinload
import uuid
import os

from ..db.models import Patient, TreatmentPlan, AuditLog
from ..core.logging import get_logger

logger = get_logger(__name__)

class PatientService:
    """Service class for patient operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> Patient:
        """Create a new patient record."""
        try:
            # Generate patient ID
            patient_data["id"] = uuid.uuid4()
            
            # Set default values
            patient_data.setdefault("status", "active")
            patient_data.setdefault("allergies", [])
            patient_data.setdefault("medications", [])
            patient_data.setdefault("medical_history", {})
            
            patient = Patient(**patient_data)
            self.db.add(patient)
            await self.db.commit()
            await self.db.refresh(patient)
            
            logger.info(f"Created patient: {patient.first_name} {patient.last_name}")
            return patient
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating patient: {str(e)}")
            raise
    
    async def get_patient_by_id(self, patient_id: str) -> Optional[Patient]:
        """Get patient by ID."""
        try:
            result = await self.db.execute(
                select(Patient).where(
                    and_(Patient.id == patient_id, Patient.deleted_at.is_(None))
                ).options(selectinload(Patient.treatment_plans))
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting patient by ID {patient_id}: {str(e)}")
            raise
    
    async def list_patients(
        self,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None,
        practitioner_id: Optional[str] = None
    ) -> Tuple[List[Patient], int]:
        """List patients with filtering and pagination."""
        try:
            query = select(Patient).where(Patient.deleted_at.is_(None))
            
            # Apply filters
            if search:
                search_term = f"%{search}%"
                query = query.where(
                    or_(
                        Patient.first_name.ilike(search_term),
                        Patient.last_name.ilike(search_term),
                        Patient.medical_record_number.ilike(search_term)
                    )
                )
            
            if stage:
                query = query.where(Patient.stage == stage)
            
            if status:
                query = query.where(Patient.status == status)
            
            if practitioner_id:
                query = query.where(Patient.practitioner_id == practitioner_id)
            
            # Get total count
            count_result = await self.db.execute(
                select(func.count()).select_from(query.subquery())
            )
            total = count_result.scalar()
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            query = query.order_by(Patient.created_at.desc())
            
            result = await self.db.execute(query)
            patients = result.scalars().all()
            
            return list(patients), total
        except Exception as e:
            logger.error(f"Error listing patients: {str(e)}")
            raise
    
    async def update_patient(self, patient_id: str, update_data: Dict[str, Any]) -> Patient:
        """Update patient information."""
        try:
            update_data["updated_at"] = datetime.utcnow()
            
            await self.db.execute(
                update(Patient)
                .where(and_(Patient.id == patient_id, Patient.deleted_at.is_(None)))
                .values(**update_data)
            )
            await self.db.commit()
            
            return await self.get_patient_by_id(patient_id)
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating patient {patient_id}: {str(e)}")
            raise
    
    async def update_medical_history(self, patient_id: str, history_data: Dict[str, Any]) -> Patient:
        """Update patient's medical history."""
        try:
            patient = await self.get_patient_by_id(patient_id)
            if not patient:
                raise ValueError("Patient not found")
            
            # Merge with existing medical history
            current_history = patient.medical_history or {}
            current_history.update(history_data)
            
            return await self.update_patient(patient_id, {"medical_history": current_history})
        except Exception as e:
            logger.error(f"Error updating medical history for patient {patient_id}: {str(e)}")
            raise
    
    async def get_patient_treatment_plans(self, patient_id: str) -> List[TreatmentPlan]:
        """Get all treatment plans for a patient."""
        try:
            result = await self.db.execute(
                select(TreatmentPlan)
                .where(and_(
                    TreatmentPlan.patient_id == patient_id,
                    TreatmentPlan.deleted_at.is_(None)
                ))
                .order_by(TreatmentPlan.created_at.desc())
            )
            return list(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting treatment plans for patient {patient_id}: {str(e)}")
            raise
    
    async def upload_patient_document(
        self,
        patient_id: str,
        file,
        document_type: str,
        description: Optional[str] = None,
        uploaded_by: str = None
    ) -> Dict[str, Any]:
        """Upload and store a patient document."""
        try:
            # Create uploads directory if it doesn't exist
            upload_dir = f"uploads/patients/{patient_id}"
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)
            
            # Create document record
            document_data = {
                "id": uuid.uuid4(),
                "patient_id": patient_id,
                "document_type": document_type,
                "filename": file.filename,
                "file_path": file_path,
                "file_size": file.size,
                "mime_type": file.content_type,
                "description": description,
                "uploaded_by": uploaded_by,
                "uploaded_at": datetime.utcnow()
            }
            
            # For now, just return the document data
            # In a full implementation, you'd save this to a documents table
            logger.info(f"Document uploaded for patient {patient_id}: {file.filename}")
            return document_data
            
        except Exception as e:
            logger.error(f"Error uploading document for patient {patient_id}: {str(e)}")
            raise
    
    async def get_patient_documents(
        self,
        patient_id: str,
        document_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get all documents for a patient."""
        try:
            # Mock implementation - in reality, query from documents table
            documents = []
            upload_dir = f"uploads/patients/{patient_id}"
            
            if os.path.exists(upload_dir):
                for filename in os.listdir(upload_dir):
                    if document_type is None or document_type in filename:
                        file_path = os.path.join(upload_dir, filename)
                        stat = os.stat(file_path)
                        documents.append({
                            "id": str(uuid.uuid4()),
                            "patient_id": patient_id,
                            "filename": filename,
                            "file_path": file_path,
                            "file_size": stat.st_size,
                            "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            return documents
        except Exception as e:
            logger.error(f"Error getting documents for patient {patient_id}: {str(e)}")
            raise
    
    async def soft_delete_patient(self, patient_id: str) -> None:
        """Soft delete patient."""
        try:
            await self.db.execute(
                update(Patient)
                .where(and_(Patient.id == patient_id, Patient.deleted_at.is_(None)))
                .values(
                    deleted_at=datetime.utcnow(),
                    status="inactive"
                )
            )
            await self.db.commit()
            
            logger.info(f"Soft deleted patient: {patient_id}")
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error soft deleting patient {patient_id}: {str(e)}")
            raise
    
    async def log_audit(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Log audit event."""
        try:
            audit_log = AuditLog(
                id=uuid.uuid4(),
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                timestamp=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            # Don't raise - audit logging should not break the main flow
