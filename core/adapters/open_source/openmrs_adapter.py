"""
OpenMRS Adapter

This adapter provides integration with the OpenMRS REST API for patient data management,
allowing synchronization of patient records, encounters, and observations.
"""

import asyncio
import json
import logging
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import httpx
from pydantic import BaseModel, Field, validator

from core.config.settings import get_adapter_config
from core.services.base import BaseService
from core.services.logger import Logger


class OpenMRSPatient(BaseModel):
    """OpenMRS patient model"""
    
    uuid: str = Field(..., description="OpenMRS UUID")
    display: str = Field(..., description="Display name")
    identifiers: List[Dict[str, Any]] = Field([], description="Patient identifiers")
    person: Dict[str, Any] = Field(..., description="Person details")
    voided: bool = Field(False, description="Whether the patient is voided")
    
    @property
    def identifier(self) -> str:
        """Get the primary identifier"""
        for identifier in self.identifiers:
            if identifier.get("preferred", False):
                return identifier.get("identifier", "")
        
        # Fall back to first identifier
        if self.identifiers:
            return self.identifiers[0].get("identifier", "")
            
        return ""
    
    @property
    def name(self) -> str:
        """Get the patient's full name"""
        if not self.person or "names" not in self.person:
            return self.display
            
        names = self.person["names"]
        if not names:
            return self.display
            
        # Get preferred name
        for name in names:
            if name.get("preferred", False):
                return self._format_name(name)
                
        # Fall back to first name
        return self._format_name(names[0])
    
    def _format_name(self, name: Dict[str, Any]) -> str:
        """Format a name object"""
        parts = []
        
        if name.get("givenName"):
            parts.append(name["givenName"])
            
        if name.get("middleName"):
            parts.append(name["middleName"])
            
        if name.get("familyName"):
            parts.append(name["familyName"])
            
        return " ".join(parts) if parts else self.display


