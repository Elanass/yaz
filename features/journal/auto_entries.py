"""
Auto-entries module for journal service.

This module provides functionality for automatically generating clinical note
content from various data sources, including EMR data, decision engine outputs,
and structured protocols.
"""

import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

from core.services.logger import get_logger
from features.journal.service import journal_service, ClinicalNote
from adapters.open_source.openmrs_adapter import openmrs_client
from adapters.open_source.hapi_fhir_adapter import fhir_client

# Configure logger
logger = get_logger(__name__)

class DataSourceConfig(BaseModel):
    """Configuration for a data source for auto-generation."""
    source_type: str  # "emr", "fhir", "adci", "lab", "protocol"
    endpoint: Optional[str] = None
    mapping: Dict[str, str] = {}  # Maps source fields to template fields
    required: bool = False

class AutoEntryTemplate(BaseModel):
    """Template for auto-generating entries in clinical notes."""
    template_id: str
    section_fields: List[str]
    data_sources: List[DataSourceConfig]
    confidence_threshold: float = 0.75
    requires_validation: bool = True

# Dictionary of auto-entry templates by template_id
auto_entry_templates: Dict[str, AutoEntryTemplate] = {
    "gastric-surgical-assessment": AutoEntryTemplate(
        template_id="gastric-surgical-assessment",
        section_fields=[
            "patient_demographics.age",
            "patient_demographics.sex",
            "patient_demographics.bmi",
            "patient_demographics.performance_status",
            "tumor_characteristics.tumor_location",
            "tumor_characteristics.tumor_size",
            "tumor_characteristics.histological_type",
            "tumor_characteristics.differentiation",
            "staging.clinical_t",
            "staging.clinical_n",
            "staging.clinical_m",
            "comorbidities.asa_class",
            "comorbidities.cardiovascular",
            "comorbidities.respiratory",
            "comorbidities.diabetes",
            "nutritional_status.weight_loss",
            "nutritional_status.albumin"
        ],
        data_sources=[
            DataSourceConfig(
                source_type="emr",
                endpoint="patient_demographics",
                mapping={
                    "age": "patient_demographics.age",
                    "sex": "patient_demographics.sex",
                    "height": "patient_demographics.height_m",
                    "weight": "patient_demographics.weight_kg",
                    "ecog_status": "patient_demographics.performance_status"
                },
                required=True
            ),
            DataSourceConfig(
                source_type="emr",
                endpoint="clinical_findings",
                mapping={
                    "tumor_location": "tumor_characteristics.tumor_location",
                    "tumor_size_cm": "tumor_characteristics.tumor_size",
                    "histology": "tumor_characteristics.histological_type",
                    "differentiation": "tumor_characteristics.differentiation",
                    "lauren_class": "tumor_characteristics.lauren_classification"
                }
            ),
            DataSourceConfig(
                source_type="emr",
                endpoint="staging",
                mapping={
                    "t_stage": "staging.clinical_t",
                    "n_stage": "staging.clinical_n",
                    "m_stage": "staging.clinical_m",
                    "staging_methods": "staging.staging_method"
                }
            ),
            DataSourceConfig(
                source_type="emr",
                endpoint="comorbidities",
                mapping={
                    "asa_class": "comorbidities.asa_class",
                    "cardiovascular": "comorbidities.cardiovascular",
                    "respiratory": "comorbidities.respiratory",
                    "diabetes": "comorbidities.diabetes",
                    "charlson_score": "comorbidities.charlson_score"
                }
            ),
            DataSourceConfig(
                source_type="lab",
                endpoint="lab_results",
                mapping={
                    "albumin": "nutritional_status.albumin",
                    "weight_loss_percent": "nutritional_status.weight_loss"
                }
            ),
            DataSourceConfig(
                source_type="adci",
                endpoint="decision_output",
                mapping={
                    "adci_score": "adci_assessment.adci_score",
                    "confidence_interval": "adci_assessment.confidence_interval",
                    "recommendation": "adci_assessment.recommendation",
                    "key_factors": "adci_assessment.key_factors"
                }
            )
        ]
    ),
    "gastric-post-surgery-followup": AutoEntryTemplate(
        template_id="gastric-post-surgery-followup",
        section_fields=[
            "surgical_procedure.procedure_performed",
            "surgical_procedure.procedure_date",
            "surgical_procedure.lymphadenectomy",
            "surgical_procedure.approach",
            "surgical_procedure.reconstruction",
            "pathology_summary.path_t",
            "pathology_summary.path_n",
            "pathology_summary.path_m",
            "pathology_summary.margins",
            "pathology_summary.lymph_nodes_harvested",
            "pathology_summary.lymph_nodes_positive",
            "postop_complications.clavien_dindo",
            "postop_complications.complication_types",
            "postop_complications.readmission",
            "current_status.weight",
            "current_status.performance_status"
        ],
        data_sources=[
            DataSourceConfig(
                source_type="emr",
                endpoint="surgical_procedure",
                mapping={
                    "procedure": "surgical_procedure.procedure_performed",
                    "date": "surgical_procedure.procedure_date",
                    "lymphadenectomy": "surgical_procedure.lymphadenectomy",
                    "approach": "surgical_procedure.approach",
                    "reconstruction": "surgical_procedure.reconstruction"
                },
                required=True
            ),
            DataSourceConfig(
                source_type="emr",
                endpoint="pathology",
                mapping={
                    "t_stage": "pathology_summary.path_t",
                    "n_stage": "pathology_summary.path_n",
                    "m_stage": "pathology_summary.path_m",
                    "margins": "pathology_summary.margins",
                    "nodes_harvested": "pathology_summary.lymph_nodes_harvested",
                    "nodes_positive": "pathology_summary.lymph_nodes_positive"
                }
            ),
            DataSourceConfig(
                source_type="emr",
                endpoint="complications",
                mapping={
                    "clavien_dindo": "postop_complications.clavien_dindo",
                    "complication_types": "postop_complications.complication_types",
                    "readmission": "postop_complications.readmission",
                    "readmission_reason": "postop_complications.readmission_reason"
                }
            ),
            DataSourceConfig(
                source_type="emr",
                endpoint="patient_status",
                mapping={
                    "weight": "current_status.weight",
                    "ecog_status": "current_status.performance_status",
                    "pain_score": "current_status.pain_score",
                    "pain_location": "current_status.pain_location"
                }
            ),
            DataSourceConfig(
                source_type="lab",
                endpoint="lab_results",
                mapping={
                    "albumin": "nutritional_assessment.albumin"
                }
            )
        ]
    )
}


