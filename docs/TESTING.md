# Testing Guide

## Overview

This document provides comprehensive testing guidelines for the YAZ Healthcare Platform. Our testing strategy ensures code quality, reliability, and compliance with healthcare standards.

## Testing Strategy

### Testing Pyramid

```
    /\
   /  \    E2E Tests (5%)
  /____\   
 /      \   Integration Tests (15%)
/________\  
           Unit Tests (80%)
```

### Test Types

1. **Unit Tests**: Individual functions and classes
2. **Integration Tests**: Module interactions and API endpoints
3. **End-to-End Tests**: Complete user workflows
4. **Security Tests**: Vulnerability and compliance testing
5. **Performance Tests**: Load and stress testing

## Test Structure

### Directory Layout

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── test_canary.py          # Smoke tests
├── unit/                   # Unit tests
│   ├── test_models.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/            # Integration tests
│   ├── test_api.py
│   ├── test_database.py
│   └── test_external_apis.py
├── e2e/                   # End-to-end tests
│   ├── test_patient_workflow.py
│   └── test_provider_workflow.py
├── security/              # Security tests
│   ├── test_authentication.py
│   ├── test_authorization.py
│   └── test_data_protection.py
├── performance/           # Performance tests
│   ├── test_load.py
│   └── test_stress.py
└── fixtures/              # Test data and fixtures
    ├── patients.json
    ├── providers.json
    └── fhir_resources.json
```

## Running Tests

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-test.txt

# Set up test environment
cp .env.example .env.test
export YAZ_ENV=test
```

### Basic Test Commands

```bash
# Run all tests
make test

# Run specific test types
make test-unit
make test-integration
make test-e2e

# Run with coverage
make test-coverage

# Run security tests
make test-security

# Run performance tests
make test-performance
```

### Advanced Test Options

```bash
# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_models.py

# Run specific test function
pytest tests/unit/test_models.py::test_patient_model

# Run tests matching pattern
pytest -k "test_fhir"

# Run tests with debugging
pytest --pdb

# Run tests in parallel
pytest -n auto
```

## Unit Testing

### Testing Guidelines

1. **Isolation**: Each test should be independent
2. **Clarity**: Test names should describe what is being tested
3. **Coverage**: Aim for 100% line coverage on new code
4. **Speed**: Unit tests should run quickly (< 1s each)

### Example Unit Test

```python
# tests/unit/test_patient_model.py
import pytest
from datetime import date
from models.patient import Patient, PatientNotFoundError

class TestPatientModel:
    """Test cases for the Patient model."""
    
    def test_create_patient_with_valid_data(self):
        """Test creating a patient with valid data."""
        patient = Patient(
            first_name="John",
            last_name="Doe",
            date_of_birth=date(1990, 1, 1),
            mrn="MRN123456"
        )
        
        assert patient.first_name == "John"
        assert patient.last_name == "Doe"
        assert patient.full_name == "John Doe"
        assert patient.mrn == "MRN123456"
    
    def test_patient_age_calculation(self):
        """Test patient age calculation."""
        patient = Patient(
            first_name="Jane",
            last_name="Smith",
            date_of_birth=date(1985, 6, 15),
            mrn="MRN789012"
        )
        
        # Assuming current date for test
        expected_age = 39  # Adjust based on current date
        assert patient.age >= expected_age
    
    def test_invalid_mrn_raises_error(self):
        """Test that invalid MRN raises validation error."""
        with pytest.raises(ValueError, match="Invalid MRN format"):
            Patient(
                first_name="Invalid",
                last_name="Patient",
                date_of_birth=date(1990, 1, 1),
                mrn="INVALID"
            )
```

### Mocking External Dependencies

```python
# tests/unit/test_fhir_service.py
import pytest
from unittest.mock import Mock, patch
from services.fhir_service import FHIRService

class TestFHIRService:
    """Test cases for FHIR service."""
    
    @patch('infra.fhir_client.FHIRClient')
    def test_create_patient_success(self, mock_client):
        """Test successful patient creation."""
        # Arrange
        mock_client_instance = Mock()
        mock_client.return_value = mock_client_instance
        mock_client_instance.create_patient.return_value = {
            "id": "patient-123",
            "resourceType": "Patient"
        }
        
        service = FHIRService()
        patient_data = {
            "name": [{"given": ["John"], "family": "Doe"}],
            "birthDate": "1990-01-01"
        }
        
        # Act
        result = service.create_patient(patient_data)
        
        # Assert
        assert result["id"] == "patient-123"
        mock_client_instance.create_patient.assert_called_once_with(patient_data)
```

## Integration Testing

### Database Integration Tests

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.base import Base
from models.patient import Patient

@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    yield session
    
    session.close()

