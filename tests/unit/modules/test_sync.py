"""
Unit tests for sync module
Tests data synchronization and messaging functionality
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from typing import List

from surgify.api.v1.sync import router
from surgify.core.services.sync_service import (
    SyncService,
    SyncRequest,
    SyncResponse,
    SyncStatus,
    MessageRequest,
    MessageResponse,
    MessageType,
)


class TestSyncService:
    """Test sync service functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.sync_service = SyncService(self.mock_db)

        self.sample_sync_request = SyncRequest(
            sync_type="incremental",
            resource_type="cases",
            source_endpoint="http://external-system/api/cases",
            priority="medium",
        )

    @pytest.mark.asyncio
    async def test_create_sync_job_success(self):
        """Test successful sync job creation"""
        with patch.object(self.sync_service, "_generate_sync_id") as mock_gen_id:
            mock_gen_id.return_value = "sync-123"

            result = await self.sync_service.create_sync_job(
                self.sample_sync_request, "test_user"
            )

            assert isinstance(result, SyncResponse)
            assert result.job_id == "sync-123"
            assert result.status == SyncStatus.PENDING
            assert result.sync_type == "incremental"
            assert result.resource_type == "cases"

    @pytest.mark.asyncio
    async def test_create_sync_job_duplicate_prevention(self):
        """Test prevention of duplicate sync jobs"""
        with patch.object(self.sync_service, "_check_existing_job") as mock_check:
            mock_check.return_value = "existing-job-123"

            result = await self.sync_service.create_sync_job(
                self.sample_sync_request, "test_user"
            )

            # Should return existing job instead of creating new one
            assert result.job_id == "existing-job-123"

    @pytest.mark.asyncio
    async def test_get_sync_job_status(self):
        """Test sync job status retrieval"""
        job_id = "sync-123"

        with patch.object(self.sync_service, "_get_job_from_db") as mock_get_job:
            mock_job = Mock()
            mock_job.job_id = job_id
            mock_job.status = SyncStatus.RUNNING
            mock_job.progress = 0.5
            mock_get_job.return_value = mock_job

            result = await self.sync_service.get_job_status(job_id)

            assert result.job_id == job_id
            assert result.status == SyncStatus.RUNNING
            assert result.progress == 0.5

    @pytest.mark.asyncio
    async def test_get_sync_job_not_found(self):
        """Test sync job not found scenario"""
        with patch.object(self.sync_service, "_get_job_from_db") as mock_get_job:
            mock_get_job.return_value = None

            with pytest.raises(ValueError, match="Sync job not found"):
                await self.sync_service.get_job_status("nonexistent-job")

    @pytest.mark.asyncio
    async def test_process_sync_job_full(self):
        """Test full synchronization processing"""
        job_data = {
            "job_id": "sync-123",
            "sync_type": "full",
            "resource_type": "cases",
            "source_endpoint": "http://external/api/cases",
        }

        with patch.object(self.sync_service, "_fetch_external_data") as mock_fetch:
            mock_fetch.return_value = [{"id": 1, "title": "Test Case"}]

            with patch.object(self.sync_service, "_update_local_data") as mock_update:
                mock_update.return_value = {"processed": 1, "errors": 0}

                result = await self.sync_service.process_sync_job(job_data)

                assert result["status"] == "completed"
                assert result["processed_count"] == 1
                assert result["error_count"] == 0

    @pytest.mark.asyncio
    async def test_process_sync_job_incremental(self):
        """Test incremental synchronization processing"""
        job_data = {
            "job_id": "sync-123",
            "sync_type": "incremental",
            "resource_type": "cases",
            "source_endpoint": "http://external/api/cases",
            "last_sync_timestamp": datetime.now() - timedelta(hours=1),
        }

        with patch.object(self.sync_service, "_fetch_incremental_data") as mock_fetch:
            mock_fetch.return_value = [{"id": 2, "title": "Updated Case"}]

            with patch.object(
                self.sync_service, "_merge_incremental_data"
            ) as mock_merge:
                mock_merge.return_value = {"processed": 1, "updated": 1, "errors": 0}

                result = await self.sync_service.process_sync_job(job_data)

                assert result["status"] == "completed"
                assert result["updated_count"] == 1

    @pytest.mark.asyncio
    async def test_process_sync_job_error_handling(self):
        """Test sync job error handling"""
        job_data = {
            "job_id": "sync-123",
            "sync_type": "full",
            "resource_type": "cases",
            "source_endpoint": "http://unreachable/api/cases",
        }

        with patch.object(self.sync_service, "_fetch_external_data") as mock_fetch:
            mock_fetch.side_effect = Exception("Network error")

            result = await self.sync_service.process_sync_job(job_data)

            assert result["status"] == "failed"
            assert "Network error" in result["error_message"]


