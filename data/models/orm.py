"""
SQLAlchemy ORM Models
Database schema for gastric oncology decision support platform
"""

from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, 
    Integer, JSON, String, Text, UUID, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
import uuid

from data.database import Base
from data.models import (
    GenderType, BloodType, ComorbidityType, TumorHistology, TumorLocation,
    SurgicalProcedure, TreatmentProtocol, DecisionStatus, ConfidenceLevel
)
from core.models.medical import (
    TumorStage, NodalStatus, MetastasisStatus, PatientPerformanceStatus
)


class PatientORM(Base):
    """Patient table for storing patient information"""
    
    __tablename__ = "patients"
    
    # Primary key
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Identifiers
    medical_record_number = Column(String(50), unique=True, nullable=False, index=True)
    external_id = Column(String(100), nullable=True, index=True)
    
    # Demographics
    age = Column(Integer, nullable=False)
    gender = Column(Enum(GenderType), nullable=False)
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    blood_type = Column(Enum(BloodType), nullable=True)
    ethnicity = Column(String(100), nullable=True)
    
    # Medical history (stored as JSON for flexibility)
    family_history = Column(JSON, nullable=True, default={})
    social_history = Column(JSON, nullable=True, default={})
    previous_treatments = Column(JSON, nullable=True, default=[])
    current_medications = Column(JSON, nullable=True, default=[])
    
    # Consent and privacy
    consent_research = Column(Boolean, default=False, nullable=False)
    privacy_level = Column(String(20), default="standard", nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    # Relationships
    comorbidities = relationship("ComorbidityORM", back_populates="patient", cascade="all, delete-orphan")
    tumor_characteristics = relationship("TumorCharacteristicsORM", back_populates="patient", uselist=False)
    performance_status = relationship("PerformanceStatusORM", back_populates="patient", uselist=False)
    laboratory_results = relationship("LaboratoryResultsORM", back_populates="patient", cascade="all, delete-orphan")
    treatment_plans = relationship("TreatmentPlanORM", back_populates="patient", cascade="all, delete-orphan")
    adci_decisions = relationship("ADCIDecisionORM", back_populates="patient", cascade="all, delete-orphan")
    clinical_outcomes = relationship("ClinicalOutcomeORM", back_populates="patient", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('ix_patients_mrn_gender', 'medical_record_number', 'gender'),
        Index('ix_patients_age_gender', 'age', 'gender'),
    )


class ComorbidityORM(Base):
    """Comorbidity table for patient comorbidities"""
    
    __tablename__ = "comorbidities"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    type = Column(Enum(ComorbidityType), nullable=False)
    severity = Column(String(50), nullable=False)
    diagnosed_date = Column(DateTime, nullable=True)
    controlled = Column(Boolean, default=False, nullable=False)
    medications = Column(JSON, nullable=True, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="comorbidities")
    
    # Indexes
    __table_args__ = (
        Index('ix_comorbidities_patient_type', 'patient_id', 'type'),
    )


class TumorCharacteristicsORM(Base):
    """Tumor characteristics table"""
    
    __tablename__ = "tumor_characteristics"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Tumor details
    histology = Column(Enum(TumorHistology), nullable=False)
    location = Column(Enum(TumorLocation), nullable=False)
    size_mm = Column(Float, nullable=True)
    differentiation = Column(String(50), nullable=True)
    her2_status = Column(Boolean, nullable=True)
    msi_status = Column(String(50), nullable=True)
    pdl1_expression = Column(Float, nullable=True)
    
    # TNM Staging
    t_stage = Column(Enum(TumorStage), nullable=False)
    n_stage = Column(Enum(NodalStatus), nullable=False)
    m_stage = Column(Enum(MetastasisStatus), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="tumor_characteristics")
    
    # Indexes
    __table_args__ = (
        Index('ix_tumor_histology_location', 'histology', 'location'),
        Index('ix_tumor_tnm_stage', 't_stage', 'n_stage', 'm_stage'),
        UniqueConstraint('patient_id', name='uq_tumor_characteristics_patient'),
    )


class PerformanceStatusORM(Base):
    """Performance status table"""
    
    __tablename__ = "performance_status"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    ecog_status = Column(Enum(PatientPerformanceStatus), nullable=False)
    karnofsky_score = Column(Integer, nullable=True)
    weight_loss_percent = Column(Float, nullable=True)
    nutritional_risk = Column(String(100), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="performance_status")
    
    # Indexes
    __table_args__ = (
        UniqueConstraint('patient_id', name='uq_performance_status_patient'),
    )


class LaboratoryResultsORM(Base):
    """Laboratory results table"""
    
    __tablename__ = "laboratory_results"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Hematology
    hemoglobin_g_dl = Column(Float, nullable=True)
    white_blood_cells = Column(Float, nullable=True)
    platelets = Column(Float, nullable=True)
    
    # Chemistry
    albumin_g_dl = Column(Float, nullable=True)
    total_protein_g_dl = Column(Float, nullable=True)
    creatinine_mg_dl = Column(Float, nullable=True)
    bilirubin_mg_dl = Column(Float, nullable=True)
    
    # Tumor markers
    cea_ng_ml = Column(Float, nullable=True)
    ca19_9_u_ml = Column(Float, nullable=True)
    ca72_4_u_ml = Column(Float, nullable=True)
    
    # Collection info
    collection_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="laboratory_results")
    
    # Indexes
    __table_args__ = (
        Index('ix_lab_results_patient_date', 'patient_id', 'collection_date'),
    )


