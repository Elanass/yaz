"""FHIR Client - Healthcare Integration Infrastructure

Provides a clean interface to FHIR backends (Medplum, HAPI FHIR, etc.)
with authentication, error handling, and response parsing.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FHIRError(Exception):
    """FHIR-specific exception"""
    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class FHIRBundle(BaseModel):
    """FHIR Bundle response model"""
    resourceType: str = "Bundle"
    type: str
    total: Optional[int] = None
    entry: List[Dict[str, Any]] = Field(default_factory=list)
    link: List[Dict[str, str]] = Field(default_factory=list)


class FHIRClient:
    """
    FHIR Client for healthcare data integration
    
    Supports:
    - Patient resources
    - Encounter management  
    - Observation data
    - Questionnaire/QuestionnaireResponse
    - Custom resource types
    """
    
    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        timeout: int = 30,
        verify_ssl: bool = True
    ):
        self.base_url = base_url.rstrip('/')
        self.token = token
        self.timeout = timeout
        
        # HTTP client with proper headers
        headers = {
            "Accept": "application/fhir+json",
            "Content-Type": "application/fhir+json",
        }
        
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
            
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=timeout,
            verify=verify_ssl
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    def _url(self, path: str) -> str:
        """Build full URL for FHIR endpoint"""
        return urljoin(self.base_url + "/", path.lstrip('/'))
    
    async def _request(
        self, 
        method: str, 
        path: str, 
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make authenticated FHIR request"""
        url = self._url(path)
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            
            # Log request for debugging
            logger.debug(f"FHIR {method} {url} -> {response.status_code}")
            
            # Handle FHIR-specific status codes
            if response.status_code == 404:
                return None
            
            if not response.is_success:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    pass
                    
                raise FHIRError(
                    f"FHIR request failed: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=error_data
                )
            
            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError:
                raise FHIRError("Invalid JSON response from FHIR server")
                
        except httpx.RequestError as e:
            raise FHIRError(f"Network error: {str(e)}")
    
    # Metadata & Capability
    async def get_metadata(self) -> Dict[str, Any]:
        """Get FHIR server capability statement"""
        return await self._request("GET", "metadata")
    
    async def get_well_known_smart_configuration(self) -> Dict[str, Any]:
        """Get SMART on FHIR configuration"""
        return await self._request("GET", ".well-known/smart-configuration")
    
    # Patient Resources
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID"""
        return await self._request("GET", f"Patient/{patient_id}")
    
    async def search_patients(
        self, 
        name: Optional[str] = None,
        identifier: Optional[str] = None,
        birthdate: Optional[str] = None,
        **kwargs
    ) -> FHIRBundle:
        """Search patients with filters"""
        params = {}
        
        if name:
            params["name"] = name
        if identifier:
            params["identifier"] = identifier
        if birthdate:
            params["birthdate"] = birthdate
            
        # Add any additional search parameters
        params.update(kwargs)
        
        result = await self._request("GET", "Patient", params=params)
        return FHIRBundle(**result) if result else FHIRBundle(type="searchset")
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new patient"""
        patient_data["resourceType"] = "Patient"
        return await self._request("POST", "Patient", data=patient_data)
    
    # Observation Resources
    async def get_observation(self, observation_id: str) -> Optional[Dict[str, Any]]:
        """Get observation by ID"""
        return await self._request("GET", f"Observation/{observation_id}")
    
    async def search_observations(
        self,
        patient: Optional[str] = None,
        code: Optional[str] = None,
        date: Optional[str] = None,
        **kwargs
    ) -> FHIRBundle:
        """Search observations"""
        params = {}
        
        if patient:
            params["subject"] = f"Patient/{patient}"
        if code:
            params["code"] = code
        if date:
            params["date"] = date
            
        params.update(kwargs)
        
        result = await self._request("GET", "Observation", params=params)
        return FHIRBundle(**result) if result else FHIRBundle(type="searchset")
    
    async def create_observation(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new observation"""
        observation_data["resourceType"] = "Observation"
        return await self._request("POST", "Observation", data=observation_data)
    
    # Questionnaire & QuestionnaireResponse
    async def get_questionnaire(self, questionnaire_id: str) -> Optional[Dict[str, Any]]:
        """Get questionnaire by ID"""
        return await self._request("GET", f"Questionnaire/{questionnaire_id}")
    
    async def search_questionnaires(
        self,
        url: Optional[str] = None,
        status: str = "active",
        **kwargs
    ) -> FHIRBundle:
        """Search questionnaires"""
        params = {"status": status}
        
        if url:
            params["url"] = url
            
        params.update(kwargs)
        
        result = await self._request("GET", "Questionnaire", params=params)
        return FHIRBundle(**result) if result else FHIRBundle(type="searchset")
    
    async def create_questionnaire(self, questionnaire_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new questionnaire"""
        questionnaire_data["resourceType"] = "Questionnaire"
        return await self._request("POST", "Questionnaire", data=questionnaire_data)
    
    async def get_questionnaire_response(self, response_id: str) -> Optional[Dict[str, Any]]:
        """Get questionnaire response by ID"""
        return await self._request("GET", f"QuestionnaireResponse/{response_id}")
    
    async def create_questionnaire_response(
        self, 
        response_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit questionnaire response"""
        response_data["resourceType"] = "QuestionnaireResponse"
        return await self._request("POST", "QuestionnaireResponse", data=response_data)
    
    # Encounter Resources
    async def get_encounter(self, encounter_id: str) -> Optional[Dict[str, Any]]:
        """Get encounter by ID"""
        return await self._request("GET", f"Encounter/{encounter_id}")
    
    async def search_encounters(
        self,
        patient: Optional[str] = None,
        status: Optional[str] = None,
        **kwargs
    ) -> FHIRBundle:
        """Search encounters"""
        params = {}
        
        if patient:
            params["subject"] = f"Patient/{patient}"
        if status:
            params["status"] = status
            
        params.update(kwargs)
        
        result = await self._request("GET", "Encounter", params=params)
        return FHIRBundle(**result) if result else FHIRBundle(type="searchset")
    
    # Generic Resource Operations
    async def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get any resource by type and ID"""
        return await self._request("GET", f"{resource_type}/{resource_id}")
    
    async def search_resources(
        self, 
        resource_type: str, 
        **params
    ) -> FHIRBundle:
        """Search any resource type with parameters"""
        result = await self._request("GET", resource_type, params=params)
        return FHIRBundle(**result) if result else FHIRBundle(type="searchset")
    
    async def create_resource(
        self, 
        resource_type: str, 
        resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create any resource type"""
        resource_data["resourceType"] = resource_type
        return await self._request("POST", resource_type, data=resource_data)
    
    async def update_resource(
        self,
        resource_type: str,
        resource_id: str,
        resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update existing resource"""
        resource_data["resourceType"] = resource_type
        return await self._request("PUT", f"{resource_type}/{resource_id}", data=resource_data)
    
    async def delete_resource(self, resource_type: str, resource_id: str) -> bool:
        """Delete resource"""
        result = await self._request("DELETE", f"{resource_type}/{resource_id}")
        return result is not None
    
    # Batch Operations
    async def post_bundle(self, bundle_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a FHIR bundle (batch/transaction)"""
        bundle_data["resourceType"] = "Bundle"
        return await self._request("POST", "", data=bundle_data)


# Factory function for easy configuration
def create_fhir_client(
    base_url: Optional[str] = None,
    token: Optional[str] = None,
    **kwargs
) -> FHIRClient:
    """
    Create FHIR client from environment or provided config
    """
    import os
    
    base_url = base_url or os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
    token = token or os.getenv("FHIR_TOKEN")
    
    return FHIRClient(base_url=base_url, token=token, **kwargs)


# Example usage
async def example_usage():
    """Example of using the FHIR client"""
    async with create_fhir_client() as client:
        # Get server capabilities
        metadata = await client.get_metadata()
        print(f"FHIR Server: {metadata.get('software', {}).get('name', 'Unknown')}")
        
        # Search patients
        patients = await client.search_patients(name="Smith")
        print(f"Found {patients.total} patients")
        
        # Create observation
        observation = {
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "8302-2",
                    "display": "Body height"
                }]
            },
            "subject": {"reference": "Patient/example"},
            "valueQuantity": {
                "value": 180,
                "unit": "cm",
                "system": "http://unitsofmeasure.org",
                "code": "cm"
            }
        }
        
        result = await client.create_observation(observation)
        print(f"Created observation: {result['id']}")


if __name__ == "__main__":
    asyncio.run(example_usage())
