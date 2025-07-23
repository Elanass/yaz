"""
Patient schemas for API request/response models.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, validator
from enum import Enum

class PatientStage(str, Enum):
    """Patient cancer stage enumeration."""
    STAGE_0 = "0"
    STAGE_I = "I"
    STAGE_II = "II"
    STAGE_III = "III"
    STAGE_IV = "IV"
    UNKNOWN = "unknown"

class PatientStatus(str, Enum):
    """Patient treatment status enumeration."""
    ACTIVE = "active"
    MONITORING = "monitoring"
    TREATMENT = "treatment"
    REMISSION = "remission"
    PALLIATIVE = "palliative"
    DECEASED = "deceased"

class TreatmentStatus(str, Enum):
    """Treatment plan status enumeration."""
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class PatientBase(BaseModel):
    """Base patient model."""
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    medical_record_number: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None

class PatientCreate(PatientBase):
    """Patient creation model."""
    user_id: Optional[str] = None  # Link to User account if patient has login
    practitioner_id: Optional[str] = None
    diagnosis_date: Optional[date] = None
    stage: Optional[PatientStage] = None
    status: PatientStatus = PatientStatus.ACTIVE
    medical_history: Optional[Dict[str, Any]] = None
    allergies: Optional[List[str]] = []
    medications: Optional[List[Dict[str, Any]]] = []

class PatientUpdate(BaseModel):
    """Patient update model."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    medical_record_number: Optional[str] = None
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None
    stage: Optional[PatientStage] = None
    status: Optional[PatientStatus] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[Dict[str, Any]]] = None

class MedicalHistoryUpdate(BaseModel):
    """Medical history update model."""
    family_history: Optional[Dict[str, Any]] = None
    past_surgeries: Optional[List[Dict[str, Any]]] = None
    chronic_conditions: Optional[List[str]] = None
    social_history: Optional[Dict[str, Any]] = None
    review_of_systems: Optional[Dict[str, Any]] = None

class PatientResponse(BaseModel):
    """Patient response model."""
    id: str
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    medical_record_number: Optional[str] = None
    user_id: Optional[str] = None
    practitioner_id: Optional[str] = None
    diagnosis_date: Optional[date] = None
    stage: Optional[PatientStage] = None
    status: PatientStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PatientDetailResponse(PatientResponse):
    """Detailed patient response model."""
    emergency_contact: Optional[Dict[str, Any]] = None
    insurance_info: Optional[Dict[str, Any]] = None
    medical_history: Optional[Dict[str, Any]] = None
    allergies: List[str] = []
    medications: List[Dict[str, Any]] = []
    
    # Related data
    practitioner_name: Optional[str] = None
    total_treatment_plans: int = 0
    last_visit_date: Optional[date] = None

class PatientList(BaseModel):
    """Patient list response model."""
    patients: List[PatientResponse]
    total: int
    skip: int
    limit: int

class TreatmentPlanBase(BaseModel):
    """Base treatment plan model."""
    name: str
    protocol_id: str
    start_date: date
    estimated_end_date: Optional[date] = None
    status: TreatmentStatus = TreatmentStatus.PLANNED
    goals: Optional[List[str]] = []
    notes: Optional[str] = None

class TreatmentPlanCreate(TreatmentPlanBase):
    """Treatment plan creation model."""
    patient_id: str
    created_by: str
    treatment_details: Optional[Dict[str, Any]] = None
    decision_factors: Optional[Dict[str, Any]] = None

class TreatmentPlanUpdate(BaseModel):
    """Treatment plan update model."""
    name: Optional[str] = None
    start_date: Optional[date] = None
    estimated_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: Optional[TreatmentStatus] = None
    goals: Optional[List[str]] = None
    notes: Optional[str] = None
    treatment_details: Optional[Dict[str, Any]] = None
    outcomes: Optional[Dict[str, Any]] = None

class TreatmentPlanResponse(BaseModel):
    """Treatment plan response model."""
    id: str
    name: str
    protocol_id: str
    protocol_name: Optional[str] = None
    patient_id: str
    start_date: date
    estimated_end_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    status: TreatmentStatus
    goals: List[str] = []
    notes: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class PatientDocumentBase(BaseModel):
    """Base patient document model."""
    document_type: str
    filename: str
    file_size: int
    mime_type: str
    description: Optional[str] = None

class PatientDocumentResponse(PatientDocumentBase):
    """Patient document response model."""
    id: str
    patient_id: str
    file_path: str
    uploaded_by: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True

class PatientSearchFilters(BaseModel):
    """Patient search filters."""
    search: Optional[str] = None
    stage: Optional[PatientStage] = None
    status: Optional[PatientStatus] = None
    practitioner_id: Optional[str] = None
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    diagnosis_date_from: Optional[date] = None
    diagnosis_date_to: Optional[date] = None
