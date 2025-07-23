"""
Database models for Gastric ADCI Platform
ElectricsQL-compatible schema design
"""

import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey, Enum, DECIMAL, Index
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
import enum

from .database import Base


class UserRole(str, enum.Enum):
    """User roles for RBAC"""
    PATIENT = "patient"
    PRACTITIONER = "practitioner" 
    RESEARCHER = "researcher"
    ADMIN = "admin"


class TreatmentStatus(str, enum.Enum):
    """Treatment status enumeration"""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    SUSPENDED = "suspended"
    DISCONTINUED = "discontinued"


class ConfidenceLevel(str, enum.Enum):
    """Confidence levels for decision engine"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class AuditAction(str, enum.Enum):
    """Audit action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    EXPORT = "export"


class CohortUploadFormat(str, enum.Enum):
    """Supported cohort upload formats"""
    CSV = "csv"
    JSON = "json"
    FHIR_BUNDLE = "fhir_bundle"
    MANUAL = "manual"


class CohortStatus(str, enum.Enum):
    """Cohort processing status"""
    DRAFT = "draft"
    VALIDATING = "validating"
    VALIDATED = "validated"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InferenceStatus(str, enum.Enum):
    """Inference session status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Base model with common fields
class BaseModel(Base):
    """Base model with common audit fields"""
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # ElectricsQL sync fields
    _electric_sync_id = Column(UUID(as_uuid=True), default=uuid.uuid4)
    _electric_sync_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    _electric_sync_version = Column(Integer, default=1)
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class User(BaseModel):
    """User model with RBAC support"""
    __tablename__ = "users"
    
    # Basic info
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    
    # Role and permissions
    role = Column(Enum(UserRole), nullable=False, default=UserRole.PATIENT)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Professional info (for practitioners/researchers)
    license_number = Column(String(100), nullable=True)
    institution = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    specialization = Column(String(255), nullable=True)
    
    # Contact info
    phone = Column(String(20), nullable=True)
    emergency_contact = Column(JSON, nullable=True)
    
    # Security
    last_login = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy settings
    data_sharing_consent = Column(Boolean, default=False, nullable=False)
    research_participation = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    patients = relationship("Patient", back_populates="practitioner", foreign_keys="Patient.practitioner_id")
    created_protocols = relationship("ClinicalProtocol", back_populates="creator")
    audit_logs = relationship("AuditLog", back_populates="user")
    webauthn_credentials = relationship("WebAuthnCredential", back_populates="user")
    oidc_mappings = relationship("OIDCUserMapping", back_populates="user")
    webauthn_credentials = relationship("WebAuthnCredential", back_populates="user")
    oidc_mappings = relationship("OIDCUserMapping", back_populates="user")
    pwa_subscriptions = relationship("PWASubscription", back_populates="user", cascade="all, delete-orphan")
    background_sync_jobs = relationship("BackgroundSyncJob", back_populates="user", cascade="all, delete-orphan")
    pwa_install_events = relationship("PWAInstallEvent", back_populates="user", cascade="all, delete-orphan")
    pwa_notification_logs = relationship("PWANotificationLog", back_populates="user", cascade="all, delete-orphan")
    pwa_performance_metrics = relationship("PWAPerformanceMetric", back_populates="user", cascade="all, delete-orphan")


class Patient(BaseModel):
    """Patient model with clinical data"""
    __tablename__ = "patients"
    
    # Demographics
    patient_id = Column(String(50), unique=True, index=True, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(20), nullable=False)
    
    # Contact (encrypted)
    contact_info = Column(Text, nullable=True)  # Encrypted JSON
    
    # Clinical info
    primary_diagnosis = Column(String(255), nullable=True)
    diagnosis_date = Column(DateTime, nullable=True)
    stage = Column(String(50), nullable=True)
    grade = Column(String(50), nullable=True)
    
    # Biomarkers and genetics
    biomarkers = Column(JSON, nullable=True)
    genetic_profile = Column(JSON, nullable=True)
    
    # Performance status
    ecog_score = Column(Integer, nullable=True)
    karnofsky_score = Column(Integer, nullable=True)
    
    # Medical history
    medical_history = Column(JSON, nullable=True)
    family_history = Column(JSON, nullable=True)
    allergies = Column(ARRAY(String), nullable=True)
    current_medications = Column(JSON, nullable=True)
    
    # Treatment team
    practitioner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    care_team = Column(JSON, nullable=True)
    
    # Relationships
    practitioner = relationship("User", back_populates="patients", foreign_keys=[practitioner_id])
    treatment_plans = relationship("TreatmentPlan", back_populates="patient")
    decision_results = relationship("DecisionResult", back_populates="patient")
    evidence_records = relationship("EvidenceRecord", back_populates="patient")


class ClinicalProtocol(BaseModel):
    """Clinical protocols and guidelines"""
    __tablename__ = "clinical_protocols"
    
    # Protocol info
    name = Column(String(255), nullable=False)
    version = Column(String(20), nullable=False)
    description = Column(Text, nullable=True)
    
    # Protocol type
    protocol_type = Column(String(50), nullable=False)  # ADCI, Gastrectomy, FLOT, etc.
    indication = Column(String(255), nullable=False)
    
    # Clinical criteria
    inclusion_criteria = Column(JSON, nullable=False)
    exclusion_criteria = Column(JSON, nullable=False)
    
    # Protocol content
    steps = Column(JSON, nullable=False)
    parameters = Column(JSON, nullable=False)
    decision_tree = Column(JSON, nullable=True)
    
    # Evidence level
    evidence_level = Column(String(10), nullable=False)
    guideline_source = Column(String(255), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    is_experimental = Column(Boolean, default=False, nullable=False)
    
    # Approval and validation
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    next_review_date = Column(DateTime, nullable=True)
    
    # Relationships
    creator = relationship("User", back_populates="created_protocols", foreign_keys=[approved_by])
    treatment_plans = relationship("TreatmentPlan", back_populates="protocol")


class TreatmentPlan(BaseModel):
    """Individual treatment plans"""
    __tablename__ = "treatment_plans"
    
    # Plan info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Patient and protocol
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    protocol_id = Column(UUID(as_uuid=True), ForeignKey("clinical_protocols.id"), nullable=False)
    
    # Plan details
    treatment_intent = Column(String(100), nullable=False)  # curative, palliative, adjuvant, etc.
    planned_duration_weeks = Column(Integer, nullable=True)
    
    # Schedule
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(Enum(TreatmentStatus), default=TreatmentStatus.PLANNING, nullable=False)
    
    # Treatment components
    surgical_plan = Column(JSON, nullable=True)
    chemotherapy_plan = Column(JSON, nullable=True)
    radiation_plan = Column(JSON, nullable=True)
    supportive_care = Column(JSON, nullable=True)
    
    # Monitoring
    response_criteria = Column(JSON, nullable=True)
    toxicity_monitoring = Column(JSON, nullable=True)
    quality_of_life_metrics = Column(JSON, nullable=True)
    
    # Outcomes
    actual_duration_weeks = Column(Integer, nullable=True)
    completion_status = Column(String(100), nullable=True)
    response_assessment = Column(JSON, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="treatment_plans")
    protocol = relationship("ClinicalProtocol", back_populates="treatment_plans")
    decision_results = relationship("DecisionResult", back_populates="treatment_plan")


class DecisionResult(BaseModel):
    """Results from decision engines"""
    __tablename__ = "decision_results"
    
    # Engine info
    engine_name = Column(String(100), nullable=False)  # ADCI, Gastrectomy, FLOT
    engine_version = Column(String(20), nullable=False)
    
    # Input and context
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    treatment_plan_id = Column(UUID(as_uuid=True), ForeignKey("treatment_plans.id"), nullable=True)
    
    input_parameters = Column(JSON, nullable=False)
    clinical_context = Column(JSON, nullable=True)
    
    # Results
    recommendation = Column(JSON, nullable=False)
    confidence_score = Column(DECIMAL(5, 4), nullable=False)  # 0.0000 to 1.0000
    confidence_level = Column(Enum(ConfidenceLevel), nullable=False)
    
    # Evidence and reasoning
    evidence_summary = Column(JSON, nullable=True)
    reasoning_chain = Column(JSON, nullable=True)
    alternative_options = Column(JSON, nullable=True)
    
    # Risk assessment
    risk_factors = Column(JSON, nullable=True)
    contraindications = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    
    # Quality metrics
    data_completeness = Column(DECIMAL(5, 4), nullable=True)
    uncertainty_factors = Column(JSON, nullable=True)
    
    # Follow-up
    monitoring_recommendations = Column(JSON, nullable=True)
    reassessment_timeline = Column(JSON, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="decision_results")
    treatment_plan = relationship("TreatmentPlan", back_populates="decision_results")


class EvidenceRecord(BaseModel):
    """Evidence records for research and validation"""
    __tablename__ = "evidence_records"
    
    # Evidence info
    title = Column(String(500), nullable=False)
    evidence_type = Column(String(100), nullable=False)  # trial, study, case_report, etc.
    source = Column(String(255), nullable=False)
    
    # Publication info
    authors = Column(ARRAY(String), nullable=True)
    publication_date = Column(DateTime, nullable=True)
    journal = Column(String(255), nullable=True)
    doi = Column(String(255), nullable=True)
    pubmed_id = Column(String(50), nullable=True)
    
    # Clinical relevance
    indication = Column(String(255), nullable=False)
    patient_population = Column(JSON, nullable=True)
    intervention = Column(JSON, nullable=False)
    outcomes = Column(JSON, nullable=False)
    
    # Quality assessment
    evidence_level = Column(String(10), nullable=False)
    study_quality = Column(String(20), nullable=True)
    bias_assessment = Column(JSON, nullable=True)
    
    # Data
    sample_size = Column(Integer, nullable=True)
    follow_up_duration = Column(Integer, nullable=True)  # months
    statistical_significance = Column(JSON, nullable=True)
    
    # Association with patients/treatments
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=True)
    applicable_protocols = Column(ARRAY(String), nullable=True)
    
    # IPFS storage
    ipfs_hash = Column(String(255), nullable=True)
    ipfs_metadata = Column(JSON, nullable=True)
    
    # Relationships
    patient = relationship("Patient", back_populates="evidence_records")


class AuditSeverity(str, enum.Enum):
    """Audit event severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditEventType(str, enum.Enum):
    """Extended audit event types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout" 
    USER_FAILED_LOGIN = "user_failed_login"
    DATA_ACCESS = "data_access"
    DATA_CREATE = "data_create"
    DATA_UPDATE = "data_update"
    DATA_DELETE = "data_delete"
    DATA_EXPORT = "data_export"
    DECISION_CREATE = "decision_create"
    DECISION_APPROVE = "decision_approve"
    PROTOCOL_CREATE = "protocol_create"
    PROTOCOL_UPDATE = "protocol_update"
    PROTOCOL_FORK = "protocol_fork"
    EVIDENCE_CREATE = "evidence_create"
    EVIDENCE_UPDATE = "evidence_update"
    SYSTEM_CONFIG = "system_config"
    PERMISSION_CHANGE = "permission_change"
    EMERGENCY_ACCESS = "emergency_access"


class AuditLog(BaseModel):
    """Advanced audit log for HIPAA/GDPR compliance with tamper-proof features"""
    __tablename__ = "audit_logs"
    
    # Override id to use integer for better performance
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Who
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user_role = Column(String(50), nullable=True)
    session_id = Column(String(255), nullable=True)
    
    # What - Enhanced event tracking
    event_type = Column(Enum(AuditEventType), nullable=False)
    action = Column(String(100), nullable=False)  # Specific action taken
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    
    # When and Where
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Details - Enhanced context
    details = Column(JSON, nullable=True)  # Structured event details
    context = Column(JSON, nullable=True)  # Additional context (department, etc.)
    
    # Legacy fields for compatibility
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    additional_data = Column(JSON, nullable=True)
    
    # Privacy and security - Enhanced
    severity = Column(Enum(AuditSeverity), nullable=False, default=AuditSeverity.MEDIUM)
    data_sensitivity = Column(String(20), nullable=False, default="normal")
    phi_accessed = Column(Boolean, default=False, nullable=False)
    
    # Tamper-proof features
    hash = Column(String(64), nullable=False, index=True)  # SHA-256 hash for integrity
    previous_hash = Column(String(64), nullable=True)  # Link to previous event
    
    # Compliance tracking
    retention_until = Column(DateTime(timezone=True), nullable=True)  # For data retention policies
    compliance_tags = Column(ARRAY(String), nullable=True)  # HIPAA, GDPR, etc.
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")


class SystemConfiguration(BaseModel):
    """System configuration settings"""
    __tablename__ = "system_configurations"
    
    # Configuration
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=False)
    data_type = Column(String(50), nullable=False)  # string, integer, boolean, json
    is_sensitive = Column(Boolean, default=False, nullable=False)
    
    # Validation
    validation_rules = Column(JSON, nullable=True)
    default_value = Column(JSON, nullable=True)
    
    # Access control
    required_role = Column(String(50), nullable=False, default="admin")
    
    @validates('value')
    def validate_value(self, key, value):
        """Validate configuration value"""
        # Add validation logic based on data_type and validation_rules
        return value


class EvidenceLog(BaseModel):
    """Tamper-proof evidence storage with IPFS integration"""
    __tablename__ = "evidence_logs"
    
    # Evidence identification
    evidence_id = Column(String(255), unique=True, index=True, nullable=False)
    evidence_type = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    
    # Tamper-proof verification
    content_hash = Column(String(64), nullable=False)  # SHA-256 hash
    ipfs_hash = Column(String(100), nullable=False)  # IPFS content hash
    file_ipfs_hash = Column(String(100), nullable=True)  # File attachment IPFS hash
    digital_signature = Column(Text, nullable=False)  # Cryptographic signature
    
    # Metadata and classification
    metadata = Column(JSON, nullable=True)
    source = Column(String(255), nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    clinical_context = Column(JSON, nullable=True)
    
    # Verification status
    verification_status = Column(String(50), nullable=False, default="verified")
    verification_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional blockchain integration
    blockchain_tx_hash = Column(String(100), nullable=True)
    blockchain_network = Column(String(50), nullable=True)
    
    # Access control
    access_level = Column(String(50), nullable=False, default="internal")
    sharing_permissions = Column(JSON, nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[BaseModel.created_by])


class WebAuthnCredential(BaseModel):
    """WebAuthn/FIDO2 credentials for passwordless authentication"""
    __tablename__ = "webauthn_credentials"
    
    # Foreign key to user
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # WebAuthn credential data
    credential_id = Column(String(1024), unique=True, nullable=False, index=True)
    public_key = Column(Text, nullable=False)  # Base64 encoded public key
    sign_count = Column(Integer, nullable=False, default=0)
    aaguid = Column(String(36), nullable=True)  # Authenticator AAGUID
    
    # Credential metadata
    credential_name = Column(String(255), nullable=False)
    authenticator_type = Column(String(50), nullable=False)  # platform, cross-platform, hybrid
    status = Column(String(20), nullable=False, default="active")  # active, revoked, expired, compromised
    
    # Usage tracking
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, nullable=False, default=0)
    
    # Security tracking
    created_from_ip = Column(String(45), nullable=True)
    created_from_user_agent = Column(Text, nullable=True)
    
    # Revocation info
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(String(255), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="webauthn_credentials")


class OIDCProvider(BaseModel):
    """OIDC identity provider configuration"""
    __tablename__ = "oidc_providers"
    
    # Provider identification
    provider_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    issuer = Column(String(500), nullable=False)
    
    # Client configuration
    client_id = Column(String(255), nullable=False)
    client_secret = Column(Text, nullable=False)  # Encrypted
    scopes = Column(ARRAY(String), nullable=False, default=["openid", "profile", "email"])
    
    # Endpoints (discovered automatically if not set)
    authorization_endpoint = Column(String(500), nullable=True)
    token_endpoint = Column(String(500), nullable=True)
    userinfo_endpoint = Column(String(500), nullable=True)
    jwks_uri = Column(String(500), nullable=True)
    
    # Attribute mapping
    username_claim = Column(String(100), nullable=False, default="preferred_username")
    email_claim = Column(String(100), nullable=False, default="email")
    first_name_claim = Column(String(100), nullable=False, default="given_name")
    last_name_claim = Column(String(100), nullable=False, default="family_name")
    
    # Security settings
    verify_ssl = Column(Boolean, nullable=False, default=True)
    require_https = Column(Boolean, nullable=False, default=True)
    token_validation = Column(Boolean, nullable=False, default=True)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    auto_create_users = Column(Boolean, nullable=False, default=False)
    
    # Relationships
    user_mappings = relationship("OIDCUserMapping", back_populates="provider")


class OIDCUserMapping(BaseModel):
    """Mapping between local users and OIDC provider identities"""
    __tablename__ = "oidc_user_mappings"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider_id = Column(String(100), nullable=False, index=True)
    
    # Provider-specific identity
    provider_subject = Column(String(255), nullable=False)  # OIDC 'sub' claim
    provider_email = Column(String(255), nullable=True)
    provider_username = Column(String(255), nullable=True)
    
    # Claims storage
    provider_claims = Column(JSON, nullable=True)  # Latest claims from provider
    
    # Metadata
    first_login = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), server_default=func.now())
    login_count = Column(Integer, nullable=False, default=1)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Unique constraint on provider + subject
    __table_args__ = (
        Index('ix_oidc_provider_subject', 'provider_id', 'provider_subject', unique=True),
    )
    
    # Relationships
    user = relationship("User", back_populates="oidc_mappings")
    provider = relationship("OIDCProvider", back_populates="user_mappings")


class PWASubscription(BaseModel):
    """PWA push notification subscriptions"""
    __tablename__ = "pwa_subscriptions"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Encrypted subscription data
    encrypted_endpoint = Column(Text, nullable=False)  # Encrypted push endpoint
    encrypted_keys = Column(Text, nullable=False)  # Encrypted VAPID keys
    endpoint_hash = Column(String(64), nullable=False, index=True)  # For duplicate detection
    
    # Status and metadata
    is_active = Column(Boolean, nullable=False, default=True)
    browser_info = Column(JSON, nullable=True)  # Browser/device information
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint on user + endpoint hash
    __table_args__ = (
        Index('ix_pwa_user_endpoint', 'user_id', 'endpoint_hash', unique=True),
    )
    
    # Relationships
    user = relationship("User", back_populates="pwa_subscriptions")


class BackgroundSyncJob(BaseModel):
    """Background sync jobs for PWA offline functionality"""
    __tablename__ = "background_sync_jobs"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Job configuration
    job_type = Column(String(100), nullable=False, index=True)
    encrypted_data = Column(Text, nullable=True)  # Encrypted job payload
    priority = Column(Integer, nullable=False, default=5)  # 1-10 scale
    max_retries = Column(Integer, nullable=False, default=3)
    
    # Job status
    status = Column(String(50), nullable=False, default='pending', index=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    
    # Indexes for efficient querying
    __table_args__ = (
        Index('ix_sync_jobs_status_priority', 'status', 'priority'),
        Index('ix_sync_jobs_user_type', 'user_id', 'job_type'),
        Index('ix_sync_jobs_scheduled', 'scheduled_at'),
    )
    
    # Relationships
    user = relationship("User", back_populates="background_sync_jobs")


class PWAInstallEvent(BaseModel):
    """PWA installation events for analytics"""
    __tablename__ = "pwa_install_events"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Event details
    event_type = Column(String(50), nullable=False)  # prompted, accepted, dismissed, installed
    platform = Column(String(100), nullable=False)  # iOS, Android, Desktop, etc.
    user_agent = Column(Text, nullable=False)
    referrer = Column(String(255), nullable=True)
    
    # Device information
    screen_width = Column(Integer, nullable=True)
    screen_height = Column(Integer, nullable=True)
    device_memory = Column(Float, nullable=True)
    connection_type = Column(String(50), nullable=True)
    
    # Geographic data (if available)
    country_code = Column(String(2), nullable=True)
    timezone = Column(String(50), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('ix_pwa_events_user_type', 'user_id', 'event_type'),
        Index('ix_pwa_events_platform', 'platform'),
        Index('ix_pwa_events_created', 'created_at'),
    )
    
    # Relationships
    user = relationship("User", back_populates="pwa_install_events")


class PWANotificationLog(BaseModel):
    """Log of PWA push notifications sent"""
    __tablename__ = "pwa_notification_logs"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("pwa_subscriptions.id"), nullable=True)
    
    # Notification details
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    tag = Column(String(100), nullable=True, index=True)
    urgency_level = Column(Integer, nullable=False, default=1)  # 1-5 scale
    
    # Delivery status
    delivery_status = Column(String(50), nullable=False, default='sent')  # sent, delivered, failed, clicked
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error tracking
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Clinical context
    case_id = Column(UUID(as_uuid=True), nullable=True)
    patient_id = Column(UUID(as_uuid=True), nullable=True)
    protocol_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Metadata
    notification_data = Column(JSON, nullable=True)  # Custom notification payload
    
    # Indexes
    __table_args__ = (
        Index('ix_notification_user_status', 'user_id', 'delivery_status'),
        Index('ix_notification_tag', 'tag'),
        Index('ix_notification_urgency', 'urgency_level'),
        Index('ix_notification_clinical', 'case_id', 'patient_id'),
    )
    
    # Relationships
    user = relationship("User", back_populates="pwa_notification_logs")
    subscription = relationship("PWASubscription")


class PWAPerformanceMetric(BaseModel):
    """PWA performance metrics for monitoring"""
    __tablename__ = "pwa_performance_metrics"
    
    # Foreign key
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Performance metrics
    load_time_ms = Column(Integer, nullable=False)
    cache_hit_ratio = Column(Float, nullable=False, default=0.0)
    offline_time_seconds = Column(Integer, nullable=False, default=0)
    sync_success_rate = Column(Float, nullable=False, default=1.0)
    
    # User engagement
    session_duration_minutes = Column(Integer, nullable=False, default=0)
    pages_visited = Column(Integer, nullable=False, default=1)
    actions_performed = Column(Integer, nullable=False, default=0)
    
    # Technical details
    browser_version = Column(String(100), nullable=True)
    platform_version = Column(String(100), nullable=True)
    network_type = Column(String(50), nullable=True)  # wifi, cellular, ethernet
    memory_usage_mb = Column(Float, nullable=True)
    
    # Geographic and temporal context
    country_code = Column(String(2), nullable=True)
    hour_of_day = Column(Integer, nullable=True)  # 0-23
    day_of_week = Column(Integer, nullable=True)  # 1-7
    
    # Indexes
    __table_args__ = (
        Index('ix_performance_user_date', 'user_id', 'created_at'),
        Index('ix_performance_load_time', 'load_time_ms'),
        Index('ix_performance_cache_ratio', 'cache_hit_ratio'),
    )
    
    # Relationships
    user = relationship("User", back_populates="pwa_performance_metrics")


class CohortStudy(BaseModel):
    """Cohort study for batch processing and analysis"""
    __tablename__ = "cohort_studies"
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    study_type = Column(String(100), nullable=False, default="gastric_cancer")
    
    # Upload metadata
    upload_format = Column(Enum(CohortUploadFormat), nullable=False)
    original_filename = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA-256 hash
    
    # IPFS storage
    ipfs_hash = Column(String(100), nullable=True)  # Raw data IPFS hash
    processed_ipfs_hash = Column(String(100), nullable=True)  # Processed results hash
    
    # Status and validation
    status = Column(Enum(CohortStatus), nullable=False, default=CohortStatus.DRAFT)
    validation_errors = Column(JSON, nullable=True)
    validation_warnings = Column(JSON, nullable=True)
    
    # Patient count and statistics
    total_patients = Column(Integer, nullable=False, default=0)
    valid_patients = Column(Integer, nullable=False, default=0)
    invalid_patients = Column(Integer, nullable=False, default=0)
    
    # Processing metadata
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration_seconds = Column(Float, nullable=True)
    
    # Data compliance and privacy
    contains_phi = Column(Boolean, nullable=False, default=True)
    anonymization_level = Column(String(50), nullable=False, default="identified")
    consent_status = Column(String(50), nullable=False, default="required")
    
    # Relationships
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[created_by])
    cohort_patients = relationship("CohortPatient", back_populates="cohort_study")
    inference_sessions = relationship("InferenceSession", back_populates="cohort_study")
    export_tasks = relationship("CohortExportTask", back_populates="cohort_study")


class CohortPatient(BaseModel):
    """Individual patient record within a cohort study"""
    __tablename__ = "cohort_patients"
    
    # Foreign key to cohort
    cohort_study_id = Column(UUID(as_uuid=True), ForeignKey("cohort_studies.id"), nullable=False)
    
    # Patient identification (anonymized)
    patient_identifier = Column(String(100), nullable=False)  # Study-specific ID
    external_patient_id = Column(String(100), nullable=True)  # Original system ID
    
    # Demographics
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    ethnicity = Column(String(100), nullable=True)
    
    # Clinical baseline data
    primary_diagnosis = Column(String(255), nullable=True)
    tumor_stage = Column(String(50), nullable=True)  # TNM staging
    tumor_grade = Column(String(50), nullable=True)
    tumor_location = Column(String(100), nullable=True)
    
    # Performance status
    ecog_score = Column(Integer, nullable=True)
    karnofsky_score = Column(Integer, nullable=True)
    
    # Biomarkers and molecular data
    biomarkers = Column(JSON, nullable=True)  # HER2, MSI, PD-L1, etc.
    genetic_mutations = Column(JSON, nullable=True)
    
    # Treatment history
    prior_treatments = Column(JSON, nullable=True)
    current_medications = Column(JSON, nullable=True)
    comorbidities = Column(JSON, nullable=True)
    
    # Lab values and measurements
    lab_values = Column(JSON, nullable=True)  # CBC, chemistry panel, etc.
    vital_signs = Column(JSON, nullable=True)
    
    # Data quality and validation
    is_valid = Column(Boolean, nullable=False, default=True)
    validation_errors = Column(JSON, nullable=True)
    data_completeness_score = Column(Float, nullable=True)  # 0.0 to 1.0
    
    # Source information
    data_source = Column(String(100), nullable=True)
    import_row_number = Column(Integer, nullable=True)
    
    # Relationships
    cohort_study = relationship("CohortStudy", back_populates="cohort_patients")
    decision_results = relationship("PatientDecisionResult", back_populates="cohort_patient")


class InferenceSession(BaseModel):
    """Batch processing session for cohort analysis"""
    __tablename__ = "inference_sessions"
    
    # Foreign key to cohort
    cohort_study_id = Column(UUID(as_uuid=True), ForeignKey("cohort_studies.id"), nullable=False)
    
    # Session metadata
    session_name = Column(String(255), nullable=False)
    session_description = Column(Text, nullable=True)
    
    # Processing configuration
    decision_engines = Column(ARRAY(String), nullable=False)  # ["adci", "gastrectomy", "flot"]
    processing_parameters = Column(JSON, nullable=True)
    
    # Status and timing
    status = Column(Enum(InferenceStatus), nullable=False, default=InferenceStatus.PENDING)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Progress tracking
    total_patients = Column(Integer, nullable=False, default=0)
    processed_patients = Column(Integer, nullable=False, default=0)
    failed_patients = Column(Integer, nullable=False, default=0)
    progress_percentage = Column(Float, nullable=False, default=0.0)
    
    # Results summary
    results_summary = Column(JSON, nullable=True)
    error_log = Column(JSON, nullable=True)
    
    # IPFS storage for results
    results_ipfs_hash = Column(String(100), nullable=True)
    
    # Version control
    version = Column(Integer, nullable=False, default=1)
    parent_session_id = Column(UUID(as_uuid=True), ForeignKey("inference_sessions.id"), nullable=True)
    
    # Relationships
    cohort_study = relationship("CohortStudy", back_populates="inference_sessions")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[created_by])
    patient_results = relationship("PatientDecisionResult", back_populates="inference_session")
    parent_session = relationship("InferenceSession", remote_side="InferenceSession.id")


class PatientDecisionResult(BaseModel):
    """Individual patient decision engine results"""
    __tablename__ = "patient_decision_results"
    
    # Foreign keys
    cohort_patient_id = Column(UUID(as_uuid=True), ForeignKey("cohort_patients.id"), nullable=False)
    inference_session_id = Column(UUID(as_uuid=True), ForeignKey("inference_sessions.id"), nullable=False)
    
    # Decision engine results
    adci_score = Column(Float, nullable=True)
    adci_confidence = Column(Float, nullable=True)
    adci_recommendation = Column(String(255), nullable=True)
    
    gastrectomy_recommendation = Column(String(255), nullable=True)
    gastrectomy_confidence = Column(Float, nullable=True)
    gastrectomy_risk_factors = Column(JSON, nullable=True)
    
    flot_eligibility = Column(Boolean, nullable=True)
    flot_recommendation = Column(String(255), nullable=True)
    flot_confidence = Column(Float, nullable=True)
    
    # Overall recommendation
    primary_recommendation = Column(String(255), nullable=True)
    recommendation_confidence = Column(Float, nullable=True)
    treatment_pathway = Column(String(255), nullable=True)
    
    # Risk assessment
    surgical_risk_score = Column(Float, nullable=True)
    mortality_risk = Column(Float, nullable=True)
    complication_risk = Column(Float, nullable=True)
    
    # Evidence and explanations
    decision_factors = Column(JSON, nullable=True)  # Contributing factors
    evidence_links = Column(JSON, nullable=True)    # Supporting evidence
    contraindications = Column(JSON, nullable=True) # Risk factors
    
    # Processing metadata
    processing_time_ms = Column(Float, nullable=True)
    engine_versions = Column(JSON, nullable=True)
    
    # Data quality
    input_completeness = Column(Float, nullable=True)
    result_reliability = Column(Float, nullable=True)
    
    # Relationships
    cohort_patient = relationship("CohortPatient", back_populates="decision_results")
    inference_session = relationship("InferenceSession", back_populates="patient_results")


class CohortExportTask(BaseModel):
    """Export tasks for cohort results and deliverables"""
    __tablename__ = "cohort_export_tasks"
    
    # Foreign key to cohort
    cohort_study_id = Column(UUID(as_uuid=True), ForeignKey("cohort_studies.id"), nullable=False)
    inference_session_id = Column(UUID(as_uuid=True), ForeignKey("inference_sessions.id"), nullable=True)
    
    # Export configuration
    export_format = Column(String(50), nullable=False)  # csv, pdf, fhir, json
    export_type = Column(String(100), nullable=False)   # full_results, summary, report
    export_parameters = Column(JSON, nullable=True)
    
    # File information
    filename = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    file_path = Column(String(1000), nullable=True)
    download_url = Column(String(1000), nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="pending")
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, nullable=False, default=0)
    
    # Security and access
    download_token = Column(String(255), nullable=True)
    access_count = Column(Integer, nullable=False, default=0)
    last_accessed = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    cohort_study = relationship("CohortStudy", back_populates="export_tasks")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[created_by])


class CohortHypothesis(BaseModel):
    """Hypothesis and what-if scenarios for cohort analysis"""
    __tablename__ = "cohort_hypotheses"
    
    # Foreign key to cohort or inference session
    cohort_study_id = Column(UUID(as_uuid=True), ForeignKey("cohort_studies.id"), nullable=False)
    base_inference_session_id = Column(UUID(as_uuid=True), ForeignKey("inference_sessions.id"), nullable=True)
    
    # Hypothesis definition
    hypothesis_name = Column(String(255), nullable=False)
    hypothesis_description = Column(Text, nullable=True)
    hypothesis_type = Column(String(100), nullable=False)  # parameter_change, subset_analysis, etc.
    
    # Parameter modifications
    parameter_changes = Column(JSON, nullable=False)  # What parameters to modify
    patient_filters = Column(JSON, nullable=True)     # Which patients to include
    
    # Results
    results_data = Column(JSON, nullable=True)
    comparison_summary = Column(JSON, nullable=True)
    statistical_significance = Column(Float, nullable=True)
    
    # Status
    status = Column(String(50), nullable=False, default="draft")
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    creator = relationship("User", foreign_keys=[created_by])
