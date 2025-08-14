"""
End-to-end tests for Sync API
Tests both cache-hit and cache-miss scenarios for sync jobs and messages
"""

import fakeredis
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from apps.surge.core.cache import cache_client
from apps.surge.core.database import Base, get_db
from apps.surge.core.services.sync_service import SyncStatus
from apps.surge.main import app


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
def sample_sync_request():
    return {
        "resource_type": "cases",
        "resource_id": "CASE-001",
        "target_system": "external_system",
        "sync_type": "full",
        "priority": "medium",
        "metadata": {"batch_size": 100},
    }


@pytest.fixture
def sample_message_request():
    return {
        "type": "case_update",
        "recipient_id": "USER-001",
        "title": "Case Update Notification",
        "content": "Case CASE-001 has been updated",
        "priority": "medium",
        "metadata": {"case_id": "CASE-001"},
    }


class TestSyncJobsAPI:
    """Test sync jobs API endpoints with cache scenarios"""

    def test_create_sync_job_success(self, client, sample_sync_request):
        """Test successful sync job creation"""
        response = client.post("/api/v1/sync/jobs", json=sample_sync_request)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["resource_type"] == sample_sync_request["resource_type"]
        assert data["resource_id"] == sample_sync_request["resource_id"]
        assert data["target_system"] == sample_sync_request["target_system"]
        assert data["sync_type"] == sample_sync_request["sync_type"]
        assert data["priority"] == sample_sync_request["priority"]
        assert data["status"] in [
            SyncStatus.PENDING,
            SyncStatus.IN_PROGRESS,
            SyncStatus.COMPLETED,
        ]
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_sync_job_missing_required_fields(self, client):
        """Test sync job creation with missing required fields"""
        incomplete_data = {
            "resource_type": "cases"
            # Missing target_system
        }

        response = client.post("/api/v1/sync/jobs", json=incomplete_data)
        assert response.status_code == 422

    def test_list_sync_jobs_cache_scenarios(self, client, sample_sync_request):
        """Test list sync jobs with cache miss then hit scenario"""
        # Create a sync job first
        create_response = client.post("/api/v1/sync/jobs", json=sample_sync_request)
        assert create_response.status_code == 201

        # First request - cache miss
        response1 = client.get("/api/v1/sync/jobs")
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list)
        assert len(data1) > 0

        # Second request - cache hit
        response2 = client.get("/api/v1/sync/jobs")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical (within cache TTL)
        assert data1 == data2

    def test_list_sync_jobs_with_filters(self, client, sample_sync_request):
        """Test list sync jobs with filters"""
        # Create a sync job
        client.post("/api/v1/sync/jobs", json=sample_sync_request)

        # Test resource type filter
        response = client.get(
            f"/api/v1/sync/jobs?resource_type={sample_sync_request['resource_type']}"
        )
        assert response.status_code == 200
        data = response.json()
        for job in data:
            assert job["resource_type"] == sample_sync_request["resource_type"]

        # Test target system filter
        response = client.get(
            f"/api/v1/sync/jobs?target_system={sample_sync_request['target_system']}"
        )
        assert response.status_code == 200
        data = response.json()
        for job in data:
            assert job["target_system"] == sample_sync_request["target_system"]

    def test_get_sync_job_success(self, client, sample_sync_request):
        """Test get sync job with cache scenarios"""
        # Create a sync job
        create_response = client.post("/api/v1/sync/jobs", json=sample_sync_request)
        job_id = create_response.json()["id"]

        # First request - cache miss
        response1 = client.get(f"/api/v1/sync/jobs/{job_id}")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - cache hit
        response2 = client.get(f"/api/v1/sync/jobs/{job_id}")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2
        assert data1["id"] == job_id

    def test_get_sync_job_not_found(self, client):
        """Test get sync job with invalid ID"""
        response = client.get("/api/v1/sync/jobs/nonexistent-id")
        assert response.status_code == 404

    def test_cancel_sync_job_success(self, client, sample_sync_request):
        """Test successful sync job cancellation"""
        # Create a sync job
        create_response = client.post("/api/v1/sync/jobs", json=sample_sync_request)
        job_id = create_response.json()["id"]

        # Cancel the job
        response = client.put(f"/api/v1/sync/jobs/{job_id}/cancel")

        # Should succeed if job is cancellable, or return 400 if already completed
        assert response.status_code in [200, 400]

        if response.status_code == 200:
            data = response.json()
            assert data["success"] == True

    def test_cancel_sync_job_idempotent(self, client, sample_sync_request):
        """Test that cancel operations are idempotent"""
        # Create a sync job
        create_response = client.post("/api/v1/sync/jobs", json=sample_sync_request)
        job_id = create_response.json()["id"]

        # Cancel multiple times
        response1 = client.put(f"/api/v1/sync/jobs/{job_id}/cancel")
        response2 = client.put(f"/api/v1/sync/jobs/{job_id}/cancel")

        # Both should have same effect (idempotent)
        assert response1.status_code in [200, 400]
        assert response2.status_code in [200, 400]

    def test_cancel_sync_job_not_found(self, client):
        """Test cancel sync job with invalid ID"""
        response = client.put("/api/v1/sync/jobs/nonexistent-id/cancel")
        assert response.status_code == 400


