"""
Evidence Storage Pydantic Schemas
Data models for tamper-proof evidence logging
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum

class EvidenceType(str, Enum):
    """Types of clinical evidence"""
    CLINICAL_STUDY = "clinical_study"
    RESEARCH_PAPER = "research_paper"
    CASE_REPORT = "case_report"
    DIAGNOSTIC_IMAGE = "diagnostic_image"
    LAB_RESULT = "lab_result"
    PATHOLOGY_REPORT = "pathology_report"
    SURGICAL_NOTE = "surgical_note"
    TREATMENT_PROTOCOL = "treatment_protocol"
    PATIENT_OUTCOME = "patient_outcome"
    ADVERSE_EVENT = "adverse_event"
    DRUG_INTERACTION = "drug_interaction"
    BIOMARKER_DATA = "biomarker_data"
    GENOMIC_DATA = "genomic_data"
    CLINICAL_TRIAL = "clinical_trial"
    GUIDELINE = "guideline"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    EXPERT_OPINION = "expert_opinion"

class EvidenceQuality(str, Enum):
    """Evidence quality levels"""
    GRADE_A = "grade_a"  # High quality
    GRADE_B = "grade_b"  # Moderate quality
    GRADE_C = "grade_c"  # Low quality
    GRADE_D = "grade_d"  # Very low quality
    UNGRADED = "ungraded"

class EvidenceStatus(str, Enum):
    """Evidence status"""
    DRAFT = "draft"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class StudyDesign(str, Enum):
    """Clinical study design types"""
    RANDOMIZED_CONTROLLED_TRIAL = "rct"
    COHORT_STUDY = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    CASE_SERIES = "case_series"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    NARRATIVE_REVIEW = "narrative_review"
    EXPERT_OPINION = "expert_opinion"

class EvidenceMetadata(BaseModel):
    """Comprehensive evidence metadata"""
    
    # Quality and reliability
    evidence_quality: EvidenceQuality = EvidenceQuality.UNGRADED
    confidence_level: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score 0-1")
    peer_reviewed: bool = False
    
    # Publication details
    authors: Optional[List[str]] = Field(None, description="List of authors")
    institution: Optional[str] = Field(None, description="Institution or organization")
    publication_date: Optional[datetime] = Field(None, description="Publication date")
    journal: Optional[str] = Field(None, description="Journal or publication venue")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    pmid: Optional[str] = Field(None, description="PubMed ID")
    
    # Study characteristics
    study_design: Optional[StudyDesign] = Field(None, description="Study design type")
    sample_size: Optional[int] = Field(None, ge=0, description="Number of participants")
    population: Optional[str] = Field(None, description="Study population description")
    intervention: Optional[str] = Field(None, description="Intervention or treatment")
    outcome_measures: Optional[List[str]] = Field(None, description="Primary/secondary outcomes")
    
    # Clinical relevance
    indication: Optional[str] = Field(None, description="Clinical indication")
    cancer_type: Optional[str] = Field(None, description="Specific cancer type")
    cancer_stage: Optional[str] = Field(None, description="Cancer stage")
    treatment_line: Optional[str] = Field(None, description="Line of treatment")
    
    # Geographic and temporal context
    country: Optional[str] = Field(None, description="Country of study")
    study_period: Optional[Dict[str, datetime]] = Field(None, description="Study start/end dates")
    
    # Links and references
    related_evidence: Optional[List[str]] = Field(None, description="Related evidence IDs")
    external_links: Optional[List[str]] = Field(None, description="External resource links")
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence_quality": "grade_a",
                "confidence_level": 0.85,
                "peer_reviewed": True,
                "authors": ["Smith J", "Johnson A", "Brown M"],
                "institution": "Mayo Clinic",
                "publication_date": "2024-01-15T00:00:00Z",
                "journal": "Journal of Clinical Oncology",
                "doi": "10.1200/JCO.2024.123456",
                "pmid": "38123456",
                "study_design": "rct",
                "sample_size": 500,
                "population": "Advanced gastric cancer patients",
                "intervention": "FLOT chemotherapy",
                "outcome_measures": ["Overall survival", "Progression-free survival"],
                "indication": "Perioperative treatment",
                "cancer_type": "gastric adenocarcinoma",
                "cancer_stage": "Stage II-III",
                "treatment_line": "First-line",
                "country": "USA"
            }
        }

class EvidenceCreate(BaseModel):
    """Schema for creating new evidence"""
    evidence_type: EvidenceType
    title: str = Field(..., min_length=5, max_length=500, description="Evidence title")
    description: str = Field(..., min_length=10, description="Detailed description")
    content: Optional[Union[str, Dict]] = Field(None, description="Evidence content")
    metadata: EvidenceMetadata
    source: str = Field(..., description="Source of evidence")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    clinical_context: Dict[str, Any] = Field(default_factory=dict, description="Clinical context")
    
    @validator('tags')
    def validate_tags(cls, v):
        """Validate and normalize tags"""
        if len(v) > 20:
            raise ValueError("Maximum 20 tags allowed")
        return [tag.lower().strip() for tag in v if tag.strip()]
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title"""
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence_type": "clinical_study",
                "title": "FLOT vs ECF/ECX in Gastric Cancer: Phase III Trial",
                "description": "Randomized phase III trial comparing FLOT with ECF/ECX as perioperative treatment in patients with resectable gastric or gastroesophageal junction adenocarcinoma",
                "content": {
                    "primary_endpoint": "Overall survival",
                    "secondary_endpoints": ["Progression-free survival", "R0 resection rate"],
                    "results": {
                        "median_os": "50 months vs 35 months",
                        "hazard_ratio": 0.77,
                        "p_value": 0.012
                    }
                },
                "source": "Al-Batran et al. Lancet 2019",
                "tags": ["flot", "gastric cancer", "perioperative", "chemotherapy"],
                "clinical_context": {
                    "protocol_id": "PROT_001",
                    "decision_point": "treatment_selection"
                }
            }
        }

