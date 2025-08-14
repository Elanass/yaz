"""SMART on FHIR Client - Healthcare App Integration

Provides SMART on FHIR capabilities including OAuth discovery,
authorization flows, and launch context management.
"""

import asyncio
import json
import logging
import secrets
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, parse_qs

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SMARTError(Exception):
    """SMART on FHIR specific exception"""
    def __init__(self, message: str, error_code: str = None, response: Dict = None):
        super().__init__(message)
        self.error_code = error_code
        self.response = response


class SMARTConfiguration(BaseModel):
    """SMART on FHIR well-known configuration"""
    authorization_endpoint: str
    token_endpoint: str
    introspection_endpoint: Optional[str] = None
    revocation_endpoint: Optional[str] = None
    scopes_supported: List[str] = Field(default_factory=list)
    response_types_supported: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    code_challenge_methods_supported: List[str] = Field(default_factory=list)


class LaunchContext(BaseModel):
    """SMART launch context"""
    patient: Optional[str] = None
    encounter: Optional[str] = None
    user: Optional[str] = None
    practitioner: Optional[str] = None
    location: Optional[str] = None
    organization: Optional[str] = None
    
    
class TokenResponse(BaseModel):
    """OAuth token response"""
    access_token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None
    patient: Optional[str] = None
    encounter: Optional[str] = None
    
    # Additional SMART context
    need_patient_banner: Optional[bool] = None
    smart_style_url: Optional[str] = None


