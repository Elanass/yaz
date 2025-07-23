"""
Protocol schemas for API request/response models.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel, validator
from enum import Enum

class ProtocolCategory(str, Enum):
    """Protocol category enumeration."""
    SURGICAL = "surgical"
    CHEMOTHERAPY = "chemotherapy"
    RADIATION = "radiation"
    IMMUNOTHERAPY = "immunotherapy"
    TARGETED_THERAPY = "targeted_therapy"
    PALLIATIVE = "palliative"
    DIAGNOSTIC = "diagnostic"
    MONITORING = "monitoring"

class ProtocolStatus(str, Enum):
    """Protocol status enumeration."""
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"

class EvidenceLevel(str, Enum):
    """Evidence level enumeration."""
    LEVEL_1 = "1"  # High-quality RCT or meta-analysis
    LEVEL_2 = "2"  # Lower-quality RCT or high-quality cohort
    LEVEL_3 = "3"  # Case-control or cohort studies
    LEVEL_4 = "4"  # Case series or expert opinion
    LEVEL_5 = "5"  # Expert opinion only

class ProtocolBase(BaseModel):
    """Base protocol model."""
    name: str
    category: ProtocolCategory
    description: str
    version: str = "1.0"
    applicable_stages: List[str] = []
    inclusion_criteria: List[str] = []
    exclusion_criteria: List[str] = []
    evidence_level: EvidenceLevel
    guidelines_source: Optional[str] = None

class ProtocolCreate(ProtocolBase):
    """Protocol creation model."""
    decision_tree: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    outcomes_tracking: Optional[Dict[str, Any]] = None
    references: Optional[List[Dict[str, Any]]] = []
    status: ProtocolStatus = ProtocolStatus.DRAFT

class ProtocolUpdate(BaseModel):
    """Protocol update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    applicable_stages: Optional[List[str]] = None
    inclusion_criteria: Optional[List[str]] = None
    exclusion_criteria: Optional[List[str]] = None
    evidence_level: Optional[EvidenceLevel] = None
    guidelines_source: Optional[str] = None
    decision_tree: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    outcomes_tracking: Optional[Dict[str, Any]] = None
    references: Optional[List[Dict[str, Any]]] = None

class ProtocolResponse(BaseModel):
    """Protocol response model."""
    id: str
    name: str
    category: ProtocolCategory
    description: str
    version: str
    status: ProtocolStatus
    applicable_stages: List[str] = []
    evidence_level: EvidenceLevel
    guidelines_source: Optional[str] = None
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProtocolDetailResponse(ProtocolResponse):
    """Detailed protocol response model."""
    inclusion_criteria: List[str] = []
    exclusion_criteria: List[str] = []
    decision_tree: Optional[Dict[str, Any]] = None
    parameters: Optional[Dict[str, Any]] = None
    outcomes_tracking: Optional[Dict[str, Any]] = None
    references: List[Dict[str, Any]] = []
    
    # Statistics
    total_patients_treated: int = 0
    success_rate: Optional[float] = None
    average_outcome_score: Optional[float] = None
    last_used_date: Optional[datetime] = None

class ProtocolList(BaseModel):
    """Protocol list response model."""
    protocols: List[ProtocolResponse]
    total: int
    skip: int
    limit: int

class ProtocolVersionBase(BaseModel):
    """Base protocol version model."""
    version: str
    changes: str
    change_reason: str

class ProtocolVersionCreate(ProtocolVersionBase):
    """Protocol version creation model."""
    protocol_data: Dict[str, Any]

class ProtocolVersionResponse(BaseModel):
    """Protocol version response model."""
    id: str
    protocol_id: str
    version: str
    changes: str
    change_reason: str
    created_by: str
    created_at: datetime
    is_current: bool = False
    
    class Config:
        from_attributes = True

class DecisionNodeBase(BaseModel):
    """Base decision node model."""
    node_id: str
    node_type: str  # "condition", "action", "decision"
    title: str
    description: Optional[str] = None
    conditions: Optional[Dict[str, Any]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    next_nodes: Optional[List[str]] = None

class DecisionTreeBase(BaseModel):
    """Base decision tree model."""
    name: str
    version: str = "1.0"
    description: Optional[str] = None
    root_node_id: str
    nodes: List[DecisionNodeBase]

class ProtocolSearchFilters(BaseModel):
    """Protocol search filters."""
    search: Optional[str] = None
    category: Optional[ProtocolCategory] = None
    status: Optional[ProtocolStatus] = None
    stage: Optional[str] = None
    evidence_level: Optional[EvidenceLevel] = None
    created_by: Optional[str] = None

class ProtocolStatistics(BaseModel):
    """Protocol statistics model."""
    total_protocols: int
    by_category: Dict[str, int]
    by_status: Dict[str, int]
    by_evidence_level: Dict[str, int]
    recently_updated: List[ProtocolResponse]
    most_used: List[ProtocolResponse]

class ProtocolUsageMetrics(BaseModel):
    """Protocol usage metrics model."""
    protocol_id: str
    total_uses: int
    success_rate: float
    average_confidence: float
    patient_outcomes: Dict[str, Any]
    usage_trends: List[Dict[str, Any]]
    comparative_effectiveness: Optional[Dict[str, Any]] = None
