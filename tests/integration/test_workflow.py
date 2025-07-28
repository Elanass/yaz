"""
Integration Tests
End-to-end workflow testing
"""

import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.fixture
def client():
    """Test client fixture"""
    app = create_app()
    return TestClient(app)


class TestCompleteWorkflow:
    """Test complete clinical decision workflow"""
    
    def test_complete_clinical_workflow(self, client):
        """Test complete workflow from registration to decision"""
        
        # Step 1: Register a new clinician
        user_data = {
            "email": "dr.smith@hospital.com",
            "password": "securepassword123",
            "full_name": "Dr. Sarah Smith",
            "role": "clinician",
            "organization": "City General Hospital"
        }
        
        register_response = client.post("/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 200
        
        # Step 2: Login to get access token
        login_data = {
            "email": user_data["email"],
            "password": user_data["password"]
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Check available decision engines
        engines_response = client.get("/api/v1/decisions/engines/available", headers=headers)
        assert engines_response.status_code == 200
        
        engines = engines_response.json()["data"]
        engine_types = [e["type"] for e in engines]
        assert "adci" in engine_types
        assert "gastrectomy" in engine_types
        
        # Step 4: Create ADCI decision for T3N1M0 gastric cancer
        adci_request = {
            "engine_type": "adci",
            "patient_data": {
                "age": 68,
                "performance_status": 1,
                "comorbidities": ["hypertension", "diabetes"],
                "bmi": 26.5
            },
            "tumor_data": {
                "stage": "T3N1M0",
                "location": "antrum",
                "histology": "adenocarcinoma",
                "size_cm": 4.5,
                "differentiation": "moderate"
            },
            "context": {
                "institution": "City General Hospital",
                "urgency": "standard",
                "mdt_discussion": True
            }
        }
        
        adci_response = client.post("/api/v1/decisions/analyze", json=adci_request, headers=headers)
        assert adci_response.status_code == 200
        
        adci_data = adci_response.json()["data"]
        assert adci_data["engine_type"] == "adci"
        assert adci_data["status"] == "completed"
        assert adci_data["confidence_score"] > 0.5  # Should be reasonable confidence
        
        adci_decision_id = adci_data["decision_id"]
        
        # Step 5: Create gastrectomy decision based on ADCI recommendation
        gastrectomy_request = {
            "engine_type": "gastrectomy",
            "patient_data": {
                "age": 68,
                "bmi": 26.5,
                "asa_score": 2,
                "performance_status": 1,
                "comorbidities": ["hypertension", "diabetes"]
            },
            "tumor_data": {
                "location": "antrum",
                "size_cm": 4.5,
                "stage": "T3N1M0",
                "histology": "adenocarcinoma"
            },
            "context": {
                "prior_decision_id": adci_decision_id,
                "surgical_team": "experienced"
            }
        }
        
        surgery_response = client.post("/api/v1/decisions/analyze", json=gastrectomy_request, headers=headers)
        assert surgery_response.status_code == 200
        
        surgery_data = surgery_response.json()["data"]
        assert surgery_data["engine_type"] == "gastrectomy"
        assert surgery_data["status"] == "completed"
        
        # Verify surgical recommendation makes sense for T3N1M0
        recommendation = surgery_data["recommendation"]
        assert "procedure" in recommendation
        assert "approach" in recommendation
        assert recommendation["lymphadenectomy"] == "D2"  # Expected for gastric cancer
        
        # Step 6: Retrieve both decisions
        adci_get_response = client.get(f"/api/v1/decisions/{adci_decision_id}", headers=headers)
        assert adci_get_response.status_code == 200
        
        surgery_decision_id = surgery_data["decision_id"]
        surgery_get_response = client.get(f"/api/v1/decisions/{surgery_decision_id}", headers=headers)
        assert surgery_get_response.status_code == 200
        
        # Step 7: List all decisions for this user
        list_response = client.get("/api/v1/decisions/", headers=headers)
        assert list_response.status_code == 200
        
        decisions = list_response.json()["data"]
        assert len(decisions) >= 2
        
        decision_ids = [d["decision_id"] for d in decisions]
        assert adci_decision_id in decision_ids
        assert surgery_decision_id in decision_ids
        
        # Step 8: Get decision statistics
        stats_response = client.get("/api/v1/decisions/stats/summary", headers=headers)
        assert stats_response.status_code == 200
        
        stats = stats_response.json()["data"]
        assert stats["total_decisions"] >= 2
        assert "by_engine" in stats
        assert stats["by_engine"].get("adci", 0) >= 1
        assert stats["by_engine"].get("gastrectomy", 0) >= 1
        
        # Step 9: Verify clinical consistency between decisions
        # ADCI should recommend multimodal therapy for T3N1M0
        adci_rec = adci_data["recommendation"]
        expected_treatments = ["multimodal_therapy", "neoadjuvant_surgery_adjuvant"]
        assert any(treatment in str(adci_rec).lower() for treatment in expected_treatments)
        
        # Gastrectomy should recommend appropriate surgical approach
        surgery_rec = surgery_data["recommendation"]
        assert surgery_rec["procedure"] in ["distal_gastrectomy", "total_gastrectomy"]
        assert surgery_rec["approach"] in ["laparoscopic", "open"]
    
    def test_error_handling_workflow(self, client):
        """Test error handling in clinical workflow"""
        
        # Step 1: Try to access decisions without authentication
        response = client.get("/api/v1/decisions/")
        assert response.status_code == 403
        
        # Step 2: Register and login
        user_data = {
            "email": "dr.test@hospital.com",
            "password": "testpass123",
            "full_name": "Dr. Test",
            "role": "clinician"
        }
        
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Try invalid decision request
        invalid_request = {
            "engine_type": "invalid_engine",
            "patient_data": {},
            "tumor_data": {}
        }
        
        response = client.post("/api/v1/decisions/analyze", json=invalid_request, headers=headers)
        assert response.status_code == 400
        assert "Unknown engine type" in response.json()["detail"]
        
        # Step 4: Try request with missing required data
        incomplete_request = {
            "engine_type": "adci",
            "patient_data": {},  # Missing age
            "tumor_data": {}     # Missing stage
        }
        
        response = client.post("/api/v1/decisions/analyze", json=incomplete_request, headers=headers)
        assert response.status_code == 400
        assert "Validation errors" in response.json()["detail"]
        
        # Step 5: Try to get non-existent decision
        response = client.get("/api/v1/decisions/nonexistent-id", headers=headers)
        assert response.status_code == 404
        assert "Decision not found" in response.json()["detail"]
    
    def test_permission_workflow(self, client):
        """Test permission-based access workflow"""
        
        # Step 1: Register patient user
        patient_data = {
            "email": "patient@example.com",
            "password": "patientpass123",
            "full_name": "John Patient",
            "role": "patient"
        }
        
        client.post("/api/v1/auth/register", json=patient_data)
        
        # Step 2: Login as patient
        login_response = client.post("/api/v1/auth/login", json={
            "email": patient_data["email"],
            "password": patient_data["password"]
        })
        
        patient_token = login_response.json()["data"]["access_token"]
        patient_headers = {"Authorization": f"Bearer {patient_token}"}
        
        # Step 3: Check patient permissions
        perms_response = client.get("/api/v1/auth/permissions", headers=patient_headers)
        assert perms_response.status_code == 200
        
        permissions = perms_response.json()["data"]
        # Patients should have limited permissions
        assert "healthcare:read" in permissions
        assert "healthcare:write" not in permissions
        
        # Step 4: Try to create decision as patient (should fail)
        decision_request = {
            "engine_type": "adci",
            "patient_data": {"age": 65, "performance_status": 1},
            "tumor_data": {"stage": "T2N0M0", "location": "antrum"}
        }
        
        response = client.post("/api/v1/decisions/analyze", json=decision_request, headers=patient_headers)
        assert response.status_code == 403  # Forbidden - patients can't write
        
        # Step 5: Register clinician
        clinician_data = {
            "email": "clinician@hospital.com",
            "password": "clinicianpass123",
            "full_name": "Dr. Clinician",
            "role": "clinician"
        }
        
        client.post("/api/v1/auth/register", json=clinician_data)
        
        # Step 6: Login as clinician and create decision
        login_response = client.post("/api/v1/auth/login", json={
            "email": clinician_data["email"],
            "password": clinician_data["password"]
        })
        
        clinician_token = login_response.json()["data"]["access_token"]
        clinician_headers = {"Authorization": f"Bearer {clinician_token}"}
        
        response = client.post("/api/v1/decisions/analyze", json=decision_request, headers=clinician_headers)
        assert response.status_code == 200  # Should succeed
    
    def test_health_check_workflow(self, client):
        """Test application health check workflow"""
        
        # Health check should work without authentication
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        
        health_data = data["data"]
        assert health_data["status"] in ["healthy", "degraded"]
        assert "version" in health_data
        assert "environment" in health_data
        assert "components" in health_data
        
        # Check that core components are reported
        components = health_data["components"]
        assert "auth" in components
        assert "decisions" in components
    
    def test_api_documentation_workflow(self, client):
        """Test API documentation access"""
        
        # Root endpoint should provide API information
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "endpoints" in data["data"]
        
        endpoints = data["data"]["endpoints"]
        assert "auth" in endpoints
        assert "decisions" in endpoints
        assert "health" in endpoints
        
        # Swagger docs should be accessible
        response = client.get("/api/docs")
        assert response.status_code == 200
        
        # OpenAPI spec should be accessible
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        assert "paths" in openapi_spec
        assert "components" in openapi_spec
