"""
Clinical Journal API for Decision Precision in Surgery Platform

These endpoints provide access to clinical note templates, creation and
management of structured clinical notes, and auto-generation of content.
"""

from typing import Dict, Any, List, Optional
import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from pydantic import BaseModel

from core.models.user import UserIdentity
from core.services.logger import get_logger
from features.journal.service import (
    journal_service,
    ClinicalTemplate,
    ClinicalNote,
    TemplateSection,
    FieldValue,
    AutoGenerateRequest
)
from features.journal.auto_entries import (
    auto_generate_note_content,
    auto_generate_for_protocol,
    auto_generate_followup
)
from api.v1.auth import get_current_active_user

# Configure logger
logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/journal",
    tags=["journal"],
    responses={404: {"description": "Not found"}},
)

class TemplateQuery(BaseModel):
    """Query parameters for template filtering."""
    clinical_domain: Optional[str] = None
    role: Optional[str] = None

class NoteQuery(BaseModel):
    """Query parameters for note filtering."""
    template_id: Optional[str] = None
    status: Optional[str] = None
    date_from: Optional[datetime.datetime] = None
    date_to: Optional[datetime.datetime] = None
    tags: Optional[List[str]] = None
    limit: int = 100
    offset: int = 0

class FieldValueUpdate(BaseModel):
    """Data for updating a field value."""
    value: Any

class CreateNoteRequest(BaseModel):
    """Request for creating a new clinical note."""
    template_id: str
    patient_id: str
    title: str
    encounter_id: Optional[str] = None
    protocol_id: Optional[str] = None
    initial_values: Optional[Dict[str, Dict[str, Any]]] = None
    tags: Optional[List[str]] = None

class AutoGenerateRequest(BaseModel):
    """Request for auto-generating note content."""
    patient_id: str
    encounter_id: Optional[str] = None

class ProtocolNoteRequest(BaseModel):
    """Request for creating a note based on a protocol."""
    protocol_id: str
    patient_id: str
    template_id: Optional[str] = None

class FollowupNoteRequest(BaseModel):
    """Request for creating a follow-up note."""
    original_note_id: str
    days_since_surgery: int


