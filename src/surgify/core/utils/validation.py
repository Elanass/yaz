"""
Validation Utilities for Collaborative Gastric ADCI Platform

This module provides centralized validation functions used throughout the platform
to ensure consistent validation logic and DRY principles.
"""

from typing import Dict, Any, List, Optional, Tuple, Union

from surgify.core.services.logger import get_logger

logger = get_logger(__name__)


def validate_patient_data(
    patient_data: Dict[str, Any], validation_type: str = "basic"
) -> Tuple[bool, List[str]]:
    """
    Centralized patient data validation function

    Args:
        patient_data: The patient data to validate
        validation_type: Type of validation to perform:
            - "basic": Basic fields only
            - "adci": ADCI-specific validation
            - "flot": FLOT-specific validation
            - "comprehensive": Full validation for all modules

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    # Common required fields across all validation types
    common_required_fields = ["patient_id", "age", "gender"]

    # Specific validation fields
    validation_fields = {
        "basic": common_required_fields + ["diagnosis"],
        "adci": common_required_fields
        + ["diagnosis", "lab_results", "surgical_history", "comorbidities"],
        "flot": common_required_fields
        + [
            "performance_status",
            "tumor_stage",
            "histology",
            "comorbidities",
            "prior_treatments",
            "lab_results",
            "imaging_findings",
        ],
        "comprehensive": common_required_fields
        + [
            "diagnosis",
            "lab_results",
            "surgical_history",
            "comorbidities",
            "performance_status",
            "tumor_stage",
            "histology",
            "prior_treatments",
            "imaging_findings",
            "vital_signs",
            "medications",
            "allergies",
        ],
    }

    # Get the required fields based on validation type
    required_fields = validation_fields.get(validation_type, validation_fields["basic"])

    # Check for missing fields
    missing_fields = [field for field in required_fields if field not in patient_data]

    # Validate age range if present
    if "age" in patient_data and not missing_fields:
        age = patient_data.get("age", 0)
        if not isinstance(age, (int, float)) or age < 0 or age > 120:
            missing_fields.append("age (invalid range)")

    # Return validation result
    is_valid = len(missing_fields) == 0

    if not is_valid:
        logger.warning(
            f"Patient data validation failed for type {validation_type}. Missing fields: {missing_fields}"
        )

    return is_valid, missing_fields


def validate_surgical_case(case_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate surgical case data

    Args:
        case_data: The surgical case data to validate

    Returns:
        Tuple of (is_valid, missing_fields)
    """
    required_fields = [
        "case_id",
        "patient_id",
        "surgery_type",
        "diagnosis",
        "surgical_plan",
        "clinical_staging",
    ]

    missing_fields = [field for field in required_fields if field not in case_data]
    is_valid = len(missing_fields) == 0

    if not is_valid:
        logger.warning(
            f"Surgical case validation failed. Missing fields: {missing_fields}"
        )

    return is_valid, missing_fields


def validate_collaboration_input(input_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate collaboration input data

    Args:
        input_data: The collaboration input data to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for either opinion or evidence
    if "opinion" not in input_data and "evidence" not in input_data:
        return False, "Collaboration must include either opinion or evidence"

    # Check for required fields
    if "case_id" not in input_data and "patient_id" not in input_data:
        return False, "Either case_id or patient_id must be provided"

    return True, ""
