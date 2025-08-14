"""Core Models Package - Modular model definitions."""

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
    "ApiResponse",
    # Base models
    "BaseEntity",
    "ClinicalDecision",
    "ClinicalUserRole",
    "ConfidenceLevel",
    "DecisionStatus",
    "Domain",
    "HealthStatus",
    "MetastasisStatus",
    "NodalStatus",
    "PaginationMeta",
    "PaginationParams",
    "PatientInfo",
    "PatientPerformanceStatus",
    "ProcessingStatus",
    "Scope",
    "TNMClassification",
    # Medical models
    "TumorStage",
    "UserRole",
]