class TestSyncConflictResolution:
    """Test sync conflict resolution"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.sync_service = SyncService(self.mock_db)

    @pytest.mark.asyncio
    async def test_resolve_conflict_newer_wins(self):
        """Test conflict resolution with newer-wins strategy"""
        local_data = {
            "id": 1,
            "title": "Local Case",
            "updated_at": datetime.now() - timedelta(minutes=30),
        }

        remote_data = {
            "id": 1,
            "title": "Remote Case",
            "updated_at": datetime.now() - timedelta(minutes=10),
        }

        result = await self.sync_service._resolve_conflict(
            local_data, remote_data, strategy="newer_wins"
        )

        assert result["title"] == "Remote Case"  # Remote is newer

    @pytest.mark.asyncio
    async def test_resolve_conflict_merge_strategy(self):
        """Test conflict resolution with merge strategy"""
        local_data = {
            "id": 1,
            "title": "Local Case",
            "description": "Local description",
            "updated_at": datetime.now() - timedelta(minutes=30),
        }

        remote_data = {
            "id": 1,
            "title": "Remote Case",
            "status": "completed",
            "updated_at": datetime.now() - timedelta(minutes=10),
        }

        result = await self.sync_service._resolve_conflict(
            local_data, remote_data, strategy="merge"
        )

        # Should merge non-conflicting fields
        assert result["description"] == "Local description"
        assert result["status"] == "completed"
        assert result["title"] == "Remote Case"  # Remote wins for conflicts


class TestSyncMessaging:
    """Test sync messaging functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.sync_service = SyncService(self.mock_db)

    @pytest.mark.asyncio
    async def test_send_sync_message(self):
        """Test sending sync messages"""
        message_request = MessageRequest(
            message_type=MessageType.SYNC_STATUS,
            recipient="user@example.com",
            content={"job_id": "sync-123", "status": "completed"},
            priority="high",
        )

        with patch.object(self.sync_service, "_send_message") as mock_send:
            mock_send.return_value = MessageResponse(
                message_id="msg-123", status="sent", sent_at=datetime.now()
            )

            result = await self.sync_service.send_message(message_request)

            assert result.message_id == "msg-123"
            assert result.status == "sent"

    @pytest.mark.asyncio
    async def test_batch_message_sending(self):
        """Test batch message sending"""
        messages = [
            MessageRequest(
                message_type=MessageType.SYNC_COMPLETE,
                recipient=f"user{i}@example.com",
                content={"job_id": f"sync-{i}"},
            )
            for i in range(5)
        ]

        with patch.object(self.sync_service, "_send_batch_messages") as mock_batch:
            mock_batch.return_value = {
                "sent": 5,
                "failed": 0,
                "message_ids": [f"msg-{i}" for i in range(5)],
            }

            result = await self.sync_service.send_batch_messages(messages)

            assert result["sent"] == 5
            assert result["failed"] == 0
            assert len(result["message_ids"]) == 5


@pytest.mark.integration
class TestSyncIntegration:
    """Integration tests for sync functionality"""

    def setup_method(self):
        """Setup integration test fixtures"""
        self.mock_db = Mock()
        self.sync_service = SyncService(self.mock_db)

    @pytest.mark.asyncio
    async def test_full_sync_workflow(self):
        """Test complete sync workflow from creation to completion"""
        # This would be a comprehensive integration test
        # that tests the entire sync process
        pass

    @pytest.mark.asyncio
    async def test_sync_with_real_external_api(self):
        """Test sync with actual external API endpoints"""
        # This would test against real external systems
        # Skip if external systems are not available
        pass

    @pytest.mark.asyncio
    async def test_sync_performance_under_load(self):
        """Test sync performance with large datasets"""
        # Performance testing for sync operations
        pass


