"""
OpenClinica Adapter

This adapter provides integration with the OpenClinica REST API for clinical trials
and protocol management, allowing synchronization of study protocols, forms, and data.
"""

import asyncio
import json
import base64
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import httpx
from pydantic import BaseModel, Field

from core.config.settings import get_adapter_config
from core.services.base import BaseService
from core.services.logger import Logger


class OpenClinicaStudy(BaseModel):
    """OpenClinica study model"""
    
    oid: str = Field(..., description="Study OID")
    name: str = Field(..., description="Study name")
    identifier: str = Field(..., description="Study identifier")
    principal_investigator: Optional[str] = Field(None, description="Principal investigator")
    status: str = Field(..., description="Study status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class OpenClinicaEvent(BaseModel):
    """OpenClinica event model"""
    
    oid: str = Field(..., description="Event OID")
    name: str = Field(..., description="Event name")
    description: Optional[str] = Field(None, description="Event description")
    category: Optional[str] = Field(None, description="Event category")
    type: str = Field(..., description="Event type")
    repeating: bool = Field(False, description="Whether the event is repeating")
    status: str = Field(..., description="Event status")


class OpenClinicaForm(BaseModel):
    """OpenClinica form model"""
    
    oid: str = Field(..., description="Form OID")
    name: str = Field(..., description="Form name")
    version: str = Field(..., description="Form version")
    status: str = Field(..., description="Form status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class OpenClinicaAdapter(BaseService):
    """OpenClinica REST API adapter for protocol management"""
    
    def __init__(self):
        super().__init__()
        self.config = get_adapter_config("openclinica")
        self.logger = Logger()
        self.base_url = self.config.get("base_url", "http://localhost:8080/OpenClinica/rest")
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
                f"OpenClinica API error: {response.status_code}",
                status_code=response.status_code,
                url=str(response.url),
                response_text=response.text
            )
            raise Exception(f"OpenClinica API error: {response.status_code} - {response.text}")
            
        return response.json()
    
    async def get_studies(self) -> List[OpenClinicaStudy]:
        """
        Get all available studies
        
        Returns:
            List of studies
        """
        try:
            response = await self.http_client.get("/clinicaldata/studies")
            
            data = await self._handle_response(response)
            studies = []
            
            for study_data in data.get("studies", []):
                try:
                    study = OpenClinicaStudy(**study_data)
                    studies.append(study)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse study data: {str(e)}",
                        exc_info=e
                    )
            
            return studies
            
        except Exception as e:
            self.logger.error(
                f"Error getting studies: {str(e)}",
                exc_info=e
            )
            raise
    
    async def get_study(self, study_oid: str) -> Optional[OpenClinicaStudy]:
        """
        Get a study by OID
        
        Args:
            study_oid: Study OID
            
        Returns:
            The study, or None if not found
        """
        try:
            response = await self.http_client.get(f"/clinicaldata/studies/{study_oid}")
            
            if response.status_code == 404:
                return None
                
            data = await self._handle_response(response)
            return OpenClinicaStudy(**data)
            
        except Exception as e:
            self.logger.error(
                f"Error getting study: {str(e)}",
                exc_info=e,
                study_oid=study_oid
            )
            raise
    
    async def get_study_events(self, study_oid: str) -> List[OpenClinicaEvent]:
        """
        Get events for a study
        
        Args:
            study_oid: Study OID
            
        Returns:
            List of events
        """
        try:
            response = await self.http_client.get(
                f"/clinicaldata/studies/{study_oid}/events"
            )
            
            data = await self._handle_response(response)
            events = []
            
            for event_data in data.get("events", []):
                try:
                    event = OpenClinicaEvent(**event_data)
                    events.append(event)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse event data: {str(e)}",
                        exc_info=e
                    )
            
            return events
            
        except Exception as e:
            self.logger.error(
                f"Error getting study events: {str(e)}",
                exc_info=e,
                study_oid=study_oid
            )
            raise
    
    async def get_event_forms(
        self,
        study_oid: str,
        event_oid: str
    ) -> List[OpenClinicaForm]:
        """
        Get forms for an event
        
        Args:
            study_oid: Study OID
            event_oid: Event OID
            
        Returns:
            List of forms
        """
        try:
            response = await self.http_client.get(
                f"/clinicaldata/studies/{study_oid}/events/{event_oid}/forms"
            )
            
            data = await self._handle_response(response)
            forms = []
            
            for form_data in data.get("forms", []):
                try:
                    form = OpenClinicaForm(**form_data)
                    forms.append(form)
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse form data: {str(e)}",
                        exc_info=e
                    )
            
            return forms
            
        except Exception as e:
            self.logger.error(
                f"Error getting event forms: {str(e)}",
                exc_info=e,
                study_oid=study_oid,
                event_oid=event_oid
            )
            raise
    
    async def get_form_versions(
        self,
        study_oid: str,
        form_oid: str
    ) -> List[Dict[str, Any]]:
        """
        Get versions of a form
        
        Args:
            study_oid: Study OID
            form_oid: Form OID
            
        Returns:
            List of form versions
        """
        try:
            response = await self.http_client.get(
                f"/clinicaldata/studies/{study_oid}/forms/{form_oid}/versions"
            )
            
            data = await self._handle_response(response)
            return data.get("versions", [])
            
        except Exception as e:
            self.logger.error(
                f"Error getting form versions: {str(e)}",
                exc_info=e,
                study_oid=study_oid,
                form_oid=form_oid
            )
            raise
    
    async def get_subject_data(
        self,
        study_oid: str,
        subject_key: str
    ) -> Dict[str, Any]:
        """
        Get data for a subject
        
        Args:
            study_oid: Study OID
            subject_key: Subject key
            
        Returns:
            Subject data
        """
        try:
            response = await self.http_client.get(
                f"/clinicaldata/studies/{study_oid}/subjects/{subject_key}"
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error getting subject data: {str(e)}",
                exc_info=e,
                study_oid=study_oid,
                subject_key=subject_key
            )
            raise
    
    async def import_protocol(
        self,
        study_oid: str,
        protocol_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import a protocol into a study
        
        Args:
            study_oid: Study OID
            protocol_data: Protocol data in OpenClinica format
            
        Returns:
            Import result
        """
        try:
            response = await self.http_client.post(
                f"/clinicaldata/studies/{study_oid}/protocols",
                json=protocol_data
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error importing protocol: {str(e)}",
                exc_info=e,
                study_oid=study_oid
            )
            raise
    
    async def check_protocol_compliance(
        self,
        study_oid: str,
        subject_key: str
    ) -> Dict[str, Any]:
        """
        Check protocol compliance for a subject
        
        Args:
            study_oid: Study OID
            subject_key: Subject key
            
        Returns:
            Compliance status with deviations
        """
        try:
            response = await self.http_client.get(
                f"/clinicaldata/studies/{study_oid}/subjects/{subject_key}/compliance"
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error checking protocol compliance: {str(e)}",
                exc_info=e,
                study_oid=study_oid,
                subject_key=subject_key
            )
            raise
    
    async def report_protocol_deviation(
        self,
        study_oid: str,
        subject_key: str,
        deviation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Report a protocol deviation
        
        Args:
            study_oid: Study OID
            subject_key: Subject key
            deviation_data: Deviation data
            
        Returns:
            Created deviation report
        """
        try:
            response = await self.http_client.post(
                f"/clinicaldata/studies/{study_oid}/subjects/{subject_key}/deviations",
                json=deviation_data
            )
            
            return await self._handle_response(response)
            
        except Exception as e:
            self.logger.error(
                f"Error reporting protocol deviation: {str(e)}",
                exc_info=e,
                study_oid=study_oid,
                subject_key=subject_key
            )
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.http_client.aclose()
