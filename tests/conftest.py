"""
Test configuration and fixtures
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from surgify.core.database import Base, get_db
from surgify.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./tests/fixtures/test_surgify.db"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_db():
    """Create a test database."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture
def client(test_db) -> Generator:
    """Create a test client."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "test_surgeon",
        "email": "surgeon@test.com",
        "full_name": "Test Surgeon",
        "password": "testpassword123",
    }


@pytest.fixture
def sample_patient_data():
    """Sample patient data for testing."""
    return {
        "patient_id": "TEST001",
        "age": 65,
        "gender": "Male",
        "bmi": 28.5,
        "medical_history": "Hypertension, Diabetes Type 2",
    }


@pytest.fixture
def sample_case_data():
    """Sample case data for testing."""
    return {
        "procedure": "Laparoscopic Gastrectomy",
        "status": "planned",
        "scheduled_date": "2025-08-15T10:00:00",
        "notes": "Test case for gastric cancer treatment",
    }