class TestMessagesAPI:
    """Test messages API endpoints with cache scenarios"""

    def test_create_message_success(self, client, sample_message_request):
        """Test successful message creation"""
        response = client.post("/api/v1/sync/messages", json=sample_message_request)

        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["type"] == sample_message_request["type"]
        assert data["recipient_id"] == sample_message_request["recipient_id"]
        assert data["title"] == sample_message_request["title"]
        assert data["content"] == sample_message_request["content"]
        assert data["priority"] == sample_message_request["priority"]
        assert data["status"] == "unread"
        assert "created_at" in data

    def test_create_message_missing_required_fields(self, client):
        """Test message creation with missing required fields"""
        incomplete_data = {
            "type": "case_update",
            "title": "Test Message",
            # Missing content
        }

        response = client.post("/api/v1/sync/messages", json=incomplete_data)
        assert response.status_code == 422

    def test_list_messages_cache_scenarios(self, client, sample_message_request):
        """Test list messages with cache scenarios"""
        # Create a message first
        create_response = client.post(
            "/api/v1/sync/messages", json=sample_message_request
        )
        assert create_response.status_code == 201

        # First request - cache miss
        response1 = client.get("/api/v1/sync/messages")
        assert response1.status_code == 200
        data1 = response1.json()
        assert isinstance(data1, list)
        assert len(data1) > 0

        # Second request - cache hit
        response2 = client.get("/api/v1/sync/messages")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2

    def test_list_messages_with_filters(self, client, sample_message_request):
        """Test list messages with filters"""
        # Create a message
        client.post("/api/v1/sync/messages", json=sample_message_request)

        # Test recipient filter
        response = client.get(
            f"/api/v1/sync/messages?recipient_id={sample_message_request['recipient_id']}"
        )
        assert response.status_code == 200
        data = response.json()
        for message in data:
            assert message["recipient_id"] == sample_message_request["recipient_id"]

        # Test type filter
        response = client.get(
            f"/api/v1/sync/messages?type={sample_message_request['type']}"
        )
        assert response.status_code == 200
        data = response.json()
        for message in data:
            assert message["type"] == sample_message_request["type"]

        # Test status filter
        response = client.get("/api/v1/sync/messages?status=unread")
        assert response.status_code == 200
        data = response.json()
        for message in data:
            assert message["status"] == "unread"

    def test_get_message_success(self, client, sample_message_request):
        """Test get message with cache scenarios"""
        # Create a message
        create_response = client.post(
            "/api/v1/sync/messages", json=sample_message_request
        )
        message_id = create_response.json()["id"]

        # First request - cache miss
        response1 = client.get(f"/api/v1/sync/messages/{message_id}")
        assert response1.status_code == 200
        data1 = response1.json()

        # Second request - cache hit
        response2 = client.get(f"/api/v1/sync/messages/{message_id}")
        assert response2.status_code == 200
        data2 = response2.json()

        # Results should be identical
        assert data1 == data2
        assert data1["id"] == message_id

    def test_get_message_not_found(self, client):
        """Test get message with invalid ID"""
        response = client.get("/api/v1/sync/messages/nonexistent-id")
        assert response.status_code == 404

    def test_mark_message_read_success(self, client, sample_message_request):
        """Test marking message as read"""
        # Create a message
        create_response = client.post(
            "/api/v1/sync/messages", json=sample_message_request
        )
        message_id = create_response.json()["id"]

        # Mark as read
        response = client.put(f"/api/v1/sync/messages/{message_id}/read")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True

        # Verify message is marked as read
        get_response = client.get(f"/api/v1/sync/messages/{message_id}")
        message_data = get_response.json()
        assert message_data["status"] == "read"
        assert "read_at" in message_data

    def test_mark_message_read_idempotent(self, client, sample_message_request):
        """Test that marking as read is idempotent"""
        # Create a message
        create_response = client.post(
            "/api/v1/sync/messages", json=sample_message_request
        )
        message_id = create_response.json()["id"]

        # Mark as read multiple times
        response1 = client.put(f"/api/v1/sync/messages/{message_id}/read")
        response2 = client.put(f"/api/v1/sync/messages/{message_id}/read")

        # First should succeed, second should indicate already read
        assert response1.status_code == 200
        assert response2.status_code in [200, 404]  # 404 if already read

    def test_delete_message_success(self, client, sample_message_request):
        """Test successful message deletion"""
        # Create a message
        create_response = client.post(
            "/api/v1/sync/messages", json=sample_message_request
        )
        message_id = create_response.json()["id"]

        # Delete the message
        response = client.delete(f"/api/v1/sync/messages/{message_id}")
        assert response.status_code == 204

        # Verify message is deleted
        get_response = client.get(f"/api/v1/sync/messages/{message_id}")
        assert get_response.status_code == 404

    def test_delete_message_idempotent(self, client, sample_message_request):
        """Test that delete operations are idempotent"""
        # Create a message
        create_response = client.post(
            "/api/v1/sync/messages", json=sample_message_request
        )
        message_id = create_response.json()["id"]

        # Delete multiple times
        response1 = client.delete(f"/api/v1/sync/messages/{message_id}")
        response2 = client.delete(f"/api/v1/sync/messages/{message_id}")

        # First should succeed, second should return 404 (idempotent)
        assert response1.status_code == 204
        assert response2.status_code == 404


