"""
Database Models for Surgery Analytics Platform
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from core.database import Base

class CaseStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ProcedureType(str, Enum):
    GASTRIC_RESECTION = "gastric_resection"
    LAPAROSCOPIC = "laparoscopic"
    OPEN_SURGERY = "open_surgery"
    ENDOSCOPIC = "endoscopic"

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
    medical_history = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    cases = relationship("Case", back_populates="patient")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    surgeon_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Case details
    procedure_type = Column(String(50), nullable=False)
    diagnosis = Column(String(200), nullable=True)
    status = Column(String(20), default=CaseStatus.PLANNED)
    
    # Scheduling
    scheduled_date = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    # Clinical data
    preop_assessment = Column(JSON, nullable=True)
    intraop_notes = Column(Text, nullable=True)
    postop_outcome = Column(JSON, nullable=True)
    
    # Decision support
    risk_score = Column(Float, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="cases")
    surgeon = relationship("User", back_populates="cases")
    decisions = relationship("Decision", back_populates="case")

class Decision(Base):
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    
    decision_type = Column(String(50), nullable=False)  # e.g., "surgical_approach", "timing"
    decision_value = Column(String(100), nullable=False)
    confidence_score = Column(Float, nullable=True)
    rationale = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    case = relationship("Case", back_populates="decisions")

class Protocol(Base):
    __tablename__ = "protocols"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    version = Column(String(20), nullable=False)
    procedure_type = Column(String(50), nullable=False)
    
    # Protocol content
    steps = Column(JSON, nullable=False)
    guidelines = Column(Text, nullable=True)
    contraindications = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
