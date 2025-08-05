"""
End-to-end tests for Enhanced Cases API
Tests both cache-hit and cache-miss scenarios
"""

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from surgify.core.cache import cache_client
from surgify.core.database import Base, get_db
from surgify.core.models.database_models import CaseModel
from surgify.core.services.case_service import CaseService
from surgify.main import app

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override dependencies
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Mock Redis client for testing
    cache_client._client = fakeredis.FakeRedis(decode_responses=True)
    cache_client._connected = True

    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def sample_case_data():
    return {
        "patient_id": "PAT-001",
        "procedure_type": "Cardiac Surgery",
        "diagnosis": "Coronary Artery Disease",
        "status": "planned",
        "priority": "high",
        "surgeon_id": "SURG-001",
        "notes": "High-risk patient requiring specialized care",
    }


class TestCasesAPI:
    """Test cases API endpoints with cache scenarios"""

    def test_create_case_success(self, client, sample_case_data):
        """Test successful case creation"""
        response = client.post("/api/v1/cases/", json=sample_case_data)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert "case_number" in data
        assert data["patient_id"] == sample_case_data["patient_id"]
        assert data["procedure_type"] == sample_case_data["procedure_type"]
        assert data["diagnosis"] == sample_case_data["diagnosis"]
        assert data["status"] == sample_case_data["status"]
        assert data["priority"] == sample_case_data["priority"]
        assert "risk_score" in data
        assert "recommendations" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_case_missing_required_fields(self, client):
        """Test case creation with missing required fields"""
        incomplete_data = {
            "patient_id": "PAT-002"
            # Missing procedure_type
        }

        response = client.post("/api/v1/cases/", json=incomplete_data)
        assert response.status_code == 422

    def test_list_cases_cache_miss_then_hit(self, client, sample_case_data):
        """Test list cases with cache miss then cache hit scenario"""
        # First, create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        assert create_response.status_code == 201

        # First request - cache miss
        response1 = client.get("/api/v1/cases/")
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list)

        # Second request - should be cache hit (same parameters)
        response2 = client.get("/api/v1/cases/")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2

    def test_list_cases_with_filters(self, client, sample_case_data):
        """Test list cases with various filters"""
        # Create a case first
        client.post("/api/v1/cases/", json=sample_case_data)

        # Test status filter
        response = client.get("/api/v1/cases/?status=planned")
        assert response.status_code == 200
        data = response.json()
        for case in data:
            assert case["status"] == "planned"

        # Test procedure type filter
        response = client.get(
            f"/api/v1/cases/?procedure_type={sample_case_data['procedure_type']}"
        )
        assert response.status_code == 200
        data = response.json()
        for case in data:
            assert case["procedure_type"] == sample_case_data["procedure_type"]

        # Test priority filter
        response = client.get(f"/api/v1/cases/?priority={sample_case_data['priority']}")
        assert response.status_code == 200
        data = response.json()
        for case in data:
            assert case["priority"] == sample_case_data["priority"]

    def test_list_cases_pagination(self, client, sample_case_data):
        """Test list cases pagination"""
        # Create multiple cases
        for i in range(5):
            case_data = sample_case_data.copy()
            case_data["patient_id"] = f"PAT-{i:03d}"
            client.post("/api/v1/cases/", json=case_data)

        # Test pagination
        response = client.get("/api/v1/cases/?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        # Test different page
        response = client.get("/api/v1/cases/?page=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_get_case_cache_scenarios(self, client, sample_case_data):
        """Test get case with cache miss and hit scenarios"""
        # Create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        case_id = create_response.json()["id"]

        # First request - cache miss
        response1 = client.get(f"/api/v1/cases/{case_id}")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - cache hit
        response2 = client.get(f"/api/v1/cases/{case_id}")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2
        assert data1["id"] == case_id

    def test_get_case_not_found(self, client):
        """Test get case with invalid ID"""
        response = client.get("/api/v1/cases/99999")
        assert response.status_code == 404

    def test_update_case_success(self, client, sample_case_data):
        """Test successful case update"""
        # Create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        case_id = create_response.json()["id"]

        # Update the case
        update_data = {
            "status": "in_progress",
            "priority": "urgent",
            "notes": "Updated notes for case",
        }

        response = client.put(f"/api/v1/cases/{case_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == case_id
        assert data["status"] == update_data["status"]
        assert data["priority"] == update_data["priority"]
        assert data["notes"] == update_data["notes"]
        # Other fields should remain unchanged
        assert data["patient_id"] == sample_case_data["patient_id"]
        assert data["procedure_type"] == sample_case_data["procedure_type"]

    def test_update_case_not_found(self, client):
        """Test update case with invalid ID"""
        update_data = {"status": "completed"}
        response = client.put("/api/v1/cases/99999", json=update_data)
        assert response.status_code == 404

    def test_update_case_idempotent(self, client, sample_case_data):
        """Test that updates are idempotent"""
        # Create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        case_id = create_response.json()["id"]

        # Same update multiple times
        update_data = {"status": "completed"}

        response1 = client.put(f"/api/v1/cases/{case_id}", json=update_data)
        response2 = client.put(f"/api/v1/cases/{case_id}", json=update_data)

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Results should be the same (idempotent)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["status"] == data2["status"] == "completed"

    def test_delete_case_success(self, client, sample_case_data):
        """Test successful case deletion"""
        # Create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        case_id = create_response.json()["id"]

        # Delete the case
        response = client.delete(f"/api/v1/cases/{case_id}")
        assert response.status_code == 204

        # Verify case is deleted
        get_response = client.get(f"/api/v1/cases/{case_id}")
        assert get_response.status_code == 404

    def test_delete_case_idempotent(self, client, sample_case_data):
        """Test that deletes are idempotent"""
        # Create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        case_id = create_response.json()["id"]

        # Delete multiple times
        response1 = client.delete(f"/api/v1/cases/{case_id}")
        response2 = client.delete(f"/api/v1/cases/{case_id}")

        # First should succeed, second should return 404 (but still idempotent)
        assert response1.status_code == 204
        assert response2.status_code == 404

    def test_search_cases(self, client, sample_case_data):
        """Test case search functionality"""
        # Create a case
        client.post("/api/v1/cases/", json=sample_case_data)

        # Search by patient ID
        response = client.get(f"/api/v1/cases/?search={sample_case_data['patient_id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

        # Search by diagnosis
        response = client.get(f"/api/v1/cases/?search=Coronary")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_sorting_functionality(self, client, sample_case_data):
        """Test case sorting"""
        # Create multiple cases with different timestamps
        for i in range(3):
            case_data = sample_case_data.copy()
            case_data["patient_id"] = f"PAT-SORT-{i:03d}"
            client.post("/api/v1/cases/", json=case_data)

        # Test ascending sort
        response = client.get("/api/v1/cases/?sort_by=created_at&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

        # Test descending sort (default)
        response = client.get("/api/v1/cases/?sort_by=created_at&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_cache_invalidation_on_create(self, client, sample_case_data):
        """Test that cache is invalidated when creating cases"""
        # Get initial list
        response1 = client.get("/api/v1/cases/")
        initial_count = len(response1.json())

        # Create a new case
        client.post("/api/v1/cases/", json=sample_case_data)

        # Get list again - should reflect new case
        response2 = client.get("/api/v1/cases/")
        new_count = len(response2.json())

        assert new_count == initial_count + 1

    def test_cache_invalidation_on_update(self, client, sample_case_data):
        """Test that cache is invalidated when updating cases"""
        # Create a case
        create_response = client.post("/api/v1/cases/", json=sample_case_data)
        case_id = create_response.json()["id"]

        # Get case (cache it)
        response1 = client.get(f"/api/v1/cases/{case_id}")
        original_status = response1.json()["status"]

        # Update the case
        client.put(f"/api/v1/cases/{case_id}", json={"status": "completed"})

        # Get case again - should reflect update
        response2 = client.get(f"/api/v1/cases/{case_id}")
        updated_status = response2.json()["status"]

        assert original_status != updated_status
        assert updated_status == "completed"

    def test_error_handling(self, client):
        """Test error handling in various scenarios"""
        # Test invalid JSON
        response = client.post("/api/v1/cases/", data="invalid json")
        assert response.status_code == 422

        # Test invalid query parameters
        response = client.get("/api/v1/cases/?page=-1")
        assert response.status_code == 422

        response = client.get("/api/v1/cases/?limit=1000")
        assert response.status_code == 422
