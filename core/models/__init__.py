"""
Core Models Package - Modular model definitions
"""

# Base models - generic, reusable
from .base import (
    BaseEntity,
    ApiResponse,
    PaginationParams,
    PaginationMeta,
    HealthStatus,
    ProcessingStatus,
    ConfidenceLevel,
    UserRole,
    Domain,
    Scope
)

# Medical models - domain-specific for gastric cancer ADCI
from .medical import (
    TumorStage,
    NodalStatus,
    MetastasisStatus,
    PatientPerformanceStatus,
    ClinicalUserRole,
    DecisionStatus,
    TNMClassification,
    PatientInfo,
    ClinicalDecision
)

__all__ = [
    # Base models
    "BaseEntity",
    "ApiResponse",
    "PaginationParams", 
    "PaginationMeta",
    "HealthStatus",
    "ProcessingStatus",
    "ConfidenceLevel",
    "UserRole",
    "Domain",
    "Scope",
    
    # Medical models
    "TumorStage",
    "NodalStatus", 
    "MetastasisStatus",
    "PatientPerformanceStatus",
    "ClinicalUserRole",
    "DecisionStatus",
    "TNMClassification",
    "PatientInfo",
    "ClinicalDecision"
]
