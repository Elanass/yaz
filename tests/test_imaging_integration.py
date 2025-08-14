"""
Integration tests for imaging/PACS endpoints
"""

import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


class TestImagingIntegration:
    """Test imaging/PACS integration"""
    
    def test_imaging_system_info(self):
        """Test PACS system information endpoint"""
        response = client.get("/imaging/system")
        # Should return 200 or 503 (if Orthanc unavailable)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "system" in data
            assert "statistics" in data
            assert data["status"] == "healthy"
    
    def test_imaging_patients_list(self):
        """Test patients list endpoint"""
        response = client.get("/imaging/patients")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "patients" in data
            assert "count" in data
            assert isinstance(data["patients"], list)
    
    def test_imaging_studies_list(self):
        """Test studies list endpoint"""
        response = client.get("/imaging/studies?limit=10")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "studies" in data
            assert "total" in data
            assert "count" in data
            assert isinstance(data["studies"], list)
    
    def test_imaging_studies_search(self):
        """Test study search endpoint"""
        search_data = {
            "patient_id": "test-patient",
            "study_date": "20250811"
        }
        
        response = client.post("/imaging/studies/search", json=search_data)
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "studies" in data
            assert "count" in data
            assert "search_params" in data
    
    def test_imaging_ohif_viewer_redirect(self):
        """Test OHIF viewer redirect"""
        response = client.get("/imaging/viewer", allow_redirects=False)
        # Should redirect to OHIF viewer
        assert response.status_code in [302, 307, 503]
    
    def test_imaging_health_check(self):
        """Test imaging health check"""
        response = client.get("/imaging/health")
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] in ["healthy", "unhealthy"]
            assert "pacs_server" in data
            assert "statistics" in data


class TestImagingFileOperations:
    """Test imaging file operations"""
    
    def test_dicom_upload_validation(self):
        """Test DICOM upload validation"""
        # Test with non-DICOM file
        files = {"file": ("test.txt", b"not a dicom file", "text/plain")}
        response = client.post("/imaging/upload", files=files)
        
        # Should reject non-DICOM files
        assert response.status_code in [400, 503]
        
        if response.status_code == 400:
            data = response.json()
            assert "DICOM" in data["detail"] or "dcm" in data["detail"]
    
    def test_instance_operations(self):
        """Test instance-level operations"""
        # Test getting non-existent instance
        response = client.get("/imaging/instances/non-existent-id")
        assert response.status_code in [404, 503]


@pytest.mark.asyncio
class TestOrthancClientIntegration:
    """Test Orthanc client directly"""
    
    async def test_orthanc_client_creation(self):
        """Test Orthanc client can be created"""
        from infra.orthanc_client import create_orthanc_client
        
        client = create_orthanc_client()
        assert client is not None
        assert client.base_url is not None
        
        await client.close()
    
    async def test_orthanc_client_system_info(self):
        """Test Orthanc client system info"""
        from infra.orthanc_client import create_orthanc_client, OrthancError
        
        async with create_orthanc_client() as client:
            try:
                system_info = await client.get_system()
                assert system_info is not None
                if system_info:
                    assert "Version" in system_info or "Name" in system_info
                    
            except OrthancError:
                # Orthanc server may not be available in test environment
                pytest.skip("Orthanc server not available")
    
    async def test_orthanc_client_statistics(self):
        """Test Orthanc client statistics"""
        from infra.orthanc_client import create_orthanc_client, OrthancError
        
        async with create_orthanc_client() as client:
            try:
                stats = await client.get_statistics()
                assert stats is not None
                if stats:
                    # Statistics should have count fields
                    expected_fields = ["CountStudies", "CountSeries", "CountInstances"]
                    for field in expected_fields:
                        if field in stats:
                            assert isinstance(stats[field], int)
                            
            except OrthancError:
                pytest.skip("Orthanc server not available")


class TestImagingErrorHandling:
    """Test imaging error handling"""
    
    def test_invalid_study_id(self):
        """Test handling of invalid study ID"""
        response = client.get("/imaging/studies/invalid-study-id")
        assert response.status_code in [404, 503]
    
    def test_invalid_patient_id(self):
        """Test handling of invalid patient ID"""
        response = client.get("/imaging/patients/invalid-patient-id")
        assert response.status_code in [404, 503]
    
    def test_malformed_search_request(self):
        """Test handling of malformed search requests"""
        invalid_data = {"invalid_field": "invalid_value"}
        response = client.post("/imaging/studies/search", json=invalid_data)
        # Should still work but return empty results
        assert response.status_code in [200, 503]


class TestOHIFIntegration:
    """Test OHIF viewer integration"""
    
    def test_ohif_viewer_access(self):
        """Test basic OHIF viewer access"""
        response = client.get("/imaging/viewer", allow_redirects=False)
        # Should redirect to OHIF or return service unavailable
        assert response.status_code in [302, 307, 503]
        
        if response.status_code in [302, 307]:
            location = response.headers.get("location", "")
            # Should redirect to localhost:3000 (default OHIF)
            assert "3000" in location or "ohif" in location.lower()
    
    def test_ohif_study_data_endpoint(self):
        """Test OHIF study data endpoint"""
        response = client.get("/imaging/studies/test-study-id/ohif-data")
        # Study may not exist, but endpoint should respond
        assert response.status_code in [200, 404, 503]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
