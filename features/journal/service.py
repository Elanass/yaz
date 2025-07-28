"""
Journal Service for Gastric ADCI Platform.

This service provides structured clinical documentation capabilities with
support for standardized templates, auto-generated entries, and
integration with clinical workflows.

Features:
- Structured clinical note templates
- Auto-generation of note content from clinical data
- Support for multi-provider contributions
- Version tracking of clinical documentation
- Integration with ADCI framework
"""

import os
import json
import datetime
import uuid
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

from core.services.logger import get_logger
from core.services.ipfs_client import IPFSClient
from core.services.encryption import encrypt_data
from services.event_logger.service import event_logger, EventCategory, EventSeverity

# Configure logger
logger = get_logger(__name__)

class TemplateField(BaseModel):
    """Definition of a field in a clinical template."""
    field_id: str
    field_name: str
    field_type: str
    required: bool
    options: Optional[List[str]] = None
    validation: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None
    codingSystem: Optional[str] = None
    calculated: Optional[bool] = False
    calculation: Optional[str] = None
    optionDescriptions: Optional[List[str]] = None
    dependsOn: Optional[Dict[str, Any]] = None
    maxLength: Optional[int] = None
    minSelections: Optional[int] = None

class TemplateSection(BaseModel):
    """Section of a clinical template containing related fields."""
    section_id: str
    section_name: str
    required: bool
    fields: List[TemplateField]

class TemplateMetadata(BaseModel):
    """Metadata for a clinical template."""
    created_date: str
    last_updated: str
    target_user_roles: List[str]
    evidence_references: Optional[List[str]] = None
    calculated_fields: Optional[List[str]] = None

class ClinicalTemplate(BaseModel):
    """Complete definition of a clinical template."""
    template_id: str
    template_name: str
    template_version: str
    clinical_domain: str
    description: str
    sections: List[TemplateSection]
    metadata: TemplateMetadata

class FieldValue(BaseModel):
    """Value for a specific template field."""
    field_id: str
    value: Any
    entered_by: str
    entered_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    modified_by: Optional[str] = None
    modified_at: Optional[datetime.datetime] = None
    auto_generated: bool = False
    confidence: Optional[float] = None
    evidence_references: Optional[List[str]] = None

class SectionValues(BaseModel):
    """Values for all fields in a template section."""
    section_id: str
    values: List[FieldValue]
    completed: bool = False
    completed_by: Optional[str] = None
    completed_at: Optional[datetime.datetime] = None

class NoteContributor(BaseModel):
    """Information about a contributor to a clinical note."""
    user_id: str
    role: str
    contribution_type: str  # e.g., "author", "editor", "reviewer", "signer"
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class NoteVersion(BaseModel):
    """Version information for a clinical note."""
    version: int
    timestamp: datetime.datetime
    user_id: str
    changes: Dict[str, Any]
    reason: Optional[str] = None

