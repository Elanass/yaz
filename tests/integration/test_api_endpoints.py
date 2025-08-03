"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient

class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client: TestClient):
        """Test health check endpoint returns correct response"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Surgify Decision Precision Engine"
        assert "version" in data
        assert "timestamp" in data

class TestAPIRoot:
    """Test API root endpoints"""
    
    def test_root_redirect(self, client: TestClient):
        """Test root endpoint redirects to Surgify interface"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 200
        assert "Redirecting to Surgify" in response.text

    def test_api_v1_root(self, client: TestClient):
        """Test API v1 root endpoint"""
        response = client.get("/api/v1/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Surgify - Decision Precision Engine"
        assert data["version"] == "2.0.0"
        assert "endpoints" in data
        assert "features" in data

class TestDashboardAPI:
    """Test dashboard API endpoints"""
    
    def test_dashboard_metrics(self, client: TestClient):
        """Test dashboard metrics endpoint"""
        response = client.get("/api/v1/dashboard/metrics")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_cases" in data
        assert "active_cases" in data
        assert "completion_rate" in data

class TestCasesAPI:
    """Test cases API endpoints"""
    
    def test_get_cases_empty(self, client: TestClient):
        """Test getting cases when database is empty"""
        response = client.get("/api/v1/cases/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_get_case_not_found(self, client: TestClient):
        """Test getting non-existent case"""
        response = client.get("/api/v1/cases/999")
        
        assert response.status_code == 404

class TestAuthAPI:
    """Test authentication API endpoints"""
    
    def test_register_user(self, client: TestClient, sample_user_data):
        """Test user registration"""
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Should return 200 or 201 depending on implementation
        assert response.status_code in [200, 201]
        data = response.json()
        assert "message" in data or "user" in data

    def test_register_duplicate_user(self, client: TestClient, sample_user_data):
        """Test registering duplicate user"""
        # Register first user
        client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Try to register same user again
        response = client.post("/api/v1/auth/register", json=sample_user_data)
        
        # Should return error for duplicate
        assert response.status_code in [400, 409]