class TestPatientRepository:
    """Test database operations for patients."""
    
    def test_create_and_retrieve_patient(self, db_session):
        """Test creating and retrieving a patient."""
        # Create patient
        patient = Patient(
            first_name="John",
            last_name="Doe",
            mrn="MRN123456"
        )
        db_session.add(patient)
        db_session.commit()
        
        # Retrieve patient
        retrieved = db_session.query(Patient).filter_by(mrn="MRN123456").first()
        
        assert retrieved is not None
        assert retrieved.first_name == "John"
        assert retrieved.last_name == "Doe"
    
    def test_patient_search_by_name(self, db_session):
        """Test searching patients by name."""
        # Create test patients
        patients = [
            Patient(first_name="John", last_name="Doe", mrn="MRN001"),
            Patient(first_name="Jane", last_name="Smith", mrn="MRN002"),
            Patient(first_name="John", last_name="Smith", mrn="MRN003")
        ]
        
        for patient in patients:
            db_session.add(patient)
        db_session.commit()
        
        # Search by first name
        johns = db_session.query(Patient).filter(
            Patient.first_name == "John"
        ).all()
        
        assert len(johns) == 2
        assert all(p.first_name == "John" for p in johns)
```

### API Integration Tests

```python
# tests/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestPatientAPI:
    """Test patient API endpoints."""
    
    def test_create_patient_endpoint(self):
        """Test creating a patient via API."""
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1990-01-01",
            "mrn": "MRN123456"
        }
        
        response = client.post("/api/patients", json=patient_data)
        
        assert response.status_code == 201
        assert response.json()["first_name"] == "John"
        assert "id" in response.json()
    
    def test_get_patient_endpoint(self):
        """Test retrieving a patient via API."""
        # First create a patient
        patient_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1985-06-15",
            "mrn": "MRN789012"
        }
        
        create_response = client.post("/api/patients", json=patient_data)
        patient_id = create_response.json()["id"]
        
        # Then retrieve it
        response = client.get(f"/api/patients/{patient_id}")
        
        assert response.status_code == 200
        assert response.json()["first_name"] == "Jane"
        assert response.json()["id"] == patient_id
    
    def test_patient_not_found(self):
        """Test retrieving non-existent patient."""
        response = client.get("/api/patients/non-existent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
```

## Security Testing

### Authentication Tests

```python
# tests/security/test_authentication.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestAuthentication:
    """Test authentication mechanisms."""
    
    def test_protected_endpoint_requires_auth(self):
        """Test that protected endpoints require authentication."""
        response = client.get("/api/patients")
        
        assert response.status_code == 401
        assert "authentication" in response.json()["detail"].lower()
    
    def test_valid_token_grants_access(self):
        """Test that valid tokens grant access."""
        # Get a valid token
        auth_response = client.post("/auth/token", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        response = client.get("/api/patients", headers=headers)
        
        assert response.status_code == 200
    
    def test_expired_token_rejected(self):
        """Test that expired tokens are rejected."""
        expired_token = "expired.jwt.token"
        headers = {"Authorization": f"Bearer {expired_token}"}
        
        response = client.get("/api/patients", headers=headers)
        
        assert response.status_code == 401
        assert "expired" in response.json()["detail"].lower()
```

### Data Protection Tests

```python
# tests/security/test_data_protection.py
import pytest
from services.encryption import PHIEncryption

class TestDataProtection:
    """Test PHI encryption and data protection."""
    
    def test_phi_encryption_roundtrip(self):
        """Test PHI encryption and decryption."""
        encryption = PHIEncryption(key=b"test-key-32-chars-long-12345678")
        original_data = "123-45-6789"  # SSN
        
        # Encrypt
        encrypted = encryption.encrypt_phi(original_data)
        assert encrypted != original_data
        
        # Decrypt
        decrypted = encryption.decrypt_phi(encrypted)
        assert decrypted == original_data
    
    def test_phi_data_masking(self):
        """Test PHI data masking for display."""
        from utils.phi_utils import mask_ssn, mask_phone
        
        # Test SSN masking
        ssn = "123-45-6789"
        masked_ssn = mask_ssn(ssn)
        assert masked_ssn == "XXX-XX-6789"
        
        # Test phone masking
        phone = "(555) 123-4567"
        masked_phone = mask_phone(phone)
        assert masked_phone == "(XXX) XXX-4567"
```

## Performance Testing

### Load Testing

```python
# tests/performance/test_load.py
import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestLoadPerformance:
    """Test application performance under load."""
    
    def test_patient_endpoint_performance(self):
        """Test patient endpoint response time."""
        start_time = time.time()
        
        response = client.get("/api/patients/test-patient-id")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self):
        """Test handling concurrent requests."""
        def make_request():
            return client.get("/health").status_code
        
        # Make 50 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(50)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(status == 200 for status in results)
    
    @pytest.mark.slow
    def test_database_query_performance(self):
        """Test database query performance."""
        from models.patient import Patient
        from database import get_db_session
        
        session = next(get_db_session())
        
        start_time = time.time()
        
        # Query that should be optimized
        patients = session.query(Patient).filter(
            Patient.last_name.like("Smith%")
        ).limit(100).all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        assert query_time < 0.5  # Should complete within 500ms
        session.close()
```

## End-to-End Testing

### Patient Workflow Tests

```python
# tests/e2e/test_patient_workflow.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="session")
def browser():
    """Create a browser instance for E2E tests."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    yield driver
    
    driver.quit()

class TestPatientWorkflow:
    """Test complete patient management workflows."""
    
    def test_create_patient_workflow(self, browser):
        """Test creating a new patient through the UI."""
        browser.get("http://localhost:8000/patients/new")
        
        # Fill out patient form
        browser.find_element(By.ID, "first-name").send_keys("John")
        browser.find_element(By.ID, "last-name").send_keys("Doe")
        browser.find_element(By.ID, "date-of-birth").send_keys("01/01/1990")
        browser.find_element(By.ID, "mrn").send_keys("MRN123456")
        
        # Submit form
        browser.find_element(By.ID, "submit-button").click()
        
        # Wait for success message
        success_message = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        
        assert "Patient created successfully" in success_message.text
    
    def test_search_patient_workflow(self, browser):
        """Test searching for patients through the UI."""
        browser.get("http://localhost:8000/patients")
        
        # Enter search term
        search_box = browser.find_element(By.ID, "patient-search")
        search_box.send_keys("John Doe")
        
        # Click search button
        browser.find_element(By.ID, "search-button").click()
        
        # Wait for results
        results = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search-results"))
        )
        
        assert "John Doe" in results.text
```

## Test Data Management

### Fixtures and Test Data

```python
# tests/fixtures/patients.py
import pytest
from models.patient import Patient

@pytest.fixture
def sample_patient():
    """Create a sample patient for testing."""
    return Patient(
        first_name="John",
        last_name="Doe",
        date_of_birth="1990-01-01",
        mrn="MRN123456"
    )

@pytest.fixture
def patient_list():
    """Create a list of patients for testing."""
    return [
        Patient(first_name="John", last_name="Doe", mrn="MRN001"),
        Patient(first_name="Jane", last_name="Smith", mrn="MRN002"),
        Patient(first_name="Bob", last_name="Johnson", mrn="MRN003")
    ]

@pytest.fixture
def fhir_patient_resource():
    """Create a FHIR Patient resource for testing."""
    return {
        "resourceType": "Patient",
        "id": "patient-123",
        "name": [
            {
                "use": "official",
                "family": "Doe",
                "given": ["John"]
            }
        ],
        "birthDate": "1990-01-01",
        "identifier": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "MR"
                        }
                    ]
                },
                "value": "MRN123456"
            }
        ]
    }
```

## Continuous Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: yaz_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run linting
      run: |
        ruff check .
        black --check .
        isort --check .
    
    - name: Run type checking
      run: mypy .
    
    - name: Run security scan
      run: bandit -r .
    
    - name: Run unit tests
      run: pytest tests/unit/ -v --cov=src
    
    - name: Run integration tests
      run: pytest tests/integration/ -v
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/yaz_test
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
```

## Test Coverage

### Coverage Requirements

- **Overall coverage**: ≥80%
- **New code coverage**: ≥90%
- **Critical paths**: 100% (authentication, PHI handling)
- **Security functions**: 100%

### Coverage Analysis

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Check coverage thresholds
pytest --cov=src --cov-fail-under=80

# Generate coverage badge
coverage-badge -o coverage.svg
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = src
omit = 
    */tests/*
    */venv/*
    */migrations/*
    */conftest.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Test Environment Setup

### Local Development

```bash
# Set up test environment
make test-setup

# Run quick tests
make test-quick

# Run full test suite
make test-full

# Run tests with debugging
make test-debug
```

### Docker Testing

```dockerfile
# Dockerfile.test
FROM python:3.10-slim

WORKDIR /app
COPY requirements-test.txt .
RUN pip install -r requirements-test.txt

COPY . .
CMD ["pytest", "-v", "--cov=src"]
```

```bash
# Build and run test container
docker build -f Dockerfile.test -t yaz-tests .
docker run --rm yaz-tests
```

## Best Practices

### Test Writing Guidelines

1. **AAA Pattern**: Arrange, Act, Assert
2. **Single Responsibility**: One test per concept
3. **Descriptive Names**: Clear test method names
4. **Fast Execution**: Keep unit tests under 1 second
5. **Deterministic**: Tests should always pass or fail consistently

### Test Maintenance

1. **Regular Cleanup**: Remove obsolete tests
2. **Refactor**: Keep tests DRY and maintainable
3. **Documentation**: Comment complex test logic
4. **Data Management**: Use factories for test data
5. **Isolation**: Ensure tests don't affect each other

### Healthcare-Specific Testing

1. **PHI Protection**: Never use real patient data in tests
2. **Compliance**: Test HIPAA audit logging
3. **Integration**: Test FHIR standard compliance
4. **Security**: Regular penetration testing
5. **Validation**: Test medical data validation rules

---

For additional testing information, see:
- [Operations Guide](OPERATIONS.md)
- [Security Guide](SECURITY.md)
- [Architecture Overview](ARCHITECTURE.md)
