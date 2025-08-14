"""SQLAlchemy ORM Models
Database schema for gastric oncology decision support platform.
"""

# Fix import paths for enums
import sys
import uuid
from datetime import datetime
from pathlib import Path


root_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_path))

try:
    from data.models import (
        BloodType,
        ComorbidityType,
        ConfidenceLevel,
        DecisionStatus,
        GenderType,
        SurgicalProcedure,
        TreatmentProtocol,
        TumorHistology,
        TumorLocation,
    )
except ImportError:
    # Create minimal enums if import fails
    from enum import Enum

    class GenderType(str, Enum):
        MALE = "male"
        FEMALE = "female"
        OTHER = "other"

    class BloodType(str, Enum):
        A_POS = "A+"
        B_POS = "B+"
        O_POS = "O+"
        AB_POS = "AB+"

    class ComorbidityType(str, Enum):
        DIABETES = "diabetes"
        HYPERTENSION = "hypertension"
        OTHER = "other"

    class ConfidenceLevel(str, Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    class DecisionStatus(str, Enum):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    class SurgicalProcedure(str, Enum):
        APPENDECTOMY = "appendectomy"
        LAPAROSCOPY = "laparoscopy"
        OTHER = "other"

    class TreatmentProtocol(str, Enum):
        STANDARD = "standard"
        EXPERIMENTAL = "experimental"
        PALLIATIVE = "palliative"

    class TumorHistology(str, Enum):
        ADENOCARCINOMA = "adenocarcinoma"
        SQUAMOUS = "squamous"
        OTHER = "other"

    class TumorLocation(str, Enum):
        STOMACH = "stomach"
        ESOPHAGUS = "esophagus"
        COLON = "colon"
        OTHER = "other"


from sqlalchemy import (
    JSON,
    UUID,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship


try:
    from core.models.medical import (
        MetastasisStatus,
        NodalStatus,
        PatientPerformanceStatus,
        TumorStage,
    )
except ImportError:
    # Fallback enums if core.models is not available
    from enum import Enum

    class MetastasisStatus(Enum):
        M0 = "M0"
        M1 = "M1"

    class NodalStatus(Enum):
        N0 = "N0"
        N1 = "N1"
        N2 = "N2"
        N3 = "N3"

    class PatientPerformanceStatus(Enum):
        ECOG_0 = "ECOG_0"
        ECOG_1 = "ECOG_1"
        ECOG_2 = "ECOG_2"
        ECOG_3 = "ECOG_3"
        ECOG_4 = "ECOG_4"

    class TumorStage(Enum):
        T1 = "T1"
        T2 = "T2"
        T3 = "T3"
        T4 = "T4"


from data.database import Base


class TenantORM(Base):
    __tablename__ = "tenants"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    studies = relationship(
        "StudyORM", back_populates="tenant", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("ix_tenants_name", "name"),)


class StudyORM(Base):
    __tablename__ = "studies"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    state = Column(
        String(30), default="draft", nullable=False
    )  # lifecycle: draft, active, archived
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tenant = relationship("TenantORM", back_populates="studies")
    subjects = relationship(
        "SubjectORM", back_populates="study", cascade="all, delete-orphan"
    )
    cases = relationship(
        "CaseORM", back_populates="study", cascade="all, delete-orphan"
    )
    deliverables = relationship(
        "DeliverableORM", back_populates="study", cascade="all, delete-orphan"
    )
    feedbacks = relationship(
        "FeedbackORM", back_populates="study", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("ix_studies_tenant_name", "tenant_id", "name"),)


class SubjectORM(Base):
    __tablename__ = "subjects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(UUID(as_uuid=True), ForeignKey("studies.id"), nullable=False)
    external_id = Column(String(100), nullable=True, index=True)
    name = Column(String(100), nullable=True)
    dob = Column(DateTime, nullable=True)
    sex = Column(String(10), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    study = relationship("StudyORM", back_populates="subjects")
    cases = relationship(
        "CaseORM", back_populates="subject", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("ix_subjects_study_external", "study_id", "external_id"),)


class CaseORM(Base):
    __tablename__ = "cases"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(UUID(as_uuid=True), ForeignKey("studies.id"), nullable=False)
    subject_id = Column(UUID(as_uuid=True), ForeignKey("subjects.id"), nullable=False)
    specimen_id = Column(String(100), nullable=True, index=True)
    state = Column(
        String(30), default="new", nullable=False
    )  # lifecycle: new, processing, complete, archived
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    study = relationship("StudyORM", back_populates="cases")
    subject = relationship("SubjectORM", back_populates="cases")
    deliverables = relationship(
        "DeliverableORM", back_populates="case", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("ix_cases_study_subject", "study_id", "subject_id"),)


class DeliverableORM(Base):
    __tablename__ = "deliverables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(UUID(as_uuid=True), ForeignKey("studies.id"), nullable=False)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=True)
    audience = Column(
        String(30), nullable=False
    )  # academic, community, enterprise, practitioner
    template = Column(String(50), nullable=False)
    content = Column(JSON, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    study = relationship("StudyORM", back_populates="deliverables")
    case = relationship("CaseORM", back_populates="deliverables")
    feedbacks = relationship(
        "FeedbackORM", back_populates="deliverable", cascade="all, delete-orphan"
    )
    __table_args__ = (Index("ix_deliverables_study_audience", "study_id", "audience"),)


class FeedbackORM(Base):
    __tablename__ = "feedbacks"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    study_id = Column(UUID(as_uuid=True), ForeignKey("studies.id"), nullable=False)
    deliverable_id = Column(
        UUID(as_uuid=True), ForeignKey("deliverables.id"), nullable=False
    )
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)
    submitted_by = Column(String(100), nullable=True)
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    study = relationship("StudyORM", back_populates="feedbacks")
    deliverable = relationship("DeliverableORM", back_populates="feedbacks")
    __table_args__ = (
        Index("ix_feedbacks_study_deliverable", "study_id", "deliverable_id"),
    )


class PatientORM(Base):
    """Patient table for storing patient information."""

    __tablename__ = "patients"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Identifiers
    medical_record_number = Column(String(50), unique=True, nullable=False, index=True)
    external_id = Column(String(100), nullable=True, index=True)

    # Demographics
    age = Column(Integer, nullable=False)
    gender = Column(
        SAEnum(
            GenderType, name="gender_type", native_enum=False, validate_strings=True
        ),
        nullable=False,
    )  # Restored from String with proper enum syntax
    weight_kg = Column(Float, nullable=True)
    height_cm = Column(Float, nullable=True)
    blood_type = Column(
        SAEnum(BloodType, name="blood_type", native_enum=False, validate_strings=True),
        nullable=True,
    )  # Restored from String with proper enum syntax
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
    comorbidities = relationship(
        "ComorbidityORM", back_populates="patient", cascade="all, delete-orphan"
    )
    tumor_characteristics = relationship(
        "TumorCharacteristicsORM", back_populates="patient", uselist=False
    )
    performance_status = relationship(
        "PerformanceStatusORM", back_populates="patient", uselist=False
    )
    laboratory_results = relationship(
        "LaboratoryResultsORM", back_populates="patient", cascade="all, delete-orphan"
    )
    treatment_plans = relationship(
        "TreatmentPlanORM", back_populates="patient", cascade="all, delete-orphan"
    )
    adci_decisions = relationship(
        "ADCIDecisionORM", back_populates="patient", cascade="all, delete-orphan"
    )
    clinical_outcomes = relationship(
        "ClinicalOutcomeORM", back_populates="patient", cascade="all, delete-orphan"
    )

    # Indexes for performance
    __table_args__ = (
        Index("ix_patients_mrn_gender", "medical_record_number", "gender"),
        Index("ix_patients_age_gender", "age", "gender"),
    )


class ComorbidityORM(Base):
    """Comorbidity table for patient comorbidities."""

    __tablename__ = "comorbidities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    type = Column(
        SAEnum(
            ComorbidityType,
            name="comorbidity_type",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )  # Restored from String with proper enum syntax
    severity = Column(String(50), nullable=False)
    diagnosed_date = Column(DateTime, nullable=True)
    controlled = Column(Boolean, default=False, nullable=False)
    medications = Column(JSON, nullable=True, default=[])

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("PatientORM", back_populates="comorbidities")

    # Indexes
    __table_args__ = (Index("ix_comorbidities_patient_type", "patient_id", "type"),)


class TumorCharacteristicsORM(Base):
    """Tumor characteristics table."""

    __tablename__ = "tumor_characteristics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    # Tumor details
    histology = Column(
        SAEnum(
            TumorHistology,
            name="tumor_histology",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )  # Restored from String with proper enum syntax
    location = Column(
        SAEnum(
            TumorLocation,
            name="tumor_location",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
    )  # Restored from String with proper enum syntax
    size_mm = Column(Float, nullable=True)
    differentiation = Column(String(50), nullable=True)
    her2_status = Column(Boolean, nullable=True)
    msi_status = Column(String(50), nullable=True)
    pdl1_expression = Column(Float, nullable=True)

    # TNM Staging
    t_stage = Column(String(10), nullable=False)  # Changed from Enum temporarily
    n_stage = Column(String(10), nullable=False)  # Changed from Enum temporarily
    m_stage = Column(String(10), nullable=False)  # Changed from Enum temporarily

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("PatientORM", back_populates="tumor_characteristics")

    # Indexes
    __table_args__ = (
        Index("ix_tumor_histology_location", "histology", "location"),
        Index("ix_tumor_tnm_stage", "t_stage", "n_stage", "m_stage"),
        UniqueConstraint("patient_id", name="uq_tumor_characteristics_patient"),
    )


class PerformanceStatusORM(Base):
    """Performance status table."""

    __tablename__ = "performance_status"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    ecog_status = Column(String(10), nullable=False)  # Changed from Enum temporarily
    karnofsky_score = Column(Integer, nullable=True)
    weight_loss_percent = Column(Float, nullable=True)
    nutritional_risk = Column(String(100), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("PatientORM", back_populates="performance_status")

    # Indexes
    __table_args__ = (
        UniqueConstraint("patient_id", name="uq_performance_status_patient"),
    )


class LaboratoryResultsORM(Base):
    """Laboratory results table."""

    __tablename__ = "laboratory_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

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
        Index("ix_lab_results_patient_date", "patient_id", "collection_date"),
    )


class TreatmentPlanORM(Base):
    """Treatment plan table."""

    __tablename__ = "treatment_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)

    # Treatment details
    protocol = Column(String(100), nullable=False)  # Changed from Enum temporarily
    surgical_procedure = Column(
        String(100), nullable=True
    )  # Changed from Enum temporarily

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
        Index("ix_treatment_plans_patient_protocol", "patient_id", "protocol"),
        Index("ix_treatment_plans_start_date", "planned_start_date"),
    )


class ADCIDecisionORM(Base):
    """ADCI decision support results table."""

    __tablename__ = "adci_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    treatment_plan_id = Column(
        UUID(as_uuid=True), ForeignKey("treatment_plans.id"), nullable=True
    )

    # Decision inputs
    input_parameters = Column(JSON, nullable=False)

    # ADCI outputs
    adci_score = Column(Float, nullable=False)
    confidence_level = Column(
        String(20), nullable=False
    )  # Changed from Enum temporarily

    # Recommendations
    recommended_protocol = Column(
        String(100), nullable=False
    )  # Changed from Enum temporarily
    alternative_protocols = Column(JSON, nullable=True, default=[])

    # Supporting data
    evidence_quality = Column(String(20), nullable=False)
    risk_factors = Column(JSON, nullable=True, default=[])
    contraindications = Column(JSON, nullable=True, default=[])

    # Decision metadata
    decision_timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    decision_maker = Column(String(100), nullable=False)
    status = Column(
        SAEnum(
            DecisionStatus,
            name="decision_status",
            native_enum=False,
            validate_strings=True,
        ),
        default=DecisionStatus.PENDING,
        nullable=False,
    )  # Restored from String with proper enum syntax

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
        Index("ix_adci_decisions_patient_score", "patient_id", "adci_score"),
        Index("ix_adci_decisions_timestamp", "decision_timestamp"),
        Index("ix_adci_decisions_maker", "decision_maker"),
    )


class ClinicalOutcomeORM(Base):
    """Clinical outcome tracking table."""

    __tablename__ = "clinical_outcomes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    adci_decision_id = Column(
        UUID(as_uuid=True), ForeignKey("adci_decisions.id"), nullable=True
    )

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
        Index(
            "ix_clinical_outcomes_patient_followup", "patient_id", "last_follow_up_date"
        ),
        Index("ix_clinical_outcomes_survival", "overall_survival_months"),
    )


class AuditLogORM(Base):
    """Audit log table for HIPAA compliance."""

    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Audit details
    entity_type = Column(String(50), nullable=False)  # patient, decision, etc.
    entity_id = Column(UUID(as_uuid=True), nullable=True)
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
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_user_timestamp", "user_id", "timestamp"),
        Index("ix_audit_logs_action_timestamp", "action", "timestamp"),
    )
