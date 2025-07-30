"""
HAPI FHIR Adapter

This adapter provides integration with the HAPI FHIR REST API for standardized healthcare
data interchange, allowing interoperability with other FHIR-compliant systems.
"""

import asyncio
import json
import logging
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, TypeVar, Generic

import httpx
from pydantic import BaseModel, Field

from core.config.settings import get_adapter_config
from core.services.base import BaseService
from core.services.logger import Logger


T = TypeVar('T')


class FHIRReference(BaseModel):
    """FHIR reference model"""
    
    reference: str = Field(..., description="Resource reference")
    type: Optional[str] = Field(None, description="Resource type")
    display: Optional[str] = Field(None, description="Display text")


class FHIRCodeableConcept(BaseModel):
    """FHIR codeable concept model"""
    
    coding: List[Dict[str, Any]] = Field(..., description="Coding")
    text: Optional[str] = Field(None, description="Plain text representation")


class FHIRBundle(BaseModel, Generic[T]):
    """FHIR bundle model"""
    
    resourceType: str = Field("Bundle", description="Resource type")
    id: Optional[str] = Field(None, description="Logical id")
    type: str = Field(..., description="Bundle type")
    total: Optional[int] = Field(None, description="Total results")
    link: Optional[List[Dict[str, str]]] = Field(None, description="Links")
    entry: List[Dict[str, Any]] = Field(..., description="Bundle entries")