class EvidenceResponse(BaseModel):
    """Schema for evidence response"""
    evidence_id: str
    evidence_type: str
    title: str
    description: str
    metadata: EvidenceMetadata
    source: str
    tags: List[str]
    clinical_context: Dict[str, Any]
    created_by: Optional[int]
    created_at: datetime
    verification_status: str
    ipfs_hash: str
    content_hash: str
    has_file: bool = False
    
    class Config:
        from_attributes = True

class EvidenceDetailResponse(EvidenceResponse):
    """Schema for detailed evidence response with content"""
    content: Optional[Union[str, Dict]]
    digital_signature: str
    verification: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence_id": "EVD_20240115103000_a1b2c3d4",
                "evidence_type": "clinical_study",
                "title": "FLOT vs ECF/ECX in Gastric Cancer",
                "description": "Phase III randomized trial...",
                "content": {"primary_endpoint": "Overall survival"},
                "verification": {
                    "signature_valid": True,
                    "hash_valid": True,
                    "ipfs_hash": "QmX1Y2Z3...",
                    "content_hash": "a1b2c3d4e5f6...",
                    "timestamp": "2024-01-15T10:30:00Z"
                },
                "verification_status": "verified",
                "has_file": False
            }
        }

class EvidenceSearchRequest(BaseModel):
    """Schema for evidence search requests"""
    query: Optional[str] = Field(None, min_length=3, description="Search query")
    evidence_type: Optional[EvidenceType] = Field(None, description="Filter by evidence type")
    evidence_quality: Optional[EvidenceQuality] = Field(None, description="Filter by quality")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    created_by: Optional[int] = Field(None, description="Filter by creator")
    start_date: Optional[datetime] = Field(None, description="Filter by creation date")
    end_date: Optional[datetime] = Field(None, description="Filter by creation date")
    cancer_type: Optional[str] = Field(None, description="Filter by cancer type")
    indication: Optional[str] = Field(None, description="Filter by clinical indication")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str = Field("created_at", description="Sort field")
    sort_order: str = Field("desc", regex="^(asc|desc)$", description="Sort order")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "FLOT chemotherapy",
                "evidence_type": "clinical_study",
                "evidence_quality": "grade_a",
                "tags": ["gastric cancer", "perioperative"],
                "cancer_type": "gastric adenocarcinoma",
                "indication": "perioperative treatment",
                "page": 1,
                "per_page": 20,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }

class EvidenceSearchResponse(BaseModel):
    """Schema for evidence search results"""
    evidence: List[EvidenceResponse]
    pagination: Dict[str, int]
    search_metadata: Dict[str, Any]
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence": [],
                "pagination": {
                    "page": 1,
                    "per_page": 20,
                    "total": 45,
                    "total_pages": 3
                },
                "search_metadata": {
                    "query": "FLOT chemotherapy",
                    "filters_applied": ["evidence_type", "tags"],
                    "search_time_ms": 150
                }
            }
        }

class EvidenceVerificationRequest(BaseModel):
    """Schema for evidence verification requests"""
    evidence_ids: List[str] = Field(..., min_items=1, max_items=100)
    
    class Config:
        json_schema_extra = {
            "example": {
                "evidence_ids": [
                    "EVD_20240115103000_a1b2c3d4",
                    "EVD_20240115104500_e5f6g7h8"
                ]
            }
        }

class EvidenceVerificationResponse(BaseModel):
    """Schema for evidence verification results"""
    overall_valid: bool
    total_evidence: int
    valid_count: int
    verification_results: List[Dict[str, Any]]
    verification_timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "overall_valid": True,
                "total_evidence": 2,
                "valid_count": 2,
                "verification_results": [
                    {
                        "evidence_id": "EVD_20240115103000_a1b2c3d4",
                        "is_valid": True,
                        "signature_valid": True,
                        "hash_valid": True,
                        "ipfs_hash": "QmX1Y2Z3..."
                    }
                ],
                "verification_timestamp": "2024-01-15T10:30:00Z"
            }
        }

class EvidenceStatsResponse(BaseModel):
    """Schema for evidence statistics"""
    total_evidence: int
    evidence_by_type: Dict[str, int]
    evidence_by_quality: Dict[str, int]
    evidence_by_month: Dict[str, int]
    top_tags: List[Dict[str, Union[str, int]]]
    verification_status: Dict[str, int]
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_evidence": 150,
                "evidence_by_type": {
                    "clinical_study": 45,
                    "research_paper": 60,
                    "case_report": 25,
                    "guideline": 20
                },
                "evidence_by_quality": {
                    "grade_a": 50,
                    "grade_b": 70,
                    "grade_c": 20,
                    "ungraded": 10
                },
                "evidence_by_month": {
                    "2024-01": 25,
                    "2024-02": 30,
                    "2024-03": 35
                },
                "top_tags": [
                    {"tag": "gastric cancer", "count": 80},
                    {"tag": "chemotherapy", "count": 65}
                ],
                "verification_status": {
                    "verified": 145,
                    "pending": 3,
                    "failed": 2
                }
            }
        }

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    filename: str
    file_size: int
    content_type: str
    ipfs_hash: str
    upload_timestamp: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "filename": "clinical_study.pdf",
                "file_size": 2048576,
                "content_type": "application/pdf",
                "ipfs_hash": "QmX1Y2Z3...",
                "upload_timestamp": "2024-01-15T10:30:00Z"
            }
        }
