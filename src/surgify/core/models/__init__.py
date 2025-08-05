"""
Core Models Package - Modular model definitions
"""

# Base models - generic, reusable
from .base import (
    ApiResponse,
    BaseEntity,
    ConfidenceLevel,
    Domain,
    HealthStatus,
    PaginationMeta,
    PaginationParams,
    ProcessingStatus,
    Scope,
    UserRole,
)

# Medical models - domain-specific for gastric cancer ADCI
from .medical import (
    ClinicalDecision,
    ClinicalUserRole,
    DecisionStatus,
    MetastasisStatus,
    NodalStatus,
    PatientInfo,
    PatientPerformanceStatus,
    TNMClassification,
    TumorStage,
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
    "ClinicalDecision",
]
