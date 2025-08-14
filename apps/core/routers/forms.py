"""Forms Router - FHIR Questionnaire Integration

Provides endpoints for creating, managing, and submitting healthcare forms
using FHIR Questionnaire and QuestionnaireResponse resources.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field

from infra.clients.fhir_client import FHIRClient, FHIRError, create_fhir_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/forms", tags=["Healthcare Forms"])


# Dependency to get FHIR client
async def get_fhir_client() -> FHIRClient:
    """Get configured FHIR client"""
    return create_fhir_client()


# Request/Response Models
class QuestionnaireRequest(BaseModel):
    """Questionnaire creation request"""
    title: str
    description: Optional[str] = None
    status: str = "active"
    purpose: Optional[str] = None
    items: List[Dict[str, Any]]


class QuestionnaireResponseRequest(BaseModel):
    """Questionnaire response submission"""
    questionnaire: str  # Reference to Questionnaire
    subject: Optional[str] = None  # Patient reference
    encounter: Optional[str] = None  # Encounter reference
    authored: Optional[str] = None  # When response was authored
    author: Optional[str] = None  # Who authored the response
    status: str = "completed"
    item: List[Dict[str, Any]]


class FormValidationError(BaseModel):
    """Form validation error"""
    field: str
    message: str
    code: str


# Error handler for FHIR errors
async def fhir_error_handler(request: Request, exc: FHIRError):
    """Handle FHIR-specific errors"""
    logger.error(f"Forms FHIR Error: {exc}")
    
    return JSONResponse(
        status_code=exc.status_code or 500,
        content={
            "error": "form_error",
            "message": str(exc),
            "details": exc.response if exc.response else None
        }
    )


# Questionnaire Management
@router.get("/questionnaires")
async def list_questionnaires(
    status: str = "active",
    limit: int = 20,
    offset: int = 0,
    client: FHIRClient = Depends(get_fhir_client)
):
    """List available questionnaires"""
    async with client:
        try:
            bundle = await client.search_questionnaires(status=status, _count=limit, _offset=offset)
            
            # Extract questionnaire summaries
            questionnaires = []
            for entry in bundle.entry:
                resource = entry.get("resource", {})
                questionnaires.append({
                    "id": resource.get("id"),
                    "title": resource.get("title"),
                    "description": resource.get("description"),
                    "status": resource.get("status"),
                    "date": resource.get("date"),
                    "publisher": resource.get("publisher"),
                    "purpose": resource.get("purpose")
                })
            
            return {
                "questionnaires": questionnaires,
                "total": bundle.total or len(questionnaires),
                "count": len(questionnaires),
                "offset": offset,
                "limit": limit
            }
            
        except FHIRError as e:
            logger.error(f"Failed to list questionnaires: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve questionnaires")


@router.get("/questionnaires/{questionnaire_id}")
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


@router.post("/questionnaires")
async def create_questionnaire(
    questionnaire_request: QuestionnaireRequest,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Create new questionnaire"""
    async with client:
        # Build FHIR Questionnaire resource
        questionnaire_data = {
            "resourceType": "Questionnaire",
            "id": str(uuid4()),
            "url": f"http://example.com/Questionnaire/{uuid4()}",
            "title": questionnaire_request.title,
            "status": questionnaire_request.status,
            "date": datetime.now().isoformat(),
            "item": questionnaire_request.items
        }
        
        if questionnaire_request.description:
            questionnaire_data["description"] = questionnaire_request.description
        
        if questionnaire_request.purpose:
            questionnaire_data["purpose"] = questionnaire_request.purpose
        
        try:
            result = await client.create_questionnaire(questionnaire_data)
            return result
        except FHIRError as e:
            logger.error(f"Failed to create questionnaire: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to create questionnaire: {str(e)}")