class HAPIFHIRAdapter(BaseService):
    """HAPI FHIR REST API adapter for healthcare data interoperability"""
    
    def __init__(self):
        super().__init__()
        self.config = get_adapter_config("hapi_fhir")
        self.logger = Logger()
        self.base_url = self.config.get("base_url", "http://localhost:8080/fhir")
        self.auth_type = self.config.get("auth_type", "none")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.token = self.config.get("token")
        self.http_client = self._create_http_client()
    
    def _create_http_client(self) -> httpx.AsyncClient:
        """Create and configure HTTP client"""
        headers = {
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        }
        
        # Add authentication
        if self.auth_type == "basic" and self.username and self.password:
            auth_str = f"{self.username}:{self.password}"
            auth_bytes = auth_str.encode("utf-8")
            auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
            headers["Authorization"] = f"Basic {auth_b64}"
            
        elif self.auth_type == "bearer" and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        
        # Create client with headers
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers=headers,
            timeout=30.0
        )
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Handle API response and convert to dictionary
        
        Args:
            response: The HTTP response
            
        Returns:
            Parsed JSON response as dictionary
            
        Raises:
            Exception: If the request failed
        """
        if response.status_code >= 400:
            self.logger.error(
                f"HAPI FHIR API error: {response.status_code}",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text
            )
            raise Exception(f"HAPI FHIR API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    async def search(
        self,
        resource_type: str,
        params: Dict[str, Any] = None
    ) -> FHIRBundle:
        """
        Search for resources
        
        Args:
            resource_type: Resource type
            params: Search parameters
            
        Returns:
            Bundle of search results
        """
        try:
            response = await self.http_client.get(
                f"/{resource_type}",
                params=params or {}
            )
            
            data = await self._handle_response(response)
            return FHIRBundle(**data)
            
        except Exception as e:
            self.logger.error(
                f"Error searching {resource_type}: {str(e)}",
                exc_info=e,
                resource_type=resource_type,
                params=params
            )
            raise
    
    async def get(self, resource_type: str, id: str) -> Dict[str, Any]:
        """
        Get a resource by ID
        
        Args:
            resource_type: Resource type
            id: Resource ID
            
        Returns:
            The resource
        """
        try:
            response = await self.http_client.get(f"/{resource_type}/{id}")
            
            if response.status_code == 404:
                return None
                
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error getting {resource_type}/{id}: {str(e)}",
                exc_info=e,
                resource_type=resource_type,
                id=id
            )
            raise
    
    async def create(self, resource_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a resource
        
        Args:
            resource_type: Resource type
            data: Resource data
            
        Returns:
            The created resource
        """
        try:
            # Set resource type if not already set
            if "resourceType" not in data:
                data["resourceType"] = resource_type
                
            response = await self.http_client.post(
                f"/{resource_type}",
                json=data
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error creating {resource_type}: {str(e)}",
                exc_info=e,
                resource_type=resource_type
            )
            raise
    
    async def update(
        self,
        resource_type: str,
        id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a resource
        
        Args:
            resource_type: Resource type
            id: Resource ID
            data: Updated resource data
            
        Returns:
            The updated resource
        """
        try:
            # Set resource type and ID if not already set
            if "resourceType" not in data:
                data["resourceType"] = resource_type
                
            if "id" not in data:
                data["id"] = id
                
            response = await self.http_client.put(
                f"/{resource_type}/{id}",
                json=data
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error updating {resource_type}/{id}: {str(e)}",
                exc_info=e,
                resource_type=resource_type,
                id=id
            )
            raise
    
    async def delete(self, resource_type: str, id: str) -> bool:
        """
        Delete a resource
        
        Args:
            resource_type: Resource type
            id: Resource ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.http_client.delete(f"/{resource_type}/{id}")
            return response.status_code < 300
            
        except Exception as e:
            self.logger.error(
                f"Error deleting {resource_type}/{id}: {str(e)}",
                exc_info=e,
                resource_type=resource_type,
                id=id
            )
            raise
    
    async def execute_operation(
        self,
        resource_type: Optional[str],
        id: Optional[str],
        operation: str,
        params: Dict[str, Any] = None,
        body: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute a FHIR operation
        
        Args:
            resource_type: Resource type (or None for system-level operations)
            id: Resource ID (or None for type-level operations)
            operation: Operation name
            params: URL parameters
            body: Request body
            
        Returns:
            Operation result
        """
        try:
            url = ""
            if resource_type:
                url += f"/{resource_type}"
                if id:
                    url += f"/{id}"
            url += f"/${operation}"
            
            if body:
                response = await self.http_client.post(
                    url,
                    params=params or {},
                    json=body
                )
            else:
                response = await self.http_client.get(
                    url,
                    params=params or {}
                )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error executing operation {operation}: {str(e)}",
                exc_info=e,
                resource_type=resource_type,
                id=id,
                operation=operation
            )
            raise
    
    async def search_patients(
        self,
        name: Optional[str] = None,
        identifier: Optional[str] = None,
        birthdate: Optional[str] = None,
        gender: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for patients
        
        Args:
            name: Patient name
            identifier: Patient identifier
            birthdate: Patient birthdate (YYYY-MM-DD)
            gender: Patient gender
            max_results: Maximum number of results
            
        Returns:
            List of matching patients
        """
        params = {"_count": str(max_results)}
        
        if name:
            params["name"] = name
            
        if identifier:
            params["identifier"] = identifier
            
        if birthdate:
            params["birthdate"] = birthdate
            
        if gender:
            params["gender"] = gender
            
        bundle = await self.search("Patient", params)
        
        # Extract patients from bundle
        patients = []
        for entry in bundle.entry:
            if "resource" in entry:
                patients.append(entry["resource"])
                
        return patients
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a patient
        
        Args:
            patient_data: Patient data
            
        Returns:
            The created patient
        """
        return await self.create("Patient", patient_data)
    
    async def get_patient(self, id: str) -> Dict[str, Any]:
        """
        Get a patient by ID
        
        Args:
            id: Patient ID
            
        Returns:
            The patient
        """
        return await self.get("Patient", id)
    
    async def search_observations(
        self,
        patient_id: Optional[str] = None,
        code: Optional[str] = None,
        date: Optional[str] = None,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for observations
        
        Args:
            patient_id: Patient ID
            code: Observation code
            date: Observation date
            max_results: Maximum number of results
            
        Returns:
            List of matching observations
        """
        params = {"_count": str(max_results)}
        
        if patient_id:
            params["subject"] = f"Patient/{patient_id}"
            
        if code:
            params["code"] = code
            
        if date:
            params["date"] = date
            
        bundle = await self.search("Observation", params)
        
        # Extract observations from bundle
        observations = []
        for entry in bundle.entry:
            if "resource" in entry:
                observations.append(entry["resource"])
                
        return observations
    
    async def create_observation(
        self,
        observation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an observation
        
        Args:
            observation_data: Observation data
            
        Returns:
            The created observation
        """
        return await self.create("Observation", observation_data)
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()


class HAPIFHIRClient(BaseService):
    """
    HAPI FHIR REST API client for Decision Precision in Surgery platform
    """
    
    def __init__(self):
        """Initialize the HAPI FHIR client"""
        self.config = get_adapter_config("hapi_fhir")
        self.base_url = self.config.get("base_url", "https://hapi.fhir.org/baseR4")
        self.logger = Logger()
        self.logger.info("HAPI FHIR client initialized")
        
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID"""
        self.logger.info(f"Fetching patient {patient_id} from FHIR server")
        # Implementation details here
        return None
        
    async def search_patients(self, query: str) -> List[Dict[str, Any]]:
        """Search for patients"""
        self.logger.info(f"Searching patients with query: {query}")
        # Implementation details here
        return []


# Create a singleton instance for importing
fhir_client = HAPIFHIRClient()