class SMARTClient:
    """
    SMART on FHIR Client for healthcare app integration
    
    Supports:
    - OAuth 2.0 authorization code flow
    - PKCE (Proof Key for Code Exchange)
    - Launch context handling
    - Token management and refresh
    - EHR integration patterns
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: Optional[str] = None,
        redirect_uri: str = "http://localhost:8000/smart/callback",
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.timeout = timeout
        
        self.client = httpx.AsyncClient(
            timeout=timeout,
            verify=verify_ssl
        )
        
        # Cache for configurations
        self._config_cache: Dict[str, SMARTConfiguration] = {}
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def _request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            response = await self.client.request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                **kwargs
            )
            
            logger.debug(f"SMART {method} {url} -> {response.status_code}")
            
            if not response.is_success:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"error_description": response.text}
                
                raise SMARTError(
                    f"SMART request failed: {response.status_code}",
                    error_code=error_data.get("error"),
                    response=error_data
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            raise SMARTError(f"Network error: {str(e)}")
    
    # Discovery and Configuration
    async def discover_smart_configuration(self, fhir_base_url: str) -> SMARTConfiguration:
        """Discover SMART configuration from FHIR server"""
        # Check cache first
        if fhir_base_url in self._config_cache:
            return self._config_cache[fhir_base_url]
        
        # Try well-known endpoint
        well_known_url = urljoin(fhir_base_url.rstrip('/') + '/', '.well-known/smart-configuration')
        
        try:
            config_data = await self._request("GET", well_known_url)
            config = SMARTConfiguration(**config_data)
            self._config_cache[fhir_base_url] = config
            return config
        except SMARTError:
            # Fallback: try to get from CapabilityStatement
            return await self._discover_from_capability_statement(fhir_base_url)
    
    async def _discover_from_capability_statement(self, fhir_base_url: str) -> SMARTConfiguration:
        """Discover SMART config from FHIR CapabilityStatement"""
        metadata_url = urljoin(fhir_base_url.rstrip('/') + '/', 'metadata')
        
        capability = await self._request("GET", metadata_url)
        
        # Extract SMART URLs from security extension
        smart_extension = None
        for rest in capability.get("rest", []):
            security = rest.get("security", {})
            for extension in security.get("extension", []):
                if extension.get("url") == "http://fhir-registry.smarthealthit.org/StructureDefinition/oauth-uris":
                    smart_extension = extension
                    break
        
        if not smart_extension:
            raise SMARTError("SMART configuration not found in CapabilityStatement")
        
        # Parse SMART URLs
        auth_endpoint = None
        token_endpoint = None
        
        for extension in smart_extension.get("extension", []):
            url = extension.get("url")
            value = extension.get("valueUri")
            
            if url == "authorize":
                auth_endpoint = value
            elif url == "token":
                token_endpoint = value
        
        if not auth_endpoint or not token_endpoint:
            raise SMARTError("Required SMART endpoints not found")
        
        config = SMARTConfiguration(
            authorization_endpoint=auth_endpoint,
            token_endpoint=token_endpoint,
            scopes_supported=["patient/*.read", "user/*.read", "openid", "profile"],
            response_types_supported=["code"],
            capabilities=["launch-ehr", "client-public", "client-confidential-symmetric"]
        )
        
        self._config_cache[fhir_base_url] = config
        return config
    
    # Authorization Flow
    def generate_state(self) -> str:
        """Generate secure state parameter"""
        return secrets.token_urlsafe(32)
    
    def generate_pkce_challenge(self) -> Tuple[str, str]:
        """Generate PKCE code verifier and challenge"""
        import base64
        import hashlib
        
        code_verifier = secrets.token_urlsafe(96)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip('=')
        
        return code_verifier, code_challenge
    
    async def build_authorization_url(
        self,
        fhir_base_url: str,
        scopes: List[str] = None,
        launch: Optional[str] = None,
        state: Optional[str] = None,
        use_pkce: bool = True
    ) -> Tuple[str, Dict[str, str]]:
        """
        Build authorization URL for SMART app launch
        
        Returns:
            Tuple of (authorization_url, session_data)
            session_data contains state, code_verifier, etc. to store
        """
        config = await self.discover_smart_configuration(fhir_base_url)
        
        # Default scopes
        if scopes is None:
            scopes = ["patient/*.read", "openid", "profile"]
        
        # Generate secure parameters
        state = state or self.generate_state()
        session_data = {"state": state, "fhir_base_url": fhir_base_url}
        
        # Build authorization parameters
        auth_params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "aud": fhir_base_url
        }
        
        # Add launch context if provided (EHR launch)
        if launch:
            auth_params["launch"] = launch
        
        # Add PKCE if supported
        if use_pkce and "S256" in config.code_challenge_methods_supported:
            code_verifier, code_challenge = self.generate_pkce_challenge()
            auth_params["code_challenge"] = code_challenge
            auth_params["code_challenge_method"] = "S256"
            session_data["code_verifier"] = code_verifier
        
        # Build URL
        auth_url = f"{config.authorization_endpoint}?{urllib.parse.urlencode(auth_params)}"
        
        return auth_url, session_data
    
    async def exchange_code_for_token(
        self,
        authorization_code: str,
        session_data: Dict[str, str]
    ) -> TokenResponse:
        """Exchange authorization code for access token"""
        fhir_base_url = session_data["fhir_base_url"]
        config = await self.discover_smart_configuration(fhir_base_url)
        
        # Build token request
        token_data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id
        }
        
        # Add client secret if available (confidential client)
        if self.client_secret:
            token_data["client_secret"] = self.client_secret
        
        # Add PKCE verifier if used
        if "code_verifier" in session_data:
            token_data["code_verifier"] = session_data["code_verifier"]
        
        # Request token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = await self._request(
            "POST",
            config.token_endpoint,
            data=token_data,
            headers=headers
        )
        
        return TokenResponse(**token_response)
    
    async def refresh_token(
        self,
        refresh_token: str,
        fhir_base_url: str
    ) -> TokenResponse:
        """Refresh access token using refresh token"""
        config = await self.discover_smart_configuration(fhir_base_url)
        
        token_data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id
        }
        
        if self.client_secret:
            token_data["client_secret"] = self.client_secret
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        token_response = await self._request(
            "POST",
            config.token_endpoint,
            data=token_data,
            headers=headers
        )
        
        return TokenResponse(**token_response)
    
    # Launch Context
    def parse_launch_context(self, token_response: TokenResponse) -> LaunchContext:
        """Parse launch context from token response"""
        return LaunchContext(
            patient=token_response.patient,
            encounter=token_response.encounter,
            # Add other context fields as available in token response
        )
    
    # Well-known Configuration Endpoint
    def get_well_known_config(
        self,
        base_url: str,
        client_name: str = "YAZ Healthcare Platform"
    ) -> Dict[str, Any]:
        """Generate well-known SMART configuration for this app"""
        return {
            "authorization_endpoint": f"{base_url}/smart/authorize",
            "token_endpoint": f"{base_url}/smart/token",
            "token_endpoint_auth_methods_supported": [
                "client_secret_basic",
                "client_secret_post"
            ],
            "scopes_supported": [
                "openid",
                "profile",
                "patient/*.read",
                "user/*.read",
                "offline_access"
            ],
            "response_types_supported": ["code"],
            "capabilities": [
                "launch-ehr",
                "launch-standalone", 
                "client-public",
                "client-confidential-symmetric",
                "context-ehr-patient",
                "context-ehr-encounter",
                "context-standalone-patient",
                "permission-offline",
                "permission-patient",
                "permission-user"
            ],
            "code_challenge_methods_supported": ["S256"],
            "grant_types_supported": ["authorization_code", "refresh_token"]
        }


# Factory function for easy configuration
def create_smart_client(
    client_id: Optional[str] = None,
    client_secret: Optional[str] = None,
    redirect_uri: Optional[str] = None,
    **kwargs
) -> SMARTClient:
    """
    Create SMART client from environment or provided config
    """
    import os
    
    client_id = client_id or os.getenv("SMART_CLIENT_ID", "demo-client")
    client_secret = client_secret or os.getenv("SMART_CLIENT_SECRET")
    redirect_uri = redirect_uri or os.getenv("SMART_REDIRECT_URI", "http://localhost:8000/smart/callback")
    
    return SMARTClient(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        **kwargs
    )


# Example usage
async def example_usage():
    """Example of using the SMART client"""
    async with create_smart_client() as client:
        fhir_url = "https://r4.smarthealthit.org"
        
        # Discover SMART configuration
        config = await client.discover_smart_configuration(fhir_url)
        print(f"Authorization endpoint: {config.authorization_endpoint}")
        
        # Build authorization URL
        auth_url, session_data = await client.build_authorization_url(
            fhir_base_url=fhir_url,
            scopes=["patient/*.read", "openid", "profile"]
        )
        
        print(f"Authorization URL: {auth_url}")
        print(f"State: {session_data['state']}")
        
        # In a real app, you would redirect user to auth_url
        # and handle the callback with the authorization code
        
        # Example callback handling:
        # auth_code = "received_from_callback"
        # token_response = await client.exchange_code_for_token(auth_code, session_data)
        # print(f"Access token: {token_response.access_token}")


if __name__ == "__main__":
    asyncio.run(example_usage())
