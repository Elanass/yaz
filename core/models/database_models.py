"""
Database Models for Surgery Analytics Platform
Cleaned and optimized to match actual database schema
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

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
    medical_history = Column(Text, nullable=True)  # Changed from JSON to Text to match DB
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
    recommendations = Column(Text, nullable=True)  # Changed from JSON to Text to match DB
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