class TestSyncAPI:
    """Test sync API endpoints"""

    def setup_method(self):
        """Setup API test fixtures"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    @patch("src.surgify.api.v1.sync.get_sync_service")
    @patch("src.surgify.api.v1.sync.get_current_user")
    def test_create_sync_job_api(self, mock_get_user, mock_get_service):
        """Test create sync job API endpoint"""
        mock_user = Mock()
        mock_user.username = "test_user"
        mock_get_user.return_value = mock_user

        mock_service = AsyncMock()
        mock_service.create_sync_job.return_value = SyncResponse(
            job_id="sync-123",
            status=SyncStatus.PENDING,
            sync_type="incremental",
            resource_type="cases",
        )
        mock_get_service.return_value = mock_service

        response = self.client.post(
            "/jobs",
            json={
                "sync_type": "incremental",
                "resource_type": "cases",
                "source_endpoint": "http://external/api/cases",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["job_id"] == "sync-123"
        assert data["status"] == "pending"

    @patch("src.surgify.api.v1.sync.get_sync_service")
    @patch("src.surgify.api.v1.sync.get_current_user")
    def test_get_sync_jobs_api(self, mock_get_user, mock_get_service):
        """Test get sync jobs API endpoint"""
        mock_user = Mock()
        mock_get_user.return_value = mock_user

        mock_service = Mock()
        mock_service.get_user_sync_jobs.return_value = [
            SyncResponse(
                job_id="sync-123",
                status=SyncStatus.COMPLETED,
                sync_type="full",
                resource_type="cases",
            )
        ]
        mock_get_service.return_value = mock_service

        response = self.client.get("/jobs")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["job_id"] == "sync-123"


class TestSyncEdgeCases:
    """Test sync edge cases and error scenarios"""

    def setup_method(self):
        """Setup test fixtures"""
        self.mock_db = Mock()
        self.sync_service = SyncService(self.mock_db)

    @pytest.mark.asyncio
    async def test_sync_large_dataset(self):
        """Test sync with very large datasets"""
        # Test handling of large data volumes
        large_dataset = [{"id": i, "data": f"data_{i}"} for i in range(10000)]

        with patch.object(self.sync_service, "_fetch_external_data") as mock_fetch:
            mock_fetch.return_value = large_dataset

            with patch.object(self.sync_service, "_process_in_batches") as mock_batch:
                mock_batch.return_value = {"processed": 10000, "errors": 0}

                job_data = {
                    "job_id": "sync-large",
                    "sync_type": "full",
                    "resource_type": "cases",
                }

                result = await self.sync_service.process_sync_job(job_data)

                assert result["processed_count"] == 10000

    @pytest.mark.asyncio
    async def test_sync_network_interruption(self):
        """Test sync behavior during network interruption"""
        job_data = {"job_id": "sync-network-test", "sync_type": "incremental"}

        # Simulate network interruption and recovery
        call_count = 0

        def network_error_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Network timeout")
            return [{"id": 1, "data": "recovered"}]

        with patch.object(self.sync_service, "_fetch_external_data") as mock_fetch:
            mock_fetch.side_effect = network_error_then_success

            with patch.object(self.sync_service, "_retry_with_backoff") as mock_retry:
                mock_retry.return_value = True

                result = await self.sync_service.process_sync_job(job_data)

                # Should eventually succeed after retries
                assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_sync_concurrent_jobs(self):
        """Test behavior with multiple concurrent sync jobs"""
        import asyncio

        job_ids = [f"sync-concurrent-{i}" for i in range(5)]

        async def create_concurrent_job(job_id):
            request = SyncRequest(sync_type="incremental", resource_type="cases")
            return await self.sync_service.create_sync_job(request, "test_user")

        # Create multiple jobs concurrently
        tasks = [create_concurrent_job(job_id) for job_id in job_ids]

        with patch.object(self.sync_service, "_generate_sync_id") as mock_gen_id:
            mock_gen_id.side_effect = job_ids

            results = await asyncio.gather(*tasks)

            # All jobs should be created successfully
            assert len(results) == 5
            assert all(result.status == SyncStatus.PENDING for result in results)