@router.put("/questionnaires/{questionnaire_id}")
async def update_questionnaire(
    questionnaire_id: str,
    questionnaire_request: QuestionnaireRequest,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Update existing questionnaire"""
    async with client:
        # Get existing questionnaire
        existing = await client.get_questionnaire(questionnaire_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        
        # Update fields
        existing["title"] = questionnaire_request.title
        existing["status"] = questionnaire_request.status
        existing["item"] = questionnaire_request.items
        
        if questionnaire_request.description:
            existing["description"] = questionnaire_request.description
        
        if questionnaire_request.purpose:
            existing["purpose"] = questionnaire_request.purpose
        
        try:
            result = await client.update_resource("Questionnaire", questionnaire_id, existing)
            return result
        except FHIRError as e:
            logger.error(f"Failed to update questionnaire: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to update questionnaire: {str(e)}")


# Questionnaire Responses
@router.get("/responses")
async def list_responses(
    patient: Optional[str] = None,
    questionnaire: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    client: FHIRClient = Depends(get_fhir_client)
):
    """List questionnaire responses"""
    async with client:
        try:
            # Build search parameters
            search_params = {"_count": limit, "_offset": offset}
            
            if patient:
                search_params["subject"] = f"Patient/{patient}"
            if questionnaire:
                search_params["questionnaire"] = questionnaire
            if status:
                search_params["status"] = status
            
            bundle = await client.search_resources("QuestionnaireResponse", **search_params)
            
            # Extract response summaries
            responses = []
            for entry in bundle.entry:
                resource = entry.get("resource", {})
                responses.append({
                    "id": resource.get("id"),
                    "questionnaire": resource.get("questionnaire"),
                    "subject": resource.get("subject"),
                    "status": resource.get("status"),
                    "authored": resource.get("authored"),
                    "author": resource.get("author")
                })
            
            return {
                "responses": responses,
                "total": bundle.total or len(responses),
                "count": len(responses),
                "offset": offset,
                "limit": limit
            }
            
        except FHIRError as e:
            logger.error(f"Failed to list responses: {e}")
            raise HTTPException(status_code=500, detail="Failed to retrieve responses")


@router.get("/responses/{response_id}")
async def get_response(
    response_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Get questionnaire response by ID"""
    async with client:
        response = await client.get_questionnaire_response(response_id)
        if not response:
            raise HTTPException(status_code=404, detail="QuestionnaireResponse not found")
        return response


@router.post("/responses")
async def submit_response(
    response_request: QuestionnaireResponseRequest,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Submit questionnaire response"""
    async with client:
        # Build FHIR QuestionnaireResponse resource
        response_data = {
            "resourceType": "QuestionnaireResponse",
            "id": str(uuid4()),
            "questionnaire": response_request.questionnaire,
            "status": response_request.status,
            "authored": response_request.authored or datetime.now().isoformat(),
            "item": response_request.item
        }
        
        if response_request.subject:
            response_data["subject"] = {"reference": response_request.subject}
        
        if response_request.encounter:
            response_data["encounter"] = {"reference": response_request.encounter}
        
        if response_request.author:
            response_data["author"] = {"reference": response_request.author}
        
        try:
            # Validate response against questionnaire
            validation_errors = await validate_response(response_data, client)
            if validation_errors:
                return JSONResponse(
                    status_code=400,
                    content={
                        "error": "validation_failed",
                        "message": "Response validation failed",
                        "errors": [error.dict() for error in validation_errors]
                    }
                )
            
            result = await client.create_questionnaire_response(response_data)
            return result
            
        except FHIRError as e:
            logger.error(f"Failed to submit response: {e}")
            raise HTTPException(status_code=400, detail=f"Failed to submit response: {str(e)}")


# Form Validation
async def validate_response(
    response_data: Dict[str, Any], 
    client: FHIRClient
) -> List[FormValidationError]:
    """Validate questionnaire response against questionnaire definition"""
    errors = []
    
    try:
        # Get questionnaire definition
        questionnaire_ref = response_data.get("questionnaire")
        if not questionnaire_ref:
            errors.append(FormValidationError(
                field="questionnaire",
                message="Questionnaire reference is required",
                code="required"
            ))
            return errors
        
        # Extract questionnaire ID from reference
        questionnaire_id = questionnaire_ref.split("/")[-1]
        questionnaire = await client.get_questionnaire(questionnaire_id)
        
        if not questionnaire:
            errors.append(FormValidationError(
                field="questionnaire",
                message="Referenced questionnaire not found",
                code="not_found"
            ))
            return errors
        
        # Validate response items against questionnaire items
        questionnaire_items = {item.get("linkId"): item for item in questionnaire.get("item", [])}
        response_items = {item.get("linkId"): item for item in response_data.get("item", [])}
        
        # Check required fields
        for item_id, item_def in questionnaire_items.items():
            if item_def.get("required", False) and item_id not in response_items:
                errors.append(FormValidationError(
                    field=item_id,
                    message=f"Required field '{item_def.get('text', item_id)}' is missing",
                    code="required"
                ))
        
        # Validate data types and constraints
        for item_id, response_item in response_items.items():
            if item_id in questionnaire_items:
                item_def = questionnaire_items[item_id]
                item_errors = validate_item(response_item, item_def)
                errors.extend(item_errors)
        
    except Exception as e:
        logger.error(f"Validation error: {e}")
        errors.append(FormValidationError(
            field="general",
            message="Validation failed due to internal error",
            code="internal_error"
        ))
    
    return errors


def validate_item(response_item: Dict[str, Any], item_def: Dict[str, Any]) -> List[FormValidationError]:
    """Validate individual response item"""
    errors = []
    item_id = response_item.get("linkId")
    item_type = item_def.get("type")
    
    # Get response value
    answer = response_item.get("answer", [])
    if not answer and item_def.get("required", False):
        errors.append(FormValidationError(
            field=item_id,
            message="Required field cannot be empty",
            code="required"
        ))
        return errors
    
    for ans in answer:
        # Validate based on item type
        if item_type == "string":
            if "valueString" not in ans:
                errors.append(FormValidationError(
                    field=item_id,
                    message="String value expected",
                    code="type_mismatch"
                ))
        
        elif item_type == "integer":
            if "valueInteger" not in ans:
                errors.append(FormValidationError(
                    field=item_id,
                    message="Integer value expected",
                    code="type_mismatch"
                ))
        
        elif item_type == "decimal":
            if "valueDecimal" not in ans:
                errors.append(FormValidationError(
                    field=item_id,
                    message="Decimal value expected",
                    code="type_mismatch"
                ))
        
        elif item_type == "boolean":
            if "valueBoolean" not in ans:
                errors.append(FormValidationError(
                    field=item_id,
                    message="Boolean value expected",
                    code="type_mismatch"
                ))
        
        elif item_type == "date":
            if "valueDate" not in ans:
                errors.append(FormValidationError(
                    field=item_id,
                    message="Date value expected",
                    code="type_mismatch"
                ))
        
        elif item_type == "choice":
            if "valueCoding" not in ans:
                errors.append(FormValidationError(
                    field=item_id,
                    message="Choice value expected",
                    code="type_mismatch"
                ))
    
    return errors


# Form Templates
@router.get("/templates")
async def list_form_templates():
    """List available form templates"""
    templates = [
        {
            "id": "patient-intake",
            "title": "Patient Intake Form",
            "description": "Basic patient information and medical history",
            "category": "intake"
        },
        {
            "id": "symptoms-assessment",
            "title": "Symptoms Assessment",
            "description": "Patient-reported symptoms and severity",
            "category": "assessment"
        },
        {
            "id": "medication-history",
            "title": "Medication History",
            "description": "Current and past medications",
            "category": "medication"
        },
        {
            "id": "surgical-checklist",
            "title": "Surgical Safety Checklist",
            "description": "Pre-operative safety checklist",
            "category": "surgery"
        }
    ]
    
    return {"templates": templates, "count": len(templates)}


@router.get("/templates/{template_id}")
async def get_form_template(template_id: str):
    """Get form template definition"""
    # Sample form templates (in production, these would be stored in database)
    templates = {
        "patient-intake": {
            "title": "Patient Intake Form",
            "description": "Basic patient information and medical history",
            "items": [
                {
                    "linkId": "patient-name",
                    "text": "Full Name",
                    "type": "string",
                    "required": True
                },
                {
                    "linkId": "patient-dob",
                    "text": "Date of Birth",
                    "type": "date",
                    "required": True
                },
                {
                    "linkId": "patient-gender",
                    "text": "Gender",
                    "type": "choice",
                    "required": True,
                    "answerOption": [
                        {"valueCoding": {"code": "male", "display": "Male"}},
                        {"valueCoding": {"code": "female", "display": "Female"}},
                        {"valueCoding": {"code": "other", "display": "Other"}}
                    ]
                },
                {
                    "linkId": "chief-complaint",
                    "text": "Chief Complaint",
                    "type": "text",
                    "required": True
                },
                {
                    "linkId": "medical-history",
                    "text": "Medical History",
                    "type": "text",
                    "required": False
                }
            ]
        },
        "symptoms-assessment": {
            "title": "Symptoms Assessment",
            "description": "Patient-reported symptoms and severity",
            "items": [
                {
                    "linkId": "pain-level",
                    "text": "Pain Level (0-10)",
                    "type": "integer",
                    "required": True
                },
                {
                    "linkId": "pain-location",
                    "text": "Pain Location",
                    "type": "string",
                    "required": True
                },
                {
                    "linkId": "symptoms-duration",
                    "text": "How long have you had these symptoms?",
                    "type": "choice",
                    "answerOption": [
                        {"valueCoding": {"code": "hours", "display": "Hours"}},
                        {"valueCoding": {"code": "days", "display": "Days"}},
                        {"valueCoding": {"code": "weeks", "display": "Weeks"}},
                        {"valueCoding": {"code": "months", "display": "Months"}}
                    ]
                }
            ]
        }
    }
    
    template = templates.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template


@router.post("/templates/{template_id}/questionnaire")
async def create_questionnaire_from_template(
    template_id: str,
    client: FHIRClient = Depends(get_fhir_client)
):
    """Create questionnaire from template"""
    # Get template
    template = await get_form_template(template_id)
    
    # Create questionnaire request
    questionnaire_request = QuestionnaireRequest(
        title=template["title"],
        description=template["description"],
        items=template["items"]
    )
    
    # Create questionnaire
    return await create_questionnaire(questionnaire_request, client)


# Health Check
@router.get("/health")
async def health_check(client: FHIRClient = Depends(get_fhir_client)):
    """Check forms service health"""
    async with client:
        try:
            # Test FHIR connection by searching questionnaires
            await client.search_questionnaires(_count=1)
            
            return {
                "status": "healthy",
                "service": "Healthcare Forms",
                "features": [
                    "FHIR Questionnaire support",
                    "QuestionnaireResponse submission",
                    "Form validation",
                    "Template library"
                ],
                "timestamp": "2025-08-11T00:00:00Z"
            }
        except Exception as e:
            logger.error(f"Forms health check failed: {e}")
            raise HTTPException(status_code=503, detail="Forms service unavailable")


# Demo Form
@router.get("/demo")
async def forms_demo():
    """Demo page for forms functionality"""
    demo_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Healthcare Forms Demo</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            .demo-section { border: 1px solid #ddd; padding: 20px; margin: 20px 0; border-radius: 8px; }
            .api-button { padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; display: inline-block; margin: 5px; }
            .api-button:hover { background: #0056b3; }
            code { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; }
            .form-example { background: #f8f9fa; padding: 15px; border-radius: 4px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <h1>Healthcare Forms Demo</h1>
        
        <div class="demo-section">
            <h2>Available Templates</h2>
            <a href="/forms/templates" class="api-button">View Templates</a>
            <a href="/forms/templates/patient-intake" class="api-button">Patient Intake</a>
            <a href="/forms/templates/symptoms-assessment" class="api-button">Symptoms Assessment</a>
        </div>
        
        <div class="demo-section">
            <h2>Questionnaires</h2>
            <a href="/forms/questionnaires" class="api-button">List Questionnaires</a>
            <div class="form-example">
                <strong>Create from template:</strong><br>
                <code>POST /forms/templates/patient-intake/questionnaire</code>
            </div>
        </div>
        
        <div class="demo-section">
            <h2>Form Responses</h2>
            <a href="/forms/responses" class="api-button">List Responses</a>
            <div class="form-example">
                <strong>Submit response:</strong><br>
                <code>POST /forms/responses</code>
            </div>
        </div>
        
        <div class="demo-section">
            <h2>Integration</h2>
            <p>Forms integrate with FHIR backend for:</p>
            <ul>
                <li>Questionnaire storage and retrieval</li>
                <li>QuestionnaireResponse submission</li>
                <li>Patient and encounter linking</li>
                <li>Response validation</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=demo_html)
