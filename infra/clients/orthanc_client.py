"""Orthanc PACS Client - Medical Imaging Integration

Provides interface to Orthanc PACS for DICOM storage, retrieval,
and integration with OHIF viewer.
"""

import asyncio
import base64
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class OrthancError(Exception):
    """Orthanc-specific exception"""
    def __init__(self, message: str, status_code: int = None, response: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class StudyInfo(BaseModel):
    """DICOM Study information"""
    ID: str
    PatientID: str
    PatientName: str
    StudyDate: str
    StudyTime: str
    StudyDescription: Optional[str] = None
    AccessionNumber: Optional[str] = None
    Series: List[str] = []
    Instances: List[str] = []
    
    
class SeriesInfo(BaseModel):
    """DICOM Series information"""
    ID: str
    SeriesNumber: str
    SeriesDescription: Optional[str] = None
    Modality: str
    StudyID: str
    Instances: List[str] = []


class InstanceInfo(BaseModel):
    """DICOM Instance information"""
    ID: str
    SOPInstanceUID: str
    SeriesID: str
    StudyID: str
    PatientID: str


class OrthancClient:
    """
    Orthanc PACS Client for medical imaging integration
    
    Supports:
    - DICOM study/series/instance management
    - OHIF viewer integration
    - Patient study retrieval
    - DICOM upload and storage
    """
    
    def __init__(
        self,
        base_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 60,
        verify_ssl: bool = True
    ):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.timeout = timeout
        
        # Setup authentication
        auth = None
        if username and password:
            auth = httpx.BasicAuth(username, password)
        
        # HTTP client with proper headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        self.client = httpx.AsyncClient(
            auth=auth,
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
        """Build full URL for Orthanc endpoint"""
        return urljoin(self.base_url + "/", path.lstrip('/'))
    
    async def _request(
        self, 
        method: str, 
        path: str, 
        data: Optional[Union[Dict, bytes]] = None,
        params: Optional[Dict] = None,
        content_type: Optional[str] = None
    ) -> Union[Dict[str, Any], List, bytes]:
        """Make authenticated Orthanc request"""
        url = self._url(path)
        
        # Handle different content types
        kwargs = {"params": params}
        
        if content_type == "application/dicom":
            kwargs["content"] = data
            kwargs["headers"] = {"Content-Type": "application/dicom"}
        elif isinstance(data, dict):
            kwargs["json"] = data
        elif data is not None:
            kwargs["content"] = data
        
        try:
            response = await self.client.request(method=method, url=url, **kwargs)
            
            # Log request for debugging
            logger.debug(f"Orthanc {method} {url} -> {response.status_code}")
            
            # Handle 404 as None
            if response.status_code == 404:
                return None
            
            if not response.is_success:
                error_data = {}
                try:
                    error_data = response.json()
                except:
                    error_data = {"message": response.text}
                    
                raise OrthancError(
                    f"Orthanc request failed: {response.status_code} {response.reason_phrase}",
                    status_code=response.status_code,
                    response=error_data
                )
            
            # Return based on content type
            content_type = response.headers.get("content-type", "")
            
            if "application/json" in content_type:
                return response.json()
            elif "application/dicom" in content_type:
                return response.content
            else:
                try:
                    return response.json()
                except:
                    return response.content
                
        except httpx.RequestError as e:
            raise OrthancError(f"Network error: {str(e)}")
    
    # System Information
    async def get_system(self) -> Dict[str, Any]:
        """Get Orthanc system information"""
        return await self._request("GET", "system")
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get Orthanc statistics"""
        return await self._request("GET", "statistics")
    
    # Patient Operations
    async def get_patients(self) -> List[str]:
        """Get all patient IDs"""
        return await self._request("GET", "patients")
    
    async def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient information"""
        return await self._request("GET", f"patients/{patient_id}")
    
    async def get_patient_studies(self, patient_id: str) -> List[str]:
        """Get studies for a patient"""
        patient_data = await self.get_patient(patient_id)
        return patient_data.get("Studies", []) if patient_data else []
    
    async def search_patients(self, query: Dict[str, str]) -> List[str]:
        """Search for patients using DICOM tags"""
        return await self._request("POST", "tools/find", data={
            "Level": "Patient",
            "Query": query
        })
    
    # Study Operations
    async def get_studies(self) -> List[str]:
        """Get all study IDs"""
        return await self._request("GET", "studies")
    
    async def get_study(self, study_id: str) -> Optional[StudyInfo]:
        """Get study information"""
        study_data = await self._request("GET", f"studies/{study_id}")
        if study_data:
            return StudyInfo(**study_data)
        return None
    
    async def get_study_series(self, study_id: str) -> List[str]:
        """Get series for a study"""
        study_data = await self.get_study(study_id)
        return study_data.Series if study_data else []
    
    async def search_studies(
        self,
        patient_id: Optional[str] = None,
        study_date: Optional[str] = None,
        accession_number: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """Search for studies"""
        query = {}
        
        if patient_id:
            query["PatientID"] = patient_id
        if study_date:
            query["StudyDate"] = study_date
        if accession_number:
            query["AccessionNumber"] = accession_number
            
        # Add any additional DICOM tags
        query.update(kwargs)
        
        return await self._request("POST", "tools/find", data={
            "Level": "Study",
            "Query": query
        })
    
    # Series Operations
    async def get_series(self, series_id: str) -> Optional[SeriesInfo]:
        """Get series information"""
        series_data = await self._request("GET", f"series/{series_id}")
        if series_data:
            return SeriesInfo(**series_data)
        return None
    
    async def get_series_instances(self, series_id: str) -> List[str]:
        """Get instances for a series"""
        series_data = await self.get_series(series_id)
        return series_data.Instances if series_data else []
    
    # Instance Operations
    async def get_instance(self, instance_id: str) -> Optional[InstanceInfo]:
        """Get instance information"""
        instance_data = await self._request("GET", f"instances/{instance_id}")
        if instance_data:
            return InstanceInfo(**instance_data)
        return None
    
    async def get_instance_dicom(self, instance_id: str) -> Optional[bytes]:
        """Get DICOM file for instance"""
        return await self._request("GET", f"instances/{instance_id}/file")
    
    async def get_instance_tags(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get DICOM tags for instance"""
        return await self._request("GET", f"instances/{instance_id}/tags")
    
    # DICOM Upload
    async def upload_dicom(self, dicom_data: bytes) -> Dict[str, Any]:
        """Upload DICOM file"""
        return await self._request(
            "POST", 
            "instances", 
            data=dicom_data,
            content_type="application/dicom"
        )
    
    async def upload_dicom_file(self, file_path: str) -> Dict[str, Any]:
        """Upload DICOM file from filesystem"""
        with open(file_path, 'rb') as f:
            dicom_data = f.read()
        return await self.upload_dicom(dicom_data)
    
    # OHIF Integration
    async def get_ohif_study_data(self, study_id: str) -> Dict[str, Any]:
        """Get study data formatted for OHIF viewer"""
        study = await self.get_study(study_id)
        if not study:
            return None
        
        # Build OHIF-compatible study data
        ohif_study = {
            "StudyInstanceUID": study_id,
            "PatientID": study.PatientID,
            "PatientName": study.PatientName,
            "StudyDate": study.StudyDate,
            "StudyTime": study.StudyTime,
            "StudyDescription": study.StudyDescription or "",
            "AccessionNumber": study.AccessionNumber or "",
            "series": []
        }
        
        # Add series data
        for series_id in study.Series:
            series = await self.get_series(series_id)
            if series:
                ohif_series = {
                    "SeriesInstanceUID": series_id,
                    "SeriesNumber": series.SeriesNumber,
                    "SeriesDescription": series.SeriesDescription or "",
                    "Modality": series.Modality,
                    "instances": []
                }
                
                # Add instance data
                for instance_id in series.Instances:
                    instance = await self.get_instance(instance_id)
                    if instance:
                        ohif_series["instances"].append({
                            "SOPInstanceUID": instance.SOPInstanceUID,
                            "InstanceNumber": instance_id,
                            "url": self._url(f"instances/{instance_id}/file")
                        })
                
                ohif_study["series"].append(ohif_series)
        
        return ohif_study
    
    async def get_ohif_viewer_url(
        self, 
        study_id: str, 
        ohif_base_url: str = "http://localhost:3000"
    ) -> str:
        """Get OHIF viewer URL for study"""
        study_data = await self.get_ohif_study_data(study_id)
        if not study_data:
            return None
        
        # Encode study data for OHIF URL
        study_json = json.dumps(study_data)
        study_encoded = base64.b64encode(study_json.encode()).decode()
        
        return f"{ohif_base_url}/viewer?studyInstanceUIDs={study_id}&url={study_encoded}"
    
    # Modality Worklist (SCU)
    async def query_worklist(self, query: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Query modality worklist"""
        query = query or {}
        return await self._request("POST", "modalities/worklist", data=query)
    
    # Archive and Export
    async def create_archive(self, resources: List[str], resource_type: str = "studies") -> str:
        """Create ZIP archive of studies/series/instances"""
        return await self._request("POST", f"{resource_type}/archive", data=resources)
    
    async def export_to_dicom_server(
        self, 
        resources: List[str], 
        target_modality: str,
        resource_type: str = "studies"
    ) -> Dict[str, Any]:
        """Export to external DICOM server"""
        return await self._request("POST", f"{resource_type}/store", data={
            "Resources": resources,
            "Modality": target_modality
        })


# Factory function for easy configuration
def create_orthanc_client(
    base_url: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    **kwargs
) -> OrthancClient:
    """
    Create Orthanc client from environment or provided config
    """
    import os
    
    base_url = base_url or os.getenv("ORTHANC_URL", "http://localhost:8042")
    username = username or os.getenv("ORTHANC_USER", "orthanc")
    password = password or os.getenv("ORTHANC_PASS", "orthanc")
    
    return OrthancClient(
        base_url=base_url, 
        username=username, 
        password=password, 
        **kwargs
    )


# Example usage
async def example_usage():
    """Example of using the Orthanc client"""
    async with create_orthanc_client() as client:
        # Get system information
        system_info = await client.get_system()
        print(f"Orthanc Version: {system_info.get('Version', 'Unknown')}")
        
        # Get statistics
        stats = await client.get_statistics()
        print(f"Studies: {stats.get('CountStudies', 0)}")
        
        # Search for studies
        studies = await client.search_studies(patient_id="12345")
        print(f"Found {len(studies)} studies for patient 12345")
        
        # Get OHIF viewer URL for first study
        if studies:
            study_id = studies[0]
            viewer_url = await client.get_ohif_viewer_url(study_id)
            print(f"OHIF Viewer: {viewer_url}")


if __name__ == "__main__":
    asyncio.run(example_usage())
