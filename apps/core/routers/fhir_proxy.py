"""FHIR Proxy Router - Healthcare Data Integration

Provides RESTful endpoints that proxy to FHIR backends (Medplum, HAPI FHIR)
with authentication, validation, and error handling.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from infra.clients.fhir_client import FHIRClient, FHIRError, create_fhir_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/fhir", tags=["FHIR Integration"])


# Dependency to get FHIR client
async def get_fhir_client() -> FHIRClient:
    """Get configured FHIR client"""
    return create_fhir_client()


# Request/Response Models
class FHIRRequest(BaseModel):
    """Generic FHIR request model"""
    resourceType: str
    data: Dict[str, Any]


class FHIRSearchParams(BaseModel):
    """FHIR search parameters"""
    _count: Optional[int] = 20
    _offset: Optional[int] = 0
    _sort: Optional[str] = None
    _include: Optional[List[str]] = None
    _revinclude: Optional[List[str]] = None


# Error handler for FHIR errors
async def fhir_error_handler(request: Request, exc: FHIRError):
    """Handle FHIR-specific errors"""
    logger.error(f"FHIR Error: {exc}")
    
    return JSONResponse(
        status_code=exc.status_code or 500,
        content={
            "resourceType": "OperationOutcome",
            "issue": [{
                "severity": "error",
                "code": "processing",
                "details": {"text": str(exc)},
                "diagnostics": str(exc.response) if exc.response else None
            }]
        }
    )


# Metadata and Capability
@router.get("/metadata")
async def get_metadata(client: FHIRClient = Depends(get_fhir_client)):
    """Get FHIR server capability statement"""
    async with client:
        try:
            metadata = await client.get_metadata()
            return metadata
        except FHIRError as e:
            logger.error(f"Failed to get FHIR metadata: {e}")
            raise HTTPException(status_code=500, detail="FHIR server unavailable")


@router.get("/.well-known/smart-configuration")
async def get_smart_configuration(client: FHIRClient = Depends(get_fhir_client)):
    """Get SMART on FHIR configuration"""
    async with client:
        try:
            config = await client.get_well_known_smart_configuration()
            return config
        except FHIRError:
            # Return default SMART configuration
            return {
                "authorization_endpoint": "/smart/authorize",
                "token_endpoint": "/smart/token",
                "capabilities": ["launch-ehr", "client-public"],
                "scopes_supported": ["patient/*.read", "user/*.read"]
            }


# Patient Resources
@router.get("/Patient/{patient_id}")
async def get_patient(
    patient_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get patient by ID"""
    async with client:
        patient = await client.get_patient(patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        return patient


@router.get("/Patient")
async def search_patients(
    request: Request,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Search patients with query parameters"""
    async with client:
        # Extract search parameters from query string
        params = dict(request.query_params)
        
        # Handle common FHIR search parameters
        search_params = {}
        
        if "name" in params:
            search_params["name"] = params["name"]
        if "identifier" in params:
            search_params["identifier"] = params["identifier"]
        if "birthdate" in params:
            search_params["birthdate"] = params["birthdate"]
        if "gender" in params:
            search_params["gender"] = params["gender"]
        
        # Add pagination parameters
        if "_count" in params:
            search_params["_count"] = params["_count"]
        if "_offset" in params:
            search_params["_offset"] = params["_offset"]
        
        bundle = await client.search_patients(**search_params)
        return bundle.dict()


@router.post("/Patient")
async def create_patient(
    patient_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Create new patient"""
    async with client:
        # Validate resourceType
        if patient_data.get("resourceType") != "Patient":
            patient_data["resourceType"] = "Patient"
        
        result = await client.create_patient(patient_data)
        return result


# Observation Resources
@router.get("/Observation/{observation_id}")
async def get_observation(
    observation_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get observation by ID"""
    async with client:
        observation = await client.get_observation(observation_id)
        if not observation:
            raise HTTPException(status_code=404, detail="Observation not found")
        return observation


@router.get("/Observation")
async def search_observations(
    request: Request,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Search observations"""
    async with client:
        params = dict(request.query_params)
        
        search_params = {}
        
        if "patient" in params:
            search_params["patient"] = params["patient"]
        if "subject" in params:
            search_params["patient"] = params["subject"].replace("Patient/", "")
        if "code" in params:
            search_params["code"] = params["code"]
        if "date" in params:
            search_params["date"] = params["date"]
        if "category" in params:
            search_params["category"] = params["category"]
        
        # Pagination
        if "_count" in params:
            search_params["_count"] = params["_count"]
        if "_offset" in params:
            search_params["_offset"] = params["_offset"]
        
        bundle = await client.search_observations(**search_params)
        return bundle.dict()


@router.post("/Observation")
async def create_observation(
    observation_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Create new observation"""
    async with client:
        if observation_data.get("resourceType") != "Observation":
            observation_data["resourceType"] = "Observation"
        
        result = await client.create_observation(observation_data)
        return result


# Encounter Resources
@router.get("/Encounter/{encounter_id}")
async def get_encounter(
    encounter_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get encounter by ID"""
    async with client:
        encounter = await client.get_encounter(encounter_id)
        if not encounter:
            raise HTTPException(status_code=404, detail="Encounter not found")
        return encounter


@router.get("/Encounter")
async def search_encounters(
    request: Request,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Search encounters"""
    async with client:
        params = dict(request.query_params)
        
        search_params = {}
        
        if "patient" in params:
            search_params["patient"] = params["patient"]
        if "subject" in params:
            search_params["patient"] = params["subject"].replace("Patient/", "")
        if "status" in params:
            search_params["status"] = params["status"]
        if "date" in params:
            search_params["date"] = params["date"]
        if "class" in params:
            search_params["class"] = params["class"]
        
        # Pagination
        if "_count" in params:
            search_params["_count"] = params["_count"]
        
        bundle = await client.search_encounters(**search_params)
        return bundle.dict()


# Questionnaire Resources
@router.get("/Questionnaire/{questionnaire_id}")
async def get_questionnaire(
    questionnaire_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get questionnaire by ID"""
    async with client:
        questionnaire = await client.get_questionnaire(questionnaire_id)
        if not questionnaire:
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        return questionnaire


@router.get("/Questionnaire")
async def search_questionnaires(
    request: Request,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Search questionnaires"""
    async with client:
        params = dict(request.query_params)
        
        search_params = {}
        
        if "url" in params:
            search_params["url"] = params["url"]
        if "status" in params:
            search_params["status"] = params["status"]
        else:
            search_params["status"] = "active"  # Default to active
        if "title" in params:
            search_params["title"] = params["title"]
        
        bundle = await client.search_questionnaires(**search_params)
        return bundle.dict()


@router.post("/Questionnaire")
async def create_questionnaire(
    questionnaire_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Create new questionnaire"""
    async with client:
        if questionnaire_data.get("resourceType") != "Questionnaire":
            questionnaire_data["resourceType"] = "Questionnaire"
        
        result = await client.create_questionnaire(questionnaire_data)
        return result


# QuestionnaireResponse Resources
@router.get("/QuestionnaireResponse/{response_id}")
async def get_questionnaire_response(
    response_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get questionnaire response by ID"""
    async with client:
        response = await client.get_questionnaire_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="QuestionnaireResponse not found")
        return response


@router.post("/QuestionnaireResponse")
async def create_questionnaire_response(
    response_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Submit questionnaire response"""
    async with client:
        if response_data.get("resourceType") != "QuestionnaireResponse":
            response_data["resourceType"] = "QuestionnaireResponse"
        
        # Set default status if not provided
        if "status" not in response_data:
            response_data["status"] = "completed"
        
        result = await client.create_questionnaire_response(response_data)
        return result


# Generic Resource Operations
@router.get("/{resource_type}/{resource_id}")
async def get_resource(
    resource_type: str,
    resource_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get any FHIR resource by type and ID"""
    async with client:
        resource = await client.get_resource(resource_type, resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail=f"{resource_type} not found")
        return resource


@router.get("/{resource_type}")
async def search_resources(
    resource_type: str,
    request: Request,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Search any FHIR resource type"""
    async with client:
        params = dict(request.query_params)
        bundle = await client.search_resources(resource_type, **params)
        return bundle.dict()


@router.post("/{resource_type}")
async def create_resource(
    resource_type: str,
    resource_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Create any FHIR resource"""
    async with client:
        if resource_data.get("resourceType") != resource_type:
            resource_data["resourceType"] = resource_type
        
        result = await client.create_resource(resource_type, resource_data)
        return result


@router.put("/{resource_type}/{resource_id}")
async def update_resource(
    resource_type: str,
    resource_id: str,
    resource_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Update existing FHIR resource"""
    async with client:
        if resource_data.get("resourceType") != resource_type:
            resource_data["resourceType"] = resource_type
        
        result = await client.update_resource(resource_type, resource_id, resource_data)
        return result


@router.delete("/{resource_type}/{resource_id}")
async def delete_resource(
    resource_type: str,
    resource_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Delete FHIR resource"""
    async with client:
        success = await client.delete_resource(resource_type, resource_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"{resource_type} not found")
        
        return {"message": f"{resource_type}/{resource_id} deleted successfully"}


# Batch Operations
@router.post("/")
async def post_bundle(
    bundle_data: Dict[str, Any],
    client: FHIRClient = Depends(get_fhir_client)
):
    """Submit FHIR Bundle (batch/transaction)"""
    async with client:
        if bundle_data.get("resourceType") != "Bundle":
            bundle_data["resourceType"] = "Bundle"
        
        result = await client.post_bundle(bundle_data)
        return result


# Health Check
@router.get("/health")
async def health_check(client: FHIRClient = Depends(get_fhir_client)):
    """Check FHIR server health"""
    async with client:
        try:
            metadata = await client.get_metadata()
            server_name = metadata.get("software", {}).get("name", "Unknown")
            server_version = metadata.get("software", {}).get("version", "Unknown")
            
            return {
                "status": "healthy",
                "fhir_server": server_name,
                "version": server_version,
                "timestamp": "2025-08-11T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"FHIR health check failed: {e}")
            raise HTTPException(status_code=503, detail="FHIR server unavailable")
