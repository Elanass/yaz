"""
Database Models for Surgery Analytics Platform
Cleaned and optimized to match actual database schema
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    Text,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from surgify.core.database import Base


class CaseStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(String(20), default="surgeon")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cases = relationship("Case", back_populates="surgeon")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(20), unique=True, index=True, nullable=False)
    age = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)
    bmi = Column(Float, nullable=True)
    medical_history = Column(
        Text, nullable=True
    )  # Changed from JSON to Text to match DB
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cases = relationship("Case", back_populates="patient")


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    surgeon_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Case details
    procedure_type = Column(String(50), nullable=True)
    diagnosis = Column(String(200), nullable=True)
    status = Column(String(20), default="planned")

    # Scheduling
    scheduled_date = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)

    # Decision support
    risk_score = Column(Float, nullable=True)
    recommendations = Column(
        Text, nullable=True
    )  # Changed from JSON to Text to match DB
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="cases")
    surgeon = relationship("User", back_populates="cases")


class Protocol(Base):
    __tablename__ = "protocols"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=True)
    procedure_type = Column(String(50), nullable=True)
    steps = Column(Text, nullable=True)
    guidelines = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# Additional models for collaborative surgery platform


class CollaborationStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class RegulatoryStatus(str, Enum):
    NOT_SUBMITTED = "not_submitted"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class SurgicalProposal(Base):
    """Hypothetical surgical solutions proposed by surgeons"""

    __tablename__ = "surgical_proposals"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    proposed_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    technique = Column(String(100), nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # minutes

    # Study validation
    study_reference = Column(String(200), nullable=True)
    validation_data = Column(Text, nullable=True)  # JSON as text
    success_rate = Column(Float, nullable=True)

    # Collaboration
    status = Column(String(20), default=CollaborationStatus.DRAFT)

    # Regulatory
    regulatory_status = Column(String(20), default=RegulatoryStatus.NOT_SUBMITTED)
    regulatory_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)


class SurgeonConsent(Base):
    """Surgeon consent and approval records"""

    __tablename__ = "surgeon_consents"

    id = Column(Integer, primary_key=True, index=True)
    proposal_id = Column(Integer, ForeignKey("surgical_proposals.id"), nullable=False)
    surgeon_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    consent_type = Column(String(50), nullable=False)  # "review", "approve", "reject"
    comments = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0

    created_at = Column(DateTime, default=datetime.utcnow)


class StudyResult(Base):
    """Study results and impact analysis data"""

    __tablename__ = "study_results"

    id = Column(Integer, primary_key=True, index=True)
    study_name = Column(String(200), nullable=False)
    study_type = Column(String(50), nullable=False)  # "ADCI", "clinical_trial", etc.

    # Study metadata
    participants = Column(Integer, nullable=True)
    duration_months = Column(Integer, nullable=True)
    methodology = Column(Text, nullable=True)

    # Results
    success_rate = Column(Float, nullable=True)
    complication_rate = Column(Float, nullable=True)
    outcomes_data = Column(Text, nullable=True)  # JSON as text

    # Publication
    published = Column(Boolean, default=False)
    publication_date = Column(DateTime, nullable=True)
    doi = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class CaseCollaboration(Base):
    """Collaboration sessions for surgical cases"""

    __tablename__ = "case_collaborations"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    session_name = Column(String(200), nullable=False)

    # Participants
    primary_surgeon = Column(Integer, ForeignKey("users.id"), nullable=False)
    participants = Column(Text, nullable=True)  # JSON list of surgeon IDs

    # Session details
    scheduled_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="scheduled")  # scheduled, active, completed
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


# Enhanced models for modular API endpoints


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class CaseModel(Base):
    """Enhanced Case model with string IDs and better audit trail"""

    __tablename__ = "enhanced_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(20), unique=True, index=True, nullable=False)
    patient_id = Column(String(50), nullable=False)  # Allow string patient IDs
    surgeon_id = Column(String(50), nullable=True)  # Allow string surgeon IDs

    # Case details
    procedure_type = Column(String(100), nullable=False)
    diagnosis = Column(String(200), nullable=True)
    status = Column(String(20), default="planned")
    priority = Column(String(20), default="medium")

    # Scheduling
    scheduled_date = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)

    # Decision support
    risk_score = Column(Float, nullable=True)
    recommendations = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)


class SyncJobModel(Base):
    """Model for sync job tracking"""

    __tablename__ = "sync_jobs"

    id = Column(String(50), primary_key=True, index=True)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50), nullable=True)
    target_system = Column(String(100), nullable=False)
    status = Column(String(20), default="pending")
    sync_type = Column(String(20), default="full")
    priority = Column(String(20), default="medium")
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    sync_metadata = Column(Text, nullable=True)  # JSON as text

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)


class MessageModel(Base):
    """Model for message management"""

    __tablename__ = "messages"

    id = Column(String(50), primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    sender_id = Column(String(50), nullable=True)
    recipient_id = Column(String(50), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")
    status = Column(String(20), default="unread")
    message_metadata = Column(Text, nullable=True)  # JSON as text

    created_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)


class DeliverableModel(Base):
    """Model for deliverable management"""

    __tablename__ = "deliverables"

    id = Column(String(50), primary_key=True, index=True)
    type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    case_id = Column(Integer, nullable=True)
    format = Column(String(20), nullable=False)
    status = Column(String(20), default="draft")
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)
    deliverable_metadata = Column(Text, nullable=True)  # JSON as text

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(50), nullable=True)
    reviewed_by = Column(String(50), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
