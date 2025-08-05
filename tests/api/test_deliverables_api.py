"""
End-to-end tests for Deliverables API
Tests both cache-hit and cache-miss scenarios for deliverable management
"""

from datetime import datetime, timedelta

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from surgify.core.cache import cache_client
from surgify.core.database import Base, get_db
from surgify.core.services.deliverable_service import (
    DeliverableFormat,
    DeliverableStatus,
    DeliverableType,
)
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
def sample_deliverable_request():
    return {
        "type": "case_report",
        "title": "Test Case Report",
        "description": "A test case report for patient PAT-001",
        "case_id": 1,
        "format": "pdf",
        "auto_generate": True,
        "parameters": {"include_images": True, "include_notes": True},
        "metadata": {"author": "Dr. Test", "department": "Surgery"},
    }


@pytest.fixture
def sample_template_parameters():
    return {
        "case_id": 1,
        "include_images": True,
        "include_notes": True,
        "report_date": "2024-01-01",
    }


class TestDeliverablesAPI:
    """Test deliverables API endpoints with cache scenarios"""

    def test_create_deliverable_success(self, client, sample_deliverable_request):
        """Test successful deliverable creation"""
        response = client.post("/api/v1/deliverables/", json=sample_deliverable_request)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["type"] == sample_deliverable_request["type"]
        assert data["title"] == sample_deliverable_request["title"]
        assert data["description"] == sample_deliverable_request["description"]
        assert data["case_id"] == sample_deliverable_request["case_id"]
        assert data["format"] == sample_deliverable_request["format"]
        assert data["status"] in [
            DeliverableStatus.DRAFT,
            DeliverableStatus.PENDING_REVIEW,
        ]
        assert "download_url" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_deliverable_missing_required_fields(self, client):
        """Test deliverable creation with missing required fields"""
        incomplete_data = {
            "type": "case_report",
            "title": "Test Report"
            # Missing format
        }

        response = client.post("/api/v1/deliverables/", json=incomplete_data)
        assert response.status_code == 422

    def test_list_deliverables_cache_scenarios(
        self, client, sample_deliverable_request
    ):
        """Test list deliverables with cache miss then hit scenario"""
        # Create a deliverable first
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        assert create_response.status_code == 201

        # First request - cache miss
        response1 = client.get("/api/v1/deliverables/")
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list)
        assert len(data1) > 0

        # Second request - cache hit
        response2 = client.get("/api/v1/deliverables/")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical (within cache TTL)
        assert data1 == data2

    def test_list_deliverables_with_filters(self, client, sample_deliverable_request):
        """Test list deliverables with various filters"""
        # Create a deliverable
        client.post("/api/v1/deliverables/", json=sample_deliverable_request)

        # Test type filter
        response = client.get(
            f"/api/v1/deliverables/?type={sample_deliverable_request['type']}"
        )
        assert response.status_code == 200
        data = response.json()
        for deliverable in data:
            assert deliverable["type"] == sample_deliverable_request["type"]

        # Test case_id filter
        response = client.get(
            f"/api/v1/deliverables/?case_id={sample_deliverable_request['case_id']}"
        )
        assert response.status_code == 200
        data = response.json()
        for deliverable in data:
            assert deliverable["case_id"] == sample_deliverable_request["case_id"]

        # Test status filter
        response = client.get("/api/v1/deliverables/?status=draft")
        assert response.status_code == 200
        data = response.json()
        for deliverable in data:
            assert deliverable["status"] in ["draft", "pending_review"]

    def test_get_deliverable_cache_scenarios(self, client, sample_deliverable_request):
        """Test get deliverable with cache scenarios"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # First request - cache miss
        response1 = client.get(f"/api/v1/deliverables/{deliverable_id}")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - cache hit
        response2 = client.get(f"/api/v1/deliverables/{deliverable_id}")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2
        assert data1["id"] == deliverable_id

    def test_get_deliverable_not_found(self, client):
        """Test get deliverable with invalid ID"""
        response = client.get("/api/v1/deliverables/nonexistent-id")
        assert response.status_code == 404

    def test_update_deliverable_success(self, client, sample_deliverable_request):
        """Test successful deliverable update"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Update the deliverable
        update_data = {
            "title": "Updated Test Report",
            "status": "pending_review",
            "description": "Updated description",
        }

        response = client.put(
            f"/api/v1/deliverables/{deliverable_id}", json=update_data
        )
        assert response.status_code == 200
        data = response.json()

        assert data["id"] == deliverable_id
        assert data["title"] == update_data["title"]
        assert data["status"] == update_data["status"]
        assert data["description"] == update_data["description"]
        # Other fields should remain unchanged
        assert data["type"] == sample_deliverable_request["type"]
        assert data["format"] == sample_deliverable_request["format"]

    def test_update_deliverable_status_transitions(
        self, client, sample_deliverable_request
    ):
        """Test deliverable status transitions with timestamps"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Update to approved status
        response = client.put(
            f"/api/v1/deliverables/{deliverable_id}", json={"status": "approved"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
        assert "approved_at" in data

        # Update to published status
        response = client.put(
            f"/api/v1/deliverables/{deliverable_id}", json={"status": "published"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "published"
        assert "published_at" in data

    def test_update_deliverable_idempotent(self, client, sample_deliverable_request):
        """Test that updates are idempotent"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Same update multiple times
        update_data = {"status": "approved"}

        response1 = client.put(
            f"/api/v1/deliverables/{deliverable_id}", json=update_data
        )
        response2 = client.put(
            f"/api/v1/deliverables/{deliverable_id}", json=update_data
        )

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Results should be the same (idempotent)
        data1 = response1.json()
        data2 = response2.json()
        assert data1["status"] == data2["status"] == "approved"

    def test_update_deliverable_not_found(self, client):
        """Test update deliverable with invalid ID"""
        update_data = {"status": "approved"}
        response = client.put("/api/v1/deliverables/nonexistent-id", json=update_data)
        assert response.status_code == 404

    def test_delete_deliverable_success(self, client, sample_deliverable_request):
        """Test successful deliverable deletion"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Delete the deliverable
        response = client.delete(f"/api/v1/deliverables/{deliverable_id}")
        assert response.status_code == 204

        # Verify deliverable is deleted
        get_response = client.get(f"/api/v1/deliverables/{deliverable_id}")
        assert get_response.status_code == 404

    def test_delete_deliverable_idempotent(self, client, sample_deliverable_request):
        """Test that delete operations are idempotent"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Delete multiple times
        response1 = client.delete(f"/api/v1/deliverables/{deliverable_id}")
        response2 = client.delete(f"/api/v1/deliverables/{deliverable_id}")

        # First should succeed, second should return 404 (idempotent)
        assert response1.status_code == 204
        assert response2.status_code == 404

    def test_download_deliverable_success(self, client, sample_deliverable_request):
        """Test successful deliverable download"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Download the deliverable
        response = client.get(f"/api/v1/deliverables/{deliverable_id}/download")
        assert response.status_code == 200

        # Check content type based on format
        format_type = sample_deliverable_request["format"].lower()
        if format_type == "pdf":
            assert "application/pdf" in response.headers.get("content-type", "")
        elif format_type == "json":
            assert "application/json" in response.headers.get("content-type", "")
        elif format_type == "html":
            assert "text/html" in response.headers.get("content-type", "")

        # Check content disposition header
        assert "attachment" in response.headers.get("content-disposition", "")

    def test_download_deliverable_not_found(self, client):
        """Test download deliverable with invalid ID"""
        response = client.get("/api/v1/deliverables/nonexistent-id/download")
        assert response.status_code == 404

    def test_download_deliverable_idempotent(self, client, sample_deliverable_request):
        """Test that downloads are idempotent"""
        # Create a deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Download multiple times
        response1 = client.get(f"/api/v1/deliverables/{deliverable_id}/download")
        response2 = client.get(f"/api/v1/deliverables/{deliverable_id}/download")

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Content should be identical
        assert response1.content == response2.content


class TestTemplatesAPI:
    """Test template-related endpoints"""

    def test_list_templates_success(self, client):
        """Test list templates with caching"""
        # First request - cache miss
        response1 = client.get("/api/v1/deliverables/templates")
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list)
        assert len(data1) > 0

        # Verify template structure
        template = data1[0]
        assert "id" in template
        assert "name" in template
        assert "type" in template
        assert "format" in template
        assert "parameters" in template

        # Second request - cache hit
        response2 = client.get("/api/v1/deliverables/templates")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2

    def test_get_template_success(self, client):
        """Test get specific template with caching"""
        # First get list of templates to find a valid ID
        list_response = client.get("/api/v1/deliverables/templates")
        templates = list_response.json()
        assert len(templates) > 0

        template_id = templates[0]["id"]

        # First request - cache miss
        response1 = client.get(f"/api/v1/deliverables/templates/{template_id}")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - cache hit
        response2 = client.get(f"/api/v1/deliverables/templates/{template_id}")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2
        assert data1["id"] == template_id

    def test_get_template_not_found(self, client):
        """Test get template with invalid ID"""
        response = client.get("/api/v1/deliverables/templates/nonexistent-id")
        assert response.status_code == 404

    def test_generate_from_template_success(self, client, sample_template_parameters):
        """Test generate deliverable from template"""
        # Get a valid template ID
        list_response = client.get("/api/v1/deliverables/templates")
        templates = list_response.json()
        assert len(templates) > 0

        template_id = templates[0]["id"]

        # Generate deliverable from template
        response = client.post(
            f"/api/v1/deliverables/templates/{template_id}/generate",
            json=sample_template_parameters,
        )

        assert response.status_code == 200
        data = response.json()

        assert "id" in data
        assert "type" in data
        assert "title" in data
        assert "format" in data
        assert data["status"] in [
            DeliverableStatus.DRAFT,
            DeliverableStatus.PENDING_REVIEW,
        ]
        assert "download_url" in data

    def test_generate_from_template_not_found(self, client, sample_template_parameters):
        """Test generate from invalid template"""
        response = client.post(
            "/api/v1/deliverables/templates/nonexistent-id/generate",
            json=sample_template_parameters,
        )
        assert response.status_code == 404


class TestDeliverablesHealthAPI:
    """Test deliverables health and monitoring endpoints"""

    def test_get_deliverable_health(self, client):
        """Test deliverable service health endpoint"""
        response = client.get("/api/v1/deliverables/health")
        assert response.status_code == 200
        data = response.json()

        assert "service" in data
        assert "status" in data
        assert data["service"] == "DeliverableService"
        assert "total_deliverables" in data
        assert "pending_review" in data
        assert "published" in data
        assert "available_templates" in data


class TestDeliverablesPaginationAndFiltering:
    """Test pagination and filtering functionality"""

    def test_pagination_functionality(self, client, sample_deliverable_request):
        """Test deliverables pagination"""
        # Create multiple deliverables
        for i in range(5):
            request = sample_deliverable_request.copy()
            request["title"] = f"Test Report {i:03d}"
            request["case_id"] = i + 1
            client.post("/api/v1/deliverables/", json=request)

        # Test pagination
        response = client.get("/api/v1/deliverables/?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        # Test different page
        response = client.get("/api/v1/deliverables/?page=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_multiple_format_support(self, client):
        """Test creating deliverables in different formats"""
        formats = ["pdf", "html", "json", "csv"]

        for format_type in formats:
            request = {
                "type": "case_report",
                "title": f"Test Report - {format_type.upper()}",
                "format": format_type,
                "auto_generate": True,
            }

            response = client.post("/api/v1/deliverables/", json=request)
            assert response.status_code == 201
            data = response.json()
            assert data["format"] == format_type

    def test_cache_invalidation_scenarios(self, client, sample_deliverable_request):
        """Test cache invalidation on create/update/delete operations"""
        # Test deliverables cache invalidation
        initial_response = client.get("/api/v1/deliverables/")
        initial_count = len(initial_response.json())

        # Create new deliverable
        client.post("/api/v1/deliverables/", json=sample_deliverable_request)

        # List should reflect new deliverable
        updated_response = client.get("/api/v1/deliverables/")
        updated_count = len(updated_response.json())
        assert updated_count > initial_count

    def test_concurrent_deliverable_operations(
        self, client, sample_deliverable_request
    ):
        """Test concurrent operations for thread safety"""
        # Create deliverable
        create_response = client.post(
            "/api/v1/deliverables/", json=sample_deliverable_request
        )
        deliverable_id = create_response.json()["id"]

        # Simulate concurrent reads
        responses = []
        for i in range(5):
            response = client.get(f"/api/v1/deliverables/{deliverable_id}")
            responses.append(response)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["id"] == deliverable_id

    def test_error_handling(self, client):
        """Test error handling in various scenarios"""
        # Test invalid JSON
        response = client.post("/api/v1/deliverables/", data="invalid json")
        assert response.status_code == 422

        # Test invalid query parameters
        response = client.get("/api/v1/deliverables/?page=-1")
        assert response.status_code == 422

        response = client.get("/api/v1/deliverables/?limit=1000")
        assert response.status_code == 422

        # Test invalid deliverable type
        invalid_request = {"type": "invalid_type", "title": "Test", "format": "pdf"}
        response = client.post("/api/v1/deliverables/", json=invalid_request)
        assert response.status_code == 422