class TreatmentPlanORM(Base):
    """Treatment plan table"""
    
    __tablename__ = "treatment_plans"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    
    # Treatment details
    protocol = Column(Enum(TreatmentProtocol), nullable=False)
    surgical_procedure = Column(Enum(SurgicalProcedure), nullable=True)
    
    # Scheduling
    planned_start_date = Column(DateTime, nullable=True)
    estimated_duration_weeks = Column(Integer, nullable=True)
    
    # Team
    primary_surgeon = Column(String(100), nullable=True)
    medical_oncologist = Column(String(100), nullable=True)
    multidisciplinary_team = Column(JSON, nullable=True, default=[])
    
    # Goals and notes
    treatment_intent = Column(String(20), nullable=False)
    clinical_notes = Column(Text, nullable=True)
    
    # Status
    status = Column(String(20), default="planned", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="treatment_plans")
    adci_decisions = relationship("ADCIDecisionORM", back_populates="treatment_plan")
    
    # Indexes
    __table_args__ = (
        Index('ix_treatment_plans_patient_protocol', 'patient_id', 'protocol'),
        Index('ix_treatment_plans_start_date', 'planned_start_date'),
    )


class ADCIDecisionORM(Base):
    """ADCI decision support results table"""
    
    __tablename__ = "adci_decisions"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    treatment_plan_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("treatment_plans.id"), nullable=True)
    
    # Decision inputs
    input_parameters = Column(JSON, nullable=False)
    
    # ADCI outputs
    adci_score = Column(Float, nullable=False)
    confidence_level = Column(Enum(ConfidenceLevel), nullable=False)
    
    # Recommendations
    recommended_protocol = Column(Enum(TreatmentProtocol), nullable=False)
    alternative_protocols = Column(JSON, nullable=True, default=[])
    
    # Supporting data
    evidence_quality = Column(String(20), nullable=False)
    risk_factors = Column(JSON, nullable=True, default=[])
    contraindications = Column(JSON, nullable=True, default=[])
    
    # Decision metadata
    decision_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    decision_maker = Column(String(100), nullable=False)
    status = Column(Enum(DecisionStatus), default=DecisionStatus.PENDING, nullable=False)
    
    # Outcome tracking
    implemented = Column(Boolean, default=False, nullable=False)
    outcome_notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="adci_decisions")
    treatment_plan = relationship("TreatmentPlanORM", back_populates="adci_decisions")
    
    # Indexes
    __table_args__ = (
        Index('ix_adci_decisions_patient_score', 'patient_id', 'adci_score'),
        Index('ix_adci_decisions_timestamp', 'decision_timestamp'),
        Index('ix_adci_decisions_maker', 'decision_maker'),
    )


class ClinicalOutcomeORM(Base):
    """Clinical outcome tracking table"""
    
    __tablename__ = "clinical_outcomes"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    adci_decision_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("adci_decisions.id"), nullable=True)
    
    # Outcome measures
    overall_survival_months = Column(Float, nullable=True)
    disease_free_survival_months = Column(Float, nullable=True)
    progression_free_survival_months = Column(Float, nullable=True)
    
    # Quality of life
    quality_of_life_score = Column(Float, nullable=True)
    functional_status_change = Column(String(50), nullable=True)
    
    # Complications
    complications = Column(JSON, nullable=True, default=[])
    adverse_events = Column(JSON, nullable=True, default=[])
    
    # Follow-up
    last_follow_up_date = Column(DateTime, nullable=True)
    follow_up_status = Column(String(20), default="active", nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("PatientORM", back_populates="clinical_outcomes")
    
    # Indexes
    __table_args__ = (
        Index('ix_clinical_outcomes_patient_followup', 'patient_id', 'last_follow_up_date'),
        Index('ix_clinical_outcomes_survival', 'overall_survival_months'),
    )


class AuditLogORM(Base):
    """Audit log table for HIPAA compliance"""
    
    __tablename__ = "audit_logs"
    
    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Audit details
    entity_type = Column(String(50), nullable=False)  # patient, decision, etc.
    entity_id = Column(PostgreSQLUUID(as_uuid=True), nullable=True)
    action = Column(String(20), nullable=False)  # create, read, update, delete
    user_id = Column(String(100), nullable=False)
    user_role = Column(String(50), nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(100), nullable=True)
    
    # Data changes
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    
    # Compliance
    reason = Column(String(200), nullable=True)
    consent_verified = Column(Boolean, default=False, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Indexes for audit queries
    __table_args__ = (
        Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_logs_user_timestamp', 'user_id', 'timestamp'),
        Index('ix_audit_logs_action_timestamp', 'action', 'timestamp'),
    )