async def fetch_data_from_source(
    source_config: DataSourceConfig,
    patient_id: str,
    encounter_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Fetch data from a configured data source.
    
    Args:
        source_config: Configuration for the data source
        patient_id: Patient ID
        encounter_id: Optional encounter ID
        
    Returns:
        Dictionary of data from the source
    """
    result = {}
    
    try:
        if source_config.source_type == "emr":
            # Fetch data from OpenMRS
            if source_config.endpoint == "patient_demographics":
                patient_data = await openmrs_client.get_patient(patient_id)
                if patient_data:
                    result = {
                        "age": patient_data.get("age"),
                        "sex": patient_data.get("gender"),
                        "height": patient_data.get("height"),
                        "weight": patient_data.get("weight"),
                        "ecog_status": patient_data.get("attributes", {}).get("ecog_status")
                    }
            
            elif source_config.endpoint == "clinical_findings":
                findings = await openmrs_client.get_observations(
                    patient_id, 
                    concept="Gastric-Tumor-Assessment"
                )
                if findings:
                    result = {
                        "tumor_location": findings.get("tumor_location"),
                        "tumor_size_cm": findings.get("tumor_size"),
                        "histology": findings.get("histological_type"),
                        "differentiation": findings.get("differentiation"),
                        "lauren_class": findings.get("lauren_classification")
                    }
            
            elif source_config.endpoint == "staging":
                staging_data = await openmrs_client.get_observations(
                    patient_id, 
                    concept="Gastric-Cancer-Staging"
                )
                if staging_data:
                    result = {
                        "t_stage": staging_data.get("t_stage"),
                        "n_stage": staging_data.get("n_stage"),
                        "m_stage": staging_data.get("m_stage"),
                        "staging_methods": staging_data.get("staging_methods", [])
                    }
            
            # Add more endpoint handlers as needed
        
        elif source_config.source_type == "fhir":
            # Fetch data from HAPI FHIR
            if source_config.endpoint == "patient":
                patient_data = await fhir_client.read_resource("Patient", patient_id)
                if patient_data:
                    # Extract relevant data from FHIR Patient resource
                    pass
            
            elif source_config.endpoint == "condition":
                conditions = await fhir_client.search_resources(
                    "Condition",
                    parameters={"patient": patient_id}
                )
                if conditions:
                    # Process conditions
                    pass
        
        elif source_config.source_type == "lab":
            # Fetch lab data
            if source_config.endpoint == "lab_results":
                lab_results = await openmrs_client.get_observations(
                    patient_id, 
                    concept="Laboratory-Results"
                )
                if lab_results:
                    result = {
                        "albumin": lab_results.get("albumin"),
                        "weight_loss_percent": lab_results.get("weight_loss_percentage")
                    }
        
        elif source_config.source_type == "adci":
            # Fetch ADCI decision engine output
            # This would connect to the ADCI decision engine
            # For now, we'll return mock data
            if source_config.endpoint == "decision_output":
                result = {
                    "adci_score": 78.5,
                    "confidence_interval": [72.3, 84.7],
                    "recommendation": "Proceed with planned surgery",
                    "key_factors": [
                        "Tumor location",
                        "Tumor stage",
                        "Performance status",
                        "Nutritional status"
                    ]
                }
    
    except Exception as e:
        logger.error(f"Error fetching data from {source_config.source_type}/{source_config.endpoint}: {str(e)}")
    
    return result


async def map_source_data_to_fields(
    data: Dict[str, Any],
    mapping: Dict[str, str]
) -> Dict[str, Dict[str, Any]]:
    """
    Map data from a source to template fields.
    
    Args:
        data: Data from the source
        mapping: Mapping from source fields to template fields
        
    Returns:
        Dictionary of section IDs to field values
    """
    result: Dict[str, Dict[str, Any]] = {}
    
    for source_field, template_field in mapping.items():
        if source_field in data and data[source_field] is not None:
            # Split the template field into section and field
            section_id, field_id = template_field.split(".")
            
            # Initialize the section if needed
            if section_id not in result:
                result[section_id] = {}
            
            # Map the value
            result[section_id][field_id] = data[source_field]
    
    return result


async def auto_generate_note_content(
    note_id: str,
    patient_id: str,
    template_id: str,
    user_id: str,
    encounter_id: Optional[str] = None
) -> Optional[ClinicalNote]:
    """
    Auto-generate content for a clinical note from various data sources.
    
    Args:
        note_id: ID of the note to update
        patient_id: Patient ID
        template_id: Template ID
        user_id: ID of the user initiating the auto-generation
        encounter_id: Optional encounter ID
        
    Returns:
        The updated clinical note, or None if the note doesn't exist
    """
    # Get the note
    note = await journal_service.get_note(note_id)
    if not note:
        logger.error(f"Note not found: {note_id}")
        return None
    
    # Get the auto-entry template
    auto_template = auto_entry_templates.get(template_id)
    if not auto_template:
        logger.error(f"Auto-entry template not found: {template_id}")
        return None
    
    # Collect data from all sources
    all_field_values: Dict[str, Dict[str, Any]] = {}
    
    for source_config in auto_template.data_sources:
        # Fetch data from the source
        source_data = await fetch_data_from_source(
            source_config,
            patient_id,
            encounter_id
        )
        
        # Skip if required source has no data
        if source_config.required and not source_data:
            logger.warning(f"Required data source {source_config.source_type}/{source_config.endpoint} returned no data")
            continue
        
        # Map data to template fields
        field_values = await map_source_data_to_fields(
            source_data,
            source_config.mapping
        )
        
        # Merge into all field values
        for section_id, section_values in field_values.items():
            if section_id not in all_field_values:
                all_field_values[section_id] = {}
                
            all_field_values[section_id].update(section_values)
    
    # Update the note with auto-generated values
    if all_field_values:
        await journal_service.auto_generate_fields(
            note_id=note_id,
            user_id=user_id,
            data_source=all_field_values
        )
    
    # Return the updated note
    return await journal_service.get_note(note_id)


async def auto_generate_for_protocol(
    protocol_id: str,
    patient_id: str,
    user_id: str,
    template_id: Optional[str] = None
) -> Optional[ClinicalNote]:
    """
    Auto-generate a clinical note based on a protocol.
    
    Args:
        protocol_id: ID of the protocol
        patient_id: Patient ID
        user_id: ID of the user initiating the auto-generation
        template_id: Optional template ID to use (otherwise determined from protocol)
        
    Returns:
        The created clinical note, or None if creation failed
    """
    # Determine template ID from protocol if not provided
    if not template_id:
        # This would look up the appropriate template based on the protocol
        # For now, we'll use a default
        template_id = "gastric-surgical-assessment"
    
    # Create a title for the note
    title = f"Gastric Surgery Assessment - Protocol {protocol_id}"
    
    # Create the note
    note = await journal_service.create_note(
        template_id=template_id,
        patient_id=patient_id,
        title=title,
        created_by=user_id,
        protocol_id=protocol_id
    )
    
    if not note:
        logger.error(f"Failed to create note for protocol {protocol_id}")
        return None
    
    # Auto-generate content
    await auto_generate_note_content(
        note_id=note.id,
        patient_id=patient_id,
        template_id=template_id,
        user_id=user_id
    )
    
    return note


async def auto_generate_followup(
    original_note_id: str,
    user_id: str,
    days_since_surgery: int
) -> Optional[ClinicalNote]:
    """
    Auto-generate a follow-up note based on a previous note.
    
    Args:
        original_note_id: ID of the original note
        user_id: ID of the user initiating the auto-generation
        days_since_surgery: Days since the surgery
        
    Returns:
        The created follow-up note, or None if creation failed
    """
    # Get the original note
    original_note = await journal_service.get_note(original_note_id)
    if not original_note:
        logger.error(f"Original note not found: {original_note_id}")
        return None
    
    # Determine the appropriate follow-up template
    template_id = "gastric-post-surgery-followup"
    
    # Create a title for the follow-up note
    title = f"Post-Surgery Follow-up ({days_since_surgery} days) - {original_note.title}"
    
    # Create the follow-up note
    followup_note = await journal_service.create_note(
        template_id=template_id,
        patient_id=original_note.patient_id,
        title=title,
        created_by=user_id,
        protocol_id=original_note.protocol_id,
        tags=["followup"]
    )
    
    if not followup_note:
        logger.error(f"Failed to create follow-up note for {original_note_id}")
        return None
    
    # Auto-generate content
    await auto_generate_note_content(
        note_id=followup_note.id,
        patient_id=original_note.patient_id,
        template_id=template_id,
        user_id=user_id
    )
    
    return followup_note