class ClinicalNote(BaseModel):
    """Complete clinical note with template values and metadata."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str
    patient_id: str
    encounter_id: Optional[str] = None
    title: str
    status: str = "draft"  # draft, completed, signed, amended
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    created_by: str
    modified_at: Optional[datetime.datetime] = None
    modified_by: Optional[str] = None
    completed_at: Optional[datetime.datetime] = None
    completed_by: Optional[str] = None
    signed_at: Optional[datetime.datetime] = None
    signed_by: Optional[str] = None
    sections: List[SectionValues]
    contributors: List[NoteContributor] = []
    versions: List[NoteVersion] = []
    tags: List[str] = []
    protocol_id: Optional[str] = None
    locked: bool = False
    ipfs_cid: Optional[str] = None  # For immutable storage
    
    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat()
        }

class JournalService:
    """Service for managing clinical notes and templates."""
    
    def __init__(self, templates_path: str = "features/journal/templates"):
        self.templates_path = templates_path
        self.templates: Dict[str, ClinicalTemplate] = {}
        self.notes: Dict[str, ClinicalNote] = {}
        self.ipfs_client = IPFSClient()
        
        # Load all templates
        self._load_templates()
    
    def _load_templates(self):
        """Load all clinical templates from the templates directory."""
        try:
            for filename in os.listdir(self.templates_path):
                if filename.endswith(".json"):
                    file_path = os.path.join(self.templates_path, filename)
                    with open(file_path, "r") as f:
                        template_data = json.load(f)
                        template = ClinicalTemplate(**template_data)
                        self.templates[template.template_id] = template
                        logger.info(f"Loaded template: {template.template_id} - {template.template_name}")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
    
    async def get_template(self, template_id: str) -> Optional[ClinicalTemplate]:
        """Get a clinical template by ID."""
        return self.templates.get(template_id)
    
    async def list_templates(
        self, 
        clinical_domain: Optional[str] = None,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List available clinical templates with optional filtering.
        
        Args:
            clinical_domain: Filter by clinical domain
            role: Filter by target user role
            
        Returns:
            List of template summaries
        """
        result = []
        for template_id, template in self.templates.items():
            # Apply filters
            if clinical_domain and template.clinical_domain != clinical_domain:
                continue
                
            if role and role not in template.metadata.target_user_roles:
                continue
                
            # Create template summary
            summary = {
                "template_id": template.template_id,
                "template_name": template.template_name,
                "template_version": template.template_version,
                "clinical_domain": template.clinical_domain,
                "description": template.description,
                "last_updated": template.metadata.last_updated
            }
            
            result.append(summary)
            
        return result
    
    async def create_note(
        self,
        template_id: str,
        patient_id: str,
        title: str,
        created_by: str,
        encounter_id: Optional[str] = None,
        protocol_id: Optional[str] = None,
        initial_values: Optional[Dict[str, Dict[str, Any]]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[ClinicalNote]:
        """
        Create a new clinical note based on a template.
        
        Args:
            template_id: ID of the template to use
            patient_id: Patient ID
            title: Note title
            created_by: ID of the user creating the note
            encounter_id: Optional encounter ID
            protocol_id: Optional protocol ID
            initial_values: Optional initial field values by section
            tags: Optional tags for the note
            
        Returns:
            The created clinical note, or None if the template doesn't exist
        """
        # Get the template
        template = await self.get_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        # Initialize sections with empty values
        sections: List[SectionValues] = []
        for section in template.sections:
            section_values = SectionValues(
                section_id=section.section_id,
                values=[]
            )
            
            # Add empty values for each field
            for field in section.fields:
                # Check if we have an initial value for this field
                initial_value = None
                if (initial_values and 
                    section.section_id in initial_values and 
                    field.field_id in initial_values[section.section_id]):
                    initial_value = initial_values[section.section_id][field.field_id]
                
                # Create field value
                field_value = FieldValue(
                    field_id=field.field_id,
                    value=initial_value,
                    entered_by=created_by,
                    auto_generated=initial_value is not None
                )
                
                section_values.values.append(field_value)
            
            sections.append(section_values)
        
        # Create the note
        note = ClinicalNote(
            template_id=template_id,
            patient_id=patient_id,
            encounter_id=encounter_id,
            title=title,
            created_by=created_by,
            sections=sections,
            contributors=[
                NoteContributor(
                    user_id=created_by,
                    role="clinician",  # This would be dynamically determined
                    contribution_type="author"
                )
            ],
            protocol_id=protocol_id,
            tags=tags or []
        )
        
        # Store the note
        self.notes[note.id] = note
        
        # Log the creation
        await event_logger.log_event(
            category=EventCategory.DATA_MODIFICATION,
            severity=EventSeverity.INFO,
            source={
                "component": "journal_service",
                "service": "journal"
            },
            context={
                "patient_id": patient_id,
                "provider_id": created_by
            },
            data={
                "action": "CREATE_NOTE",
                "resource_type": "CLINICAL_NOTE",
                "resource_id": note.id,
                "metadata": {
                    "template_id": template_id,
                    "title": title
                }
            },
            message=f"Clinical note created: {title} for patient {patient_id}"
        )
        
        return note
    
    async def update_note_field(
        self,
        note_id: str,
        section_id: str,
        field_id: str,
        value: Any,
        user_id: str,
        auto_generated: bool = False,
        confidence: Optional[float] = None,
        evidence_references: Optional[List[str]] = None
    ) -> Optional[ClinicalNote]:
        """
        Update a field value in a clinical note.
        
        Args:
            note_id: ID of the note to update
            section_id: ID of the section containing the field
            field_id: ID of the field to update
            value: New field value
            user_id: ID of the user making the update
            auto_generated: Whether the value was auto-generated
            confidence: Optional confidence score for auto-generated values
            evidence_references: Optional references to evidence
            
        Returns:
            The updated clinical note, or None if the note doesn't exist
        """
        # Get the note
        note = self.notes.get(note_id)
        if not note:
            logger.error(f"Note not found: {note_id}")
            return None
        
        # Check if note is locked
        if note.locked:
            logger.error(f"Cannot update locked note: {note_id}")
            return None
        
        # Find the section
        section = next((s for s in note.sections if s.section_id == section_id), None)
        if not section:
            logger.error(f"Section not found: {section_id} in note {note_id}")
            return None
        
        # Find the field
        field = next((f for f in section.values if f.field_id == field_id), None)
        if not field:
            logger.error(f"Field not found: {field_id} in section {section_id} of note {note_id}")
            return None
        
        # Create a version entry for tracking changes
        version = NoteVersion(
            version=len(note.versions) + 1,
            timestamp=datetime.datetime.utcnow(),
            user_id=user_id,
            changes={
                "section_id": section_id,
                "field_id": field_id,
                "old_value": field.value,
                "new_value": value
            }
        )
        
        # Update the field
        field.value = value
        field.modified_by = user_id
        field.modified_at = datetime.datetime.utcnow()
        field.auto_generated = auto_generated
        field.confidence = confidence
        field.evidence_references = evidence_references
        
        # Update note metadata
        note.modified_at = datetime.datetime.utcnow()
        note.modified_by = user_id
        note.versions.append(version)
        
        # Check if this user is already a contributor
        if not any(c.user_id == user_id for c in note.contributors):
            # Add as a contributor
            note.contributors.append(
                NoteContributor(
                    user_id=user_id,
                    role="clinician",  # This would be dynamically determined
                    contribution_type="editor"
                )
            )
        
        # Log the update
        await event_logger.log_event(
            category=EventCategory.DATA_MODIFICATION,
            severity=EventSeverity.INFO,
            source={
                "component": "journal_service",
                "service": "journal"
            },
            context={
                "patient_id": note.patient_id,
                "provider_id": user_id
            },
            data={
                "action": "UPDATE_NOTE_FIELD",
                "resource_type": "CLINICAL_NOTE",
                "resource_id": note.id,
                "metadata": {
                    "section_id": section_id,
                    "field_id": field_id,
                    "version": version.version
                }
            },
            message=f"Clinical note field updated: {field_id} in note {note.id}"
        )
        
        return note
    
    async def complete_section(
        self,
        note_id: str,
        section_id: str,
        user_id: str
    ) -> Optional[ClinicalNote]:
        """
        Mark a section as completed in a clinical note.
        
        Args:
            note_id: ID of the note
            section_id: ID of the section to complete
            user_id: ID of the user completing the section
            
        Returns:
            The updated clinical note, or None if the note doesn't exist
        """
        # Get the note
        note = self.notes.get(note_id)
        if not note:
            logger.error(f"Note not found: {note_id}")
            return None
        
        # Check if note is locked
        if note.locked:
            logger.error(f"Cannot update locked note: {note_id}")
            return None
        
        # Find the section
        section = next((s for s in note.sections if s.section_id == section_id), None)
        if not section:
            logger.error(f"Section not found: {section_id} in note {note_id}")
            return None
        
        # Mark section as completed
        section.completed = True
        section.completed_by = user_id
        section.completed_at = datetime.datetime.utcnow()
        
        # Update note metadata
        note.modified_at = datetime.datetime.utcnow()
        note.modified_by = user_id
        
        # Log the completion
        await event_logger.log_event(
            category=EventCategory.DATA_MODIFICATION,
            severity=EventSeverity.INFO,
            source={
                "component": "journal_service",
                "service": "journal"
            },
            context={
                "patient_id": note.patient_id,
                "provider_id": user_id
            },
            data={
                "action": "COMPLETE_SECTION",
                "resource_type": "CLINICAL_NOTE",
                "resource_id": note.id,
                "metadata": {
                    "section_id": section_id
                }
            },
            message=f"Clinical note section completed: {section_id} in note {note.id}"
        )
        
        return note
    
    async def complete_note(
        self,
        note_id: str,
        user_id: str
    ) -> Optional[ClinicalNote]:
        """
        Mark a clinical note as completed.
        
        Args:
            note_id: ID of the note to complete
            user_id: ID of the user completing the note
            
        Returns:
            The updated clinical note, or None if the note doesn't exist
        """
        # Get the note
        note = self.notes.get(note_id)
        if not note:
            logger.error(f"Note not found: {note_id}")
            return None
        
        # Check if note is locked
        if note.locked:
            logger.error(f"Cannot update locked note: {note_id}")
            return None
        
        # Get the template to check required fields
        template = await self.get_template(note.template_id)
        if not template:
            logger.error(f"Template not found: {note.template_id}")
            return None
        
        # Check if all required sections are completed
        incomplete_sections = []
        for template_section in template.sections:
            if not template_section.required:
                continue
                
            # Find the corresponding section in the note
            note_section = next((s for s in note.sections if s.section_id == template_section.section_id), None)
            if not note_section or not note_section.completed:
                incomplete_sections.append(template_section.section_name)
        
        if incomplete_sections:
            sections_str = ", ".join(incomplete_sections)
            logger.error(f"Cannot complete note {note_id}: Required sections not completed: {sections_str}")
            return None
        
        # Update note status
        note.status = "completed"
        note.completed_at = datetime.datetime.utcnow()
        note.completed_by = user_id
        
        # Log the completion
        await event_logger.log_event(
            category=EventCategory.DATA_MODIFICATION,
            severity=EventSeverity.INFO,
            source={
                "component": "journal_service",
                "service": "journal"
            },
            context={
                "patient_id": note.patient_id,
                "provider_id": user_id
            },
            data={
                "action": "COMPLETE_NOTE",
                "resource_type": "CLINICAL_NOTE",
                "resource_id": note.id
            },
            message=f"Clinical note completed: {note.title} for patient {note.patient_id}"
        )
        
        return note
    
    async def sign_note(
        self,
        note_id: str,
        user_id: str
    ) -> Optional[ClinicalNote]:
        """
        Sign a clinical note, finalizing it for the medical record.
        
        Args:
            note_id: ID of the note to sign
            user_id: ID of the user signing the note
            
        Returns:
            The updated clinical note, or None if the note doesn't exist
        """
        # Get the note
        note = self.notes.get(note_id)
        if not note:
            logger.error(f"Note not found: {note_id}")
            return None
        
        # Check if note is completed
        if note.status != "completed":
            logger.error(f"Cannot sign note {note_id}: Note is not completed")
            return None
        
        # Update note status
        note.status = "signed"
        note.signed_at = datetime.datetime.utcnow()
        note.signed_by = user_id
        note.locked = True
        
        # Store on IPFS for immutability
        try:
            note_json = note.json()
            cid = await self.ipfs_client.add_json(note_json)
            note.ipfs_cid = cid
            logger.info(f"Note {note_id} stored on IPFS with CID: {cid}")
        except Exception as e:
            logger.error(f"Failed to store note {note_id} on IPFS: {str(e)}")
        
        # Add signing contributor
        note.contributors.append(
            NoteContributor(
                user_id=user_id,
                role="clinician",  # This would be dynamically determined
                contribution_type="signer"
            )
        )
        
        # Log the signing
        await event_logger.log_event(
            category=EventCategory.DATA_MODIFICATION,
            severity=EventSeverity.INFO,
            source={
                "component": "journal_service",
                "service": "journal"
            },
            context={
                "patient_id": note.patient_id,
                "provider_id": user_id
            },
            data={
                "action": "SIGN_NOTE",
                "resource_type": "CLINICAL_NOTE",
                "resource_id": note.id,
                "metadata": {
                    "ipfs_cid": note.ipfs_cid
                }
            },
            message=f"Clinical note signed: {note.title} for patient {note.patient_id}"
        )
        
        return note
    
    async def amend_note(
        self,
        note_id: str,
        user_id: str,
        reason: str
    ) -> Optional[ClinicalNote]:
        """
        Create an amended version of a signed note.
        
        Args:
            note_id: ID of the note to amend
            user_id: ID of the user creating the amendment
            reason: Reason for the amendment
            
        Returns:
            The new amended note, or None if the original note doesn't exist
        """
        # Get the original note
        original_note = self.notes.get(note_id)
        if not original_note:
            logger.error(f"Note not found: {note_id}")
            return None
        
        # Check if note is signed
        if original_note.status != "signed":
            logger.error(f"Cannot amend note {note_id}: Note is not signed")
            return None
        
        # Create a new note based on the original
        new_note = ClinicalNote(
            template_id=original_note.template_id,
            patient_id=original_note.patient_id,
            encounter_id=original_note.encounter_id,
            title=f"{original_note.title} (Amended)",
            created_by=user_id,
            sections=original_note.sections.copy(),
            contributors=[
                NoteContributor(
                    user_id=user_id,
                    role="clinician",  # This would be dynamically determined
                    contribution_type="author"
                )
            ],
            protocol_id=original_note.protocol_id,
            tags=original_note.tags + ["amended"]
        )
        
        # Add version with amendment reason
        new_note.versions.append(
            NoteVersion(
                version=1,
                timestamp=datetime.datetime.utcnow(),
                user_id=user_id,
                changes={"amendment": True, "original_note_id": original_note.id},
                reason=reason
            )
        )
        
        # Store the new note
        self.notes[new_note.id] = new_note
        
        # Log the amendment
        await event_logger.log_event(
            category=EventCategory.DATA_MODIFICATION,
            severity=EventSeverity.INFO,
            source={
                "component": "journal_service",
                "service": "journal"
            },
            context={
                "patient_id": original_note.patient_id,
                "provider_id": user_id
            },
            data={
                "action": "AMEND_NOTE",
                "resource_type": "CLINICAL_NOTE",
                "resource_id": new_note.id,
                "metadata": {
                    "original_note_id": original_note.id,
                    "reason": reason
                }
            },
            message=f"Clinical note amended: {original_note.title} for patient {original_note.patient_id}"
        )
        
        return new_note
    
    async def get_note(self, note_id: str) -> Optional[ClinicalNote]:
        """Get a clinical note by ID."""
        return self.notes.get(note_id)
    
    async def get_notes_for_patient(
        self,
        patient_id: str,
        template_id: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime.datetime] = None,
        date_to: Optional[datetime.datetime] = None,
        tags: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ClinicalNote]:
        """
        Get clinical notes for a patient with filtering.
        
        Args:
            patient_id: Patient ID to filter by
            template_id: Optional template ID to filter by
            status: Optional status to filter by
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            tags: Optional tags to filter by
            limit: Maximum number of notes to return
            offset: Offset for pagination
            
        Returns:
            List of matching clinical notes
        """
        # Filter notes
        filtered_notes = []
        for note in self.notes.values():
            if note.patient_id != patient_id:
                continue
                
            if template_id and note.template_id != template_id:
                continue
                
            if status and note.status != status:
                continue
                
            if date_from and note.created_at < date_from:
                continue
                
            if date_to and note.created_at > date_to:
                continue
                
            if tags and not all(tag in note.tags for tag in tags):
                continue
                
            filtered_notes.append(note)
        
        # Sort by created_at descending (newest first)
        filtered_notes.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        paginated_notes = filtered_notes[offset:offset + limit]
        
        return paginated_notes
    
    async def auto_generate_fields(
        self,
        note_id: str,
        user_id: str,
        data_source: Dict[str, Any]
    ) -> Optional[ClinicalNote]:
        """
        Auto-generate field values from external data sources.
        
        Args:
            note_id: ID of the note to update
            user_id: ID of the user initiating the auto-generation
            data_source: Dictionary of data to use for field generation
            
        Returns:
            The updated clinical note, or None if the note doesn't exist
        """
        # Get the note
        note = self.notes.get(note_id)
        if not note:
            logger.error(f"Note not found: {note_id}")
            return None
        
        # Check if note is locked
        if note.locked:
            logger.error(f"Cannot update locked note: {note_id}")
            return None
        
        # Get the template
        template = await self.get_template(note.template_id)
        if not template:
            logger.error(f"Template not found: {note.template_id}")
            return None
        
        # Map of section.field_id to auto-generated values
        auto_values = {}
        
        # Process data source to generate field values
        if "patient_demographics" in data_source:
            demo = data_source["patient_demographics"]
            
            if "age" in demo:
                auto_values["patient_demographics.age"] = demo["age"]
                
            if "sex" in demo:
                auto_values["patient_demographics.sex"] = demo["sex"]
                
            if "weight_kg" in demo and "height_m" in demo:
                # Calculate BMI
                weight = demo["weight_kg"]
                height = demo["height_m"]
                bmi = weight / (height * height)
                auto_values["patient_demographics.bmi"] = round(bmi, 1)
                
            if "ecog" in demo:
                auto_values["patient_demographics.performance_status"] = demo["ecog"]
        
        if "tumor_data" in data_source:
            tumor = data_source["tumor_data"]
            
            if "location" in tumor:
                auto_values["tumor_characteristics.tumor_location"] = tumor["location"]
                
            if "size_cm" in tumor:
                auto_values["tumor_characteristics.tumor_size"] = tumor["size_cm"]
                
            if "histology" in tumor:
                auto_values["tumor_characteristics.histological_type"] = tumor["histology"]
                
            if "differentiation" in tumor:
                auto_values["tumor_characteristics.differentiation"] = tumor["differentiation"]
                
            if "lauren" in tumor:
                auto_values["tumor_characteristics.lauren_classification"] = tumor["lauren"]
        
        if "staging" in data_source:
            staging = data_source["staging"]
            
            if "clinical_t" in staging:
                auto_values["staging.clinical_t"] = staging["clinical_t"]
                
            if "clinical_n" in staging:
                auto_values["staging.clinical_n"] = staging["clinical_n"]
                
            if "clinical_m" in staging:
                auto_values["staging.clinical_m"] = staging["clinical_m"]
                
            if "methods" in staging:
                auto_values["staging.staging_method"] = staging["methods"]
        
        # Add more mappings for other data sources
        
        # Apply auto-generated values
        for key, value in auto_values.items():
            section_id, field_id = key.split(".")
            
            # Update the field
            await self.update_note_field(
                note_id=note_id,
                section_id=section_id,
                field_id=field_id,
                value=value,
                user_id=user_id,
                auto_generated=True,
                confidence=0.95  # Default high confidence for direct mappings
            )
        
        return note


# Create a singleton instance
journal_service = JournalService()
