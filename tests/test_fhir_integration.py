"""
Integration tests for FHIR proxy endpoints
"""

import pytest
import httpx
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class TestFHIRIntegration:
    """Test FHIR proxy integration"""
    
    def test_fhir_metadata_endpoint(self):
        """Test FHIR metadata endpoint"""
        response = client.get("/fhir/metadata")
        # Should return 200 or 503 (if FHIR server unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "resourceType" in data
            assert data["resourceType"] == "CapabilityStatement"
    
    def test_fhir_patient_search(self):
        """Test patient search endpoint"""
        response = client.get("/fhir/Patient?_count=1")
        # Should return 200 or 503 (if FHIR server unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "resourceType" in data
            assert data["resourceType"] == "Bundle"
    
    def test_fhir_patient_create(self):
        """Test patient creation"""
        patient_data = {
            "resourceType": "Patient",
            "name": [{
                "family": "TestFamily",
                "given": ["TestGiven"]
            }],
            "gender": "unknown"
        }
        
        response = client.post("/fhir/Patient", json=patient_data)
        # Should return 201, 400, or 503
        assert response.status_code in [201, 400, 503]
    
    def test_fhir_observation_search(self):
        """Test observation search"""
        response = client.get("/fhir/Observation?_count=1")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "resourceType" in data
            assert data["resourceType"] == "Bundle"
    
    def test_fhir_questionnaire_endpoints(self):
        """Test questionnaire endpoints"""
        # Search questionnaires
        response = client.get("/fhir/Questionnaire?status=active&_count=1")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "resourceType" in data
            assert data["resourceType"] == "Bundle"
    
    def test_fhir_smart_configuration(self):
        """Test SMART configuration endpoint"""
        response = client.get("/fhir/.well-known/smart-configuration")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "authorization_endpoint" in data
            assert "token_endpoint" in data
    
    def test_fhir_health_check(self):
        """Test FHIR health check"""
        response = client.get("/fhir/health")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] in ["healthy", "unhealthy"]


@pytest.mark.asyncio
class TestFHIRClientIntegration:
    """Test FHIR client directly"""
    
    async def test_fhir_client_creation(self):
        """Test FHIR client can be created"""
        from infra.fhir_client import create_fhir_client
        
        client = create_fhir_client()
        assert client is not None
        assert client.base_url is not None
        
        await client.close()
    
    async def test_fhir_client_metadata(self):
        """Test FHIR client metadata retrieval"""
        from infra.fhir_client import create_fhir_client, FHIRError
        
        async with create_fhir_client() as client:
            try:
                metadata = await client.get_metadata()
                assert metadata is not None
                if metadata:
                    assert "resourceType" in metadata
            except FHIRError:
                # FHIR server may not be available in test environment
                pytest.skip("FHIR server not available")
    
    async def test_fhir_client_patient_operations(self):
        """Test FHIR client patient operations"""
        from infra.fhir_client import create_fhir_client, FHIRError
        
        async with create_fhir_client() as client:
            try:
                # Search patients
                bundle = await client.search_patients(_count=1)
                assert bundle is not None
                assert bundle.resourceType == "Bundle"
                
            except FHIRError:
                pytest.skip("FHIR server not available")


class TestFHIRErrorHandling:
    """Test FHIR error handling"""
    
    def test_invalid_fhir_resource_type(self):
        """Test handling of invalid resource type"""
        response = client.get("/fhir/InvalidResource/123")
        # Should return error response
        assert response.status_code in [400, 404, 503]
    
    def test_malformed_fhir_request(self):
        """Test handling of malformed requests"""
        invalid_data = {"invalid": "data"}
        response = client.post("/fhir/Patient", json=invalid_data)
        assert response.status_code in [400, 503]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