@router.get("/templates", response_model=List[Dict[str, Any]])
async def list_templates(
    query: TemplateQuery = Depends(),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    List available clinical note templates with optional filtering.
    """
    templates = await journal_service.list_templates(
        clinical_domain=query.clinical_domain,
        role=query.role
    )
    return templates

@router.get("/templates/{template_id}", response_model=ClinicalTemplate)
async def get_template(
    template_id: str = Path(..., description="The ID of the template to retrieve"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get a specific clinical note template by ID.
    """
    template = await journal_service.get_template(template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template {template_id} not found"
        )
    return template

@router.post("/notes", response_model=ClinicalNote)
async def create_note(
    request: CreateNoteRequest,
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Create a new clinical note based on a template.
    """
    note = await journal_service.create_note(
        template_id=request.template_id,
        patient_id=request.patient_id,
        title=request.title,
        created_by=current_user.id,
        encounter_id=request.encounter_id,
        protocol_id=request.protocol_id,
        initial_values=request.initial_values,
        tags=request.tags
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create note with template {request.template_id}"
        )
    
    return note

@router.get("/notes/patient/{patient_id}", response_model=List[ClinicalNote])
async def get_patient_notes(
    patient_id: str = Path(..., description="The ID of the patient"),
    query: NoteQuery = Depends(),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get clinical notes for a specific patient with optional filtering.
    """
    notes = await journal_service.get_notes_for_patient(
        patient_id=patient_id,
        template_id=query.template_id,
        status=query.status,
        date_from=query.date_from,
        date_to=query.date_to,
        tags=query.tags,
        limit=query.limit,
        offset=query.offset
    )
    return notes

@router.get("/notes/{note_id}", response_model=ClinicalNote)
async def get_note(
    note_id: str = Path(..., description="The ID of the note to retrieve"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Get a specific clinical note by ID.
    """
    note = await journal_service.get_note(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} not found"
        )
    return note

@router.put("/notes/{note_id}/fields/{section_id}/{field_id}", response_model=ClinicalNote)
async def update_note_field(
    note_id: str = Path(..., description="The ID of the note to update"),
    section_id: str = Path(..., description="The ID of the section containing the field"),
    field_id: str = Path(..., description="The ID of the field to update"),
    update: FieldValueUpdate = Body(..., description="The new field value"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Update a field value in a clinical note.
    """
    note = await journal_service.update_note_field(
        note_id=note_id,
        section_id=section_id,
        field_id=field_id,
        value=update.value,
        user_id=current_user.id
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to update field {field_id} in note {note_id}"
        )
    
    return note

@router.put("/notes/{note_id}/sections/{section_id}/complete", response_model=ClinicalNote)
async def complete_section(
    note_id: str = Path(..., description="The ID of the note"),
    section_id: str = Path(..., description="The ID of the section to complete"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Mark a section as completed in a clinical note.
    """
    note = await journal_service.complete_section(
        note_id=note_id,
        section_id=section_id,
        user_id=current_user.id
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to complete section {section_id} in note {note_id}"
        )
    
    return note

@router.put("/notes/{note_id}/complete", response_model=ClinicalNote)
async def complete_note(
    note_id: str = Path(..., description="The ID of the note to complete"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Mark a clinical note as completed.
    """
    note = await journal_service.complete_note(
        note_id=note_id,
        user_id=current_user.id
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to complete note {note_id}"
        )
    
    return note

@router.put("/notes/{note_id}/sign", response_model=ClinicalNote)
async def sign_note(
    note_id: str = Path(..., description="The ID of the note to sign"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Sign a clinical note, finalizing it for the medical record.
    """
    note = await journal_service.sign_note(
        note_id=note_id,
        user_id=current_user.id
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to sign note {note_id}"
        )
    
    return note

@router.post("/notes/{note_id}/amend", response_model=ClinicalNote)
async def amend_note(
    note_id: str = Path(..., description="The ID of the note to amend"),
    reason: str = Body(..., embed=True, description="Reason for the amendment"),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Create an amended version of a signed note.
    """
    note = await journal_service.amend_note(
        note_id=note_id,
        user_id=current_user.id,
        reason=reason
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to amend note {note_id}"
        )
    
    return note

@router.post("/notes/{note_id}/auto-generate", response_model=ClinicalNote)
async def auto_generate_content(
    note_id: str = Path(..., description="The ID of the note to update"),
    request: AutoGenerateRequest = Body(...),
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Auto-generate content for a clinical note from various data sources.
    """
    # Get the note to determine template ID
    note = await journal_service.get_note(note_id)
    if not note:
        raise HTTPException(
            status_code=404,
            detail=f"Note {note_id} not found"
        )
    
    # Auto-generate content
    updated_note = await auto_generate_note_content(
        note_id=note_id,
        patient_id=request.patient_id,
        template_id=note.template_id,
        user_id=current_user.id,
        encounter_id=request.encounter_id
    )
    
    if not updated_note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to auto-generate content for note {note_id}"
        )
    
    return updated_note

@router.post("/notes/protocol", response_model=ClinicalNote)
async def create_protocol_note(
    request: ProtocolNoteRequest,
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Auto-generate a clinical note based on a protocol.
    """
    note = await auto_generate_for_protocol(
        protocol_id=request.protocol_id,
        patient_id=request.patient_id,
        user_id=current_user.id,
        template_id=request.template_id
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create note for protocol {request.protocol_id}"
        )
    
    return note

@router.post("/notes/followup", response_model=ClinicalNote)
async def create_followup_note(
    request: FollowupNoteRequest,
    current_user: UserIdentity = Depends(get_current_active_user)
):
    """
    Auto-generate a follow-up note based on a previous note.
    """
    note = await auto_generate_followup(
        original_note_id=request.original_note_id,
        user_id=current_user.id,
        days_since_surgery=request.days_since_surgery
    )
    
    if not note:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to create follow-up note for {request.original_note_id}"
        )
    
    return note
