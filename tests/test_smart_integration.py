"""
Integration tests for SMART on FHIR endpoints
"""

import pytest
from fastapi.testclient import TestClient
from urllib.parse import urlparse, parse_qs

from main import app


client = TestClient(app)


class TestSMARTIntegration:
    """Test SMART on FHIR integration"""
    
    def test_smart_configuration_endpoint(self):
        """Test SMART well-known configuration"""
        response = client.get("/smart/.well-known/smart-configuration")
        assert response.status_code == 200
        
        data = response.json()
        assert "authorization_endpoint" in data
        assert "token_endpoint" in data
        assert "scopes_supported" in data
        assert "capabilities" in data
        
        # Check required SMART capabilities
        capabilities = data["capabilities"]
        assert "launch-ehr" in capabilities
        assert "client-public" in capabilities
    
    def test_smart_standalone_launch(self):
        """Test standalone app launch"""
        response = client.get("/smart/standalone", allow_redirects=False)
        assert response.status_code in [302, 307]
        
        # Should redirect to authorization endpoint
        location = response.headers.get("location", "")
        assert location.startswith("http")
        
        # Parse redirect URL
        parsed = urlparse(location)
        query_params = parse_qs(parsed.query)
        
        # Check required OAuth parameters
        assert "response_type" in query_params
        assert "client_id" in query_params
        assert "redirect_uri" in query_params
        assert "scope" in query_params
        assert "state" in query_params
        assert "aud" in query_params
    
    def test_smart_ehr_launch(self):
        """Test EHR-initiated launch"""
        launch_params = {
            "iss": "https://r4.smarthealthit.org",
            "launch": "test-launch-token"
        }
        
        response = client.get("/smart/launch", params=launch_params, allow_redirects=False)
        assert response.status_code in [302, 307, 400]
        
        if response.status_code in [302, 307]:
            location = response.headers.get("location", "")
            assert location.startswith("http")
            
            # Parse redirect URL
            parsed = urlparse(location)
            query_params = parse_qs(parsed.query)
            
            # Should include launch parameter
            assert "launch" in query_params
            assert query_params["launch"][0] == "test-launch-token"
    
    def test_smart_authorization_endpoint(self):
        """Test authorization endpoint"""
        auth_params = {
            "response_type": "code",
            "client_id": "test-client",
            "redirect_uri": "http://localhost:8000/smart/callback",
            "scope": "patient/*.read",
            "state": "test-state",
            "aud": "https://r4.smarthealthit.org"
        }
        
        response = client.get("/smart/authorize", params=auth_params)
        assert response.status_code == 200
        
        # Should return consent page
        content = response.text
        assert "authorization" in content.lower() or "consent" in content.lower()
        assert auth_params["client_id"] in content
    
    def test_smart_token_endpoint(self):
        """Test token endpoint"""
        token_data = {
            "grant_type": "authorization_code",
            "code": "test-auth-code",
            "redirect_uri": "http://localhost:8000/smart/callback",
            "client_id": "test-client"
        }
        
        response = client.post("/smart/token", data=token_data)
        # May return 400 if auth code is invalid (expected in test)
        assert response.status_code in [200, 400]
        
        if response.status_code == 400:
            data = response.json()
            assert "error" in data or "Invalid" in data.get("detail", "")
    
    def test_smart_callback_endpoint(self):
        """Test OAuth callback endpoint"""
        callback_params = {
            "code": "test-auth-code",
            "state": "test-state"
        }
        
        response = client.get("/smart/callback", params=callback_params)
        # Will likely return 400 due to invalid state in test
        assert response.status_code in [200, 400]
    
    def test_smart_callback_error_handling(self):
        """Test callback error handling"""
        error_params = {
            "error": "access_denied",
            "error_description": "User denied access",
            "state": "test-state"
        }
        
        response = client.get("/smart/callback", params=error_params)
        assert response.status_code == 400
        
        data = response.json()
        assert "error" in data["detail"].lower()
    
    def test_smart_health_check(self):
        """Test SMART service health check"""
        response = client.get("/smart/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "SMART on FHIR"
        assert "endpoints" in data
    
    def test_smart_demo_page(self):
        """Test SMART demo page"""
        response = client.get("/smart/demo")
        assert response.status_code == 200
        
        content = response.text
        assert "SMART on FHIR" in content
        assert "Demo" in content
        assert "/smart/standalone" in content


@pytest.mark.asyncio
class TestSMARTClientIntegration:
    """Test SMART client directly"""
    
    async def test_smart_client_creation(self):
        """Test SMART client can be created"""
        from infra.smart_client import create_smart_client
        
        client = create_smart_client()
        assert client is not None
        assert client.client_id is not None
        assert client.redirect_uri is not None
        
        await client.close()
    
    async def test_smart_client_configuration_discovery(self):
        """Test SMART configuration discovery"""
        from infra.smart_client import create_smart_client, SMARTError
        
        async with create_smart_client() as client:
            try:
                # Try to discover configuration from SMART sandbox
                config = await client.discover_smart_configuration("https://r4.smarthealthit.org")
                assert config is not None
                assert config.authorization_endpoint is not None
                assert config.token_endpoint is not None
                
            except SMARTError:
                # SMART server may not be available
                pytest.skip("SMART server not available")
    
    async def test_smart_client_authorization_url_building(self):
        """Test authorization URL building"""
        from infra.smart_client import create_smart_client, SMARTError
        
        async with create_smart_client() as client:
            try:
                fhir_url = "https://r4.smarthealthit.org"
                auth_url, session_data = await client.build_authorization_url(
                    fhir_base_url=fhir_url,
                    scopes=["patient/*.read", "openid"]
                )
                
                assert auth_url.startswith("https://")
                assert "response_type=code" in auth_url
                assert "client_id=" in auth_url
                assert "redirect_uri=" in auth_url
                assert "scope=" in auth_url
                assert "state=" in auth_url
                
                assert "state" in session_data
                assert "fhir_base_url" in session_data
                assert session_data["fhir_base_url"] == fhir_url
                
            except SMARTError:
                pytest.skip("SMART server not available")


class TestSMARTErrorHandling:
    """Test SMART error handling"""
    
    def test_invalid_authorization_request(self):
        """Test handling of invalid authorization requests"""
        # Missing required parameters
        response = client.get("/smart/authorize?response_type=code")
        assert response.status_code == 422  # Validation error
    
    def test_invalid_token_request(self):
        """Test handling of invalid token requests"""
        # Missing required parameters
        response = client.post("/smart/token", data={"grant_type": "authorization_code"})
        assert response.status_code == 422  # Validation error
    
    def test_malformed_launch_request(self):
        """Test handling of malformed launch requests"""
        # Missing required parameters
        response = client.get("/smart/launch")
        assert response.status_code == 422  # Validation error


class TestSMARTScopes:
    """Test SMART scope handling"""
    
    def test_smart_scopes_in_configuration(self):
        """Test SMART scopes in configuration"""
        response = client.get("/smart/.well-known/smart-configuration")
        assert response.status_code == 200
        
        data = response.json()
        scopes = data["scopes_supported"]
        
        # Check for common SMART scopes
        assert "patient/*.read" in scopes
        assert "user/*.read" in scopes
        assert "openid" in scopes
        assert "profile" in scopes
    
    def test_launch_context_scopes(self):
        """Test launch context scopes"""
        launch_params = {
            "iss": "https://r4.smarthealthit.org",
            "launch": "test-launch-token"
        }
        
        response = client.get("/smart/launch", params=launch_params, allow_redirects=False)
        
        if response.status_code in [302, 307]:
            location = response.headers.get("location", "")
            # Should include launch scope
            assert "launch" in location


class TestSMARTSecurity:
    """Test SMART security features"""
    
    def test_pkce_support(self):
        """Test PKCE (Proof Key for Code Exchange) support"""
        response = client.get("/smart/.well-known/smart-configuration")
        assert response.status_code == 200
        
        data = response.json()
        assert "code_challenge_methods_supported" in data
        assert "S256" in data["code_challenge_methods_supported"]
    
    def test_state_parameter_validation(self):
        """Test state parameter validation"""
        # Callback with invalid state should fail
        callback_params = {
            "code": "test-code",
            "state": "invalid-state"
        }
        
        response = client.get("/smart/callback", params=callback_params)
        assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
