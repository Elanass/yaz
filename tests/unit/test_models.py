"""
Unit tests for core models
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from datetime import datetime
from surgify.core.models.database_models import User, Patient, Case, CaseStatus


class TestUser:
    """Test User model"""

    def test_user_creation(self):
        """Test user creation with valid data"""
        user = User(
            username="test_surgeon",
            email="surgeon@test.com",
            hashed_password="hashed_password",
            full_name="Test Surgeon",
            role="surgeon",
            is_active=True,
        )

        assert user.username == "test_surgeon"
        assert user.email == "surgeon@test.com"
        assert user.role == "surgeon"
        assert user.is_active is True


class TestPatient:
    """Test Patient model"""

    def test_patient_creation(self):
        """Test patient creation with valid data"""
        patient = Patient(
            patient_id="TEST001",
            age=65,
            gender="Male",
            bmi=28.5,
            medical_history="Hypertension, Diabetes",
        )

        assert patient.patient_id == "TEST001"
        assert patient.age == 65
        assert patient.gender == "Male"
        assert patient.bmi == 28.5


class TestCase:
    """Test Case model"""

    def test_case_creation(self):
        """Test case creation with valid data"""
        case = Case(
            case_number="CASE001",
            procedure_type="Laparoscopic Gastrectomy",
            status=CaseStatus.PLANNED,
            notes="Test surgical case",
            patient_id=1,
        )

        assert case.procedure_type == "Laparoscopic Gastrectomy"
        assert case.status == CaseStatus.PLANNED
        assert case.notes == "Test surgical case"
        assert case.case_number == "CASE001"


class TestCaseStatus:
    """Test CaseStatus enum"""

    def test_case_status_values(self):
        """Test all case status values"""
        assert CaseStatus.PLANNED == "planned"
        assert CaseStatus.IN_PROGRESS == "in_progress"
        assert CaseStatus.COMPLETED == "completed"
        assert CaseStatus.CANCELLED == "cancelled"