class TestSyncStatusAPI:
    """Test sync status and health endpoints"""

    def test_get_sync_status_success(self, client, sample_sync_request):
        """Test get sync status for resource"""
        # Create a sync job first
        client.post("/api/v1/sync/jobs", json=sample_sync_request)

        # Get sync status
        response = client.get(
            f"/api/v1/sync/status/{sample_sync_request['resource_type']}"
        )
        assert response.status_code == 200
        data = response.json()

        assert "resource_type" in data
        assert "status" in data
        assert data["resource_type"] == sample_sync_request["resource_type"]

    def test_get_sync_status_with_resource_id(self, client, sample_sync_request):
        """Test get sync status for specific resource"""
        # Create a sync job first
        client.post("/api/v1/sync/jobs", json=sample_sync_request)

        # Get sync status for specific resource
        response = client.get(
            f"/api/v1/sync/status/{sample_sync_request['resource_type']}?"
            f"resource_id={sample_sync_request['resource_id']}"
        )
        assert response.status_code == 200
        data = response.json()

        assert data["resource_type"] == sample_sync_request["resource_type"]
        assert data["resource_id"] == sample_sync_request["resource_id"]

    def test_get_sync_health(self, client):
        """Test sync service health endpoint"""
        response = client.get("/api/v1/sync/health")
        assert response.status_code == 200
        data = response.json()

        assert "service" in data
        assert "status" in data
        assert data["service"] == "SyncService"
        assert "active_sync_jobs" in data
        assert "total_messages" in data
        assert "unread_messages" in data

    def test_pagination_functionality(
        self, client, sample_sync_request, sample_message_request
    ):
        """Test pagination for sync jobs and messages"""
        # Create multiple sync jobs
        for i in range(5):
            request = sample_sync_request.copy()
            request["resource_id"] = f"RESOURCE-{i:03d}"
            client.post("/api/v1/sync/jobs", json=request)

        # Test sync jobs pagination
        response = client.get("/api/v1/sync/jobs?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

        # Create multiple messages
        for i in range(5):
            request = sample_message_request.copy()
            request["title"] = f"Message {i:03d}"
            client.post("/api/v1/sync/messages", json=request)

        # Test messages pagination
        response = client.get("/api/v1/sync/messages?page=1&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_cache_invalidation_scenarios(
        self, client, sample_sync_request, sample_message_request
    ):
        """Test cache invalidation on create/update/delete operations"""
        # Test sync jobs cache invalidation
        initial_response = client.get("/api/v1/sync/jobs")
        initial_count = len(initial_response.json())

        # Create new sync job
        client.post("/api/v1/sync/jobs", json=sample_sync_request)

        # List should reflect new job
        updated_response = client.get("/api/v1/sync/jobs")
        updated_count = len(updated_response.json())
        assert updated_count > initial_count

        # Test messages cache invalidation
        initial_msg_response = client.get("/api/v1/sync/messages")
        initial_msg_count = len(initial_msg_response.json())

        # Create new message
        client.post("/api/v1/sync/messages", json=sample_message_request)

        # List should reflect new message
        updated_msg_response = client.get("/api/v1/sync/messages")
        updated_msg_count = len(updated_msg_response.json())
        assert updated_msg_count > initial_msg_count

    def test_error_handling(self, client):
        """Test error handling in various scenarios"""
        # Test invalid JSON for sync jobs
        response = client.post("/api/v1/sync/jobs", data="invalid json")
        assert response.status_code == 422

        # Test invalid JSON for messages
        response = client.post("/api/v1/sync/messages", data="invalid json")
        assert response.status_code == 422

        # Test invalid query parameters
        response = client.get("/api/v1/sync/jobs?page=-1")
        assert response.status_code == 422

        response = client.get("/api/v1/sync/messages?limit=1000")
        assert response.status_code == 422