class OpenMRSAdapter(BaseService):
    """OpenMRS REST API adapter for patient data management"""
    
    def __init__(self):
        super().__init__()
        self.config = get_adapter_config("openmrs")
        self.logger = Logger()
        self.base_url = self.config.get("base_url", "http://localhost:8080/openmrs/ws/rest/v1")
        self.username = self.config.get("username")
        self.password = self.config.get("password")
        self.http_client = self._create_http_client()
    
    def _create_http_client(self) -> httpx.AsyncClient:
        """Create and configure HTTP client"""
        # Create auth header
        auth_str = f"{self.username}:{self.password}"
        auth_bytes = auth_str.encode("utf-8")
        auth_b64 = base64.b64encode(auth_bytes).decode("utf-8")
        
        # Create client with auth headers
        return httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
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
                f"OpenMRS API error: {response.status_code}",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text
            )
            raise Exception(f"OpenMRS API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    async def search_patients(
        self,
        query: str,
        limit: int = 10,
        include_voided: bool = False
    ) -> List[OpenMRSPatient]:
        """
        Search for patients by name or identifier
        
        Args:
            query: Search query (name or identifier)
            limit: Maximum number of results
            include_voided: Whether to include voided patients
            
        Returns:
            List of matching patients
        """
        try:
            response = await self.http_client.get(
                "/patient",
                params={
                    "q": query,
                    "v": "full",
                    "limit": limit,
                    "includeVoided": str(include_voided).lower()
                }
            )
            
            data = await self._handle_response(response)
            results = data.get("results", [])
            
            # Convert to model objects
            patients = []
            for patient_data in results:
                try:
                    patient = OpenMRSPatient(**patient_data)
                    patients.append(patient)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse patient data: {str(e)}",
                        exc_info=e
                    )
            
            return patients
            
        except Exception as e:
            self.logger.error(
                f"Error searching patients: {str(e)}",
                exc_info=e,
                query=query
            )
            raise
    
    async def get_patient(self, uuid: str) -> Optional[OpenMRSPatient]:
        """
        Get a patient by UUID
        
        Args:
            uuid: Patient UUID
            
        Returns:
            The patient, or None if not found
        """
        try:
            response = await self.http_client.get(
                f"/patient/{uuid}",
                params={"v": "full"}
            )
            
            if response.status_code == 404:
                return None
                
            data = await self._handle_response(response)
            return OpenMRSPatient(**data)
            
        except Exception as e:
            self.logger.error(
                f"Error getting patient: {str(e)}",
                exc_info=e,
                uuid=uuid
            )
            raise
    
    async def get_patient_encounters(self, uuid: str) -> List[Dict[str, Any]]:
        """
        Get patient encounters
        
        Args:
            uuid: Patient UUID
            
        Returns:
            List of encounters
        """
        try:
            response = await self.http_client.get(
                f"/encounter",
                params={
                    "patient": uuid,
                    "v": "full"
                }
            )
            
            data = await self._handle_response(response)
            return data.get("results", [])
            
        except Exception as e:
            self.logger.error(
                f"Error getting patient encounters: {str(e)}",
                exc_info=e,
                uuid=uuid
            )
            raise
    
    async def get_patient_observations(
        self,
        uuid: str,
        concept: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get patient observations
        
        Args:
            uuid: Patient UUID
            concept: Optional concept UUID to filter observations
            
        Returns:
            List of observations
        """
        try:
            params = {
                "patient": uuid,
                "v": "full"
            }
            
            if concept:
                params["concept"] = concept
                
            response = await self.http_client.get(
                f"/obs",
                params=params
            )
            
            data = await self._handle_response(response)
            return data.get("results", [])
            
        except Exception as e:
            self.logger.error(
                f"Error getting patient observations: {str(e)}",
                exc_info=e,
                uuid=uuid,
                concept=concept
            )
            raise
    
    async def create_patient(self, patient_data: Dict[str, Any]) -> OpenMRSPatient:
        """
        Create a new patient
        
        Args:
            patient_data: Patient data
            
        Returns:
            The created patient
        """
        try:
            response = await self.http_client.post(
                "/patient",
                json=patient_data
            )
            
            data = await self._handle_response(response)
            return OpenMRSPatient(**data)
            
        except Exception as e:
            self.logger.error(
                f"Error creating patient: {str(e)}",
                exc_info=e
            )
            raise
    
    async def update_patient(self, uuid: str, patient_data: Dict[str, Any]) -> OpenMRSPatient:
        """
        Update a patient
        
        Args:
            uuid: Patient UUID
            patient_data: Updated patient data
            
        Returns:
            The updated patient
        """
        try:
            response = await self.http_client.post(
                f"/patient/{uuid}",
                json=patient_data
            )
            
            data = await self._handle_response(response)
            return OpenMRSPatient(**data)
            
        except Exception as e:
            self.logger.error(
                f"Error updating patient: {str(e)}",
                exc_info=e,
                uuid=uuid
            )
            raise
    
    async def create_encounter(self, encounter_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new encounter
        
        Args:
            encounter_data: Encounter data
            
        Returns:
            The created encounter
        """
        try:
            response = await self.http_client.post(
                "/encounter",
                json=encounter_data
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error creating encounter: {str(e)}",
                exc_info=e
            )
            raise
    
    async def create_observation(self, observation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new observation
        
        Args:
            observation_data: Observation data
            
        Returns:
            The created observation
        """
        try:
            response = await self.http_client.post(
                "/obs",
                json=observation_data
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error creating observation: {str(e)}",
                exc_info=e
            )
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()


class OpenMRSClient(BaseService):
    """
    OpenMRS REST API client for Decision Precision in Surgery platform
    """
    
    def __init__(self):
        """Initialize the OpenMRS client"""
        self.config = get_adapter_config("openmrs")
        self.base_url = self.config.get("base_url", "https://demo.openmrs.org/openmrs/ws/rest/v1")
        self.username = self.config.get("username", "admin")
        self.password = self.config.get("password", "Admin123")
        self.logger = Logger()
        self.logger.info("OpenMRS client initialized")
        
    async def get_patient(self, patient_id: str) -> Optional[OpenMRSPatient]:
        """Get patient by ID"""
        self.logger.info(f"Fetching patient {patient_id} from OpenMRS")
        # Implementation details here
        return None
        
    async def search_patients(self, query: str) -> List[OpenMRSPatient]:
        """Search for patients"""
        self.logger.info(f"Searching patients with query: {query}")
        # Implementation details here
        return []


# Create a singleton instance for importing
openmrs_client = OpenMRSClient()
