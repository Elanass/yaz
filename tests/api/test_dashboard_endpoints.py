import pytest
from fastapi.testclient import TestClient
from surgify.main import app

client = TestClient(app)


class TestDashboardEndpoints:
    def test_get_metrics(self):
        """Test dashboard metrics endpoint."""
        response = client.get("/api/v1/dashboard/dashboard/metrics")
        assert response.status_code == 200

        data = response.json()
        assert "success_rate" in data
        assert "complication_rate" in data
        assert "average_surgery_time" in data

        # Validate data types
        assert isinstance(data["success_rate"], float)
        assert isinstance(data["complication_rate"], float)
        assert isinstance(data["average_surgery_time"], float)

    def test_get_trends(self):
        """Test dashboard trends endpoint."""
        response = client.get("/api/v1/dashboard/dashboard/trends")
        assert response.status_code == 200

        data = response.json()
        assert "daily" in data
        assert "weekly" in data
        assert "monthly" in data

        # Validate data types
        assert isinstance(data["daily"], list)
        assert isinstance(data["weekly"], list)
        assert isinstance(data["monthly"], list)

    def test_export_report(self):
        """Test dashboard report export endpoint."""
        response = client.get("/api/v1/dashboard/dashboard/export")
        assert response.status_code == 200

        data = response.json()
        assert "report_path" in data
        assert isinstance(data["report_path"], str)
