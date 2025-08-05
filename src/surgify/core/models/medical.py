"""
Medical Models - Gastric cancer ADCI specific medical classifications
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

from .base import BaseEntity, ProcessingStatus, ConfidenceLevel


# Medical/Clinical Specific Enums
class TumorStage(str, Enum):
    """TNM Tumor classification"""

    T1A = "T1a"
    T1B = "T1b"
    T2 = "T2"
    T3 = "T3"
    T4A = "T4a"
    T4B = "T4b"


class NodalStatus(str, Enum):
    """TNM Nodal status classification"""

    N0 = "N0"
    N1 = "N1"
    N2 = "N2"
    N3 = "N3"


class MetastasisStatus(str, Enum):
    """TNM Metastasis status classification"""

    M0 = "M0"
    M1 = "M1"


class PatientPerformanceStatus(str, Enum):
    """Patient performance status (ECOG scale)"""

    NORMAL = "normal"  # ECOG 0
    RESTRICTED = "restricted"  # ECOG 1
    AMBULATORY = "ambulatory"  # ECOG 2
    SYMPTOMATIC = "symptomatic"  # ECOG 3
    BEDRIDDEN = "bedridden"  # ECOG 4


class ClinicalUserRole(str, Enum):
    """Medical-specific user roles"""

    PATIENT = "patient"
    CLINICIAN = "clinician"
    SURGEON = "surgeon"
    ONCOLOGIST = "oncologist"
    PATHOLOGIST = "pathologist"
    RESEARCHER = "researcher"
    RADIOLOGIST = "radiologist"


class DecisionStatus(str, Enum):
    """Medical decision processing status"""

    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REQUIRES_CONSULTATION = "requires_consultation"
    FAILED = "failed"


# Medical Models
class TNMClassification(BaseModel):
    """TNM staging classification"""

    tumor_stage: TumorStage
    nodal_status: NodalStatus
    metastasis_status: MetastasisStatus
    overall_stage: Optional[str] = None

    class Config:
        from_attributes = True


class PatientInfo(BaseEntity):
    """Patient information model"""

    patient_id: str
    age: Optional[int] = None
    gender: Optional[str] = None
    performance_status: Optional[PatientPerformanceStatus] = None
    medical_history: Optional[dict] = None

    class Config:
        from_attributes = True


class ClinicalDecision(BaseEntity):
    """Clinical decision model"""

    patient_id: str
    decision_type: str
    status: DecisionStatus = DecisionStatus.PENDING
    confidence: Optional[ConfidenceLevel] = None
    recommendations: Optional[dict] = None
    reasoning: Optional[str] = None
    reviewed_by: Optional[str] = None

    class Config:
        from_attributes = True
