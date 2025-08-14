"""Healthcare-specific validation classes."""

import re
from datetime import datetime, date
from typing import Any, Dict, List, Optional, Union
import json

from .base import BaseValidator, ValidationResult


class PHIValidator(BaseValidator):
    """Validator for Protected Health Information (PHI) compliance."""
    
    # Common PHI patterns to detect
    SSN_PATTERN = re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    DATE_PATTERN = re.compile(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b')
    
    # Medical record number patterns
    MRN_PATTERNS = [
        re.compile(r'\bMRN\s*:?\s*\d+\b', re.IGNORECASE),
        re.compile(r'\b\d{6,10}\b'),  # Generic numeric IDs
    ]
    
    def __init__(self, allow_masked: bool = True, strict: bool = True):
        """
        Initialize PHI validator.
        
        Args:
            allow_masked: Whether to allow masked PHI (e.g., XXX-XX-1234)
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.allow_masked = allow_masked
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate that data doesn't contain unprotected PHI."""
        result = self._create_result()
        
        if not isinstance(data, str):
            # For non-string data, check if it's a dict/list containing strings
            if isinstance(data, dict):
                for key, value in data.items():
                    sub_result = self.validate(value)
                    result.errors.extend(sub_result.errors)
                    result.warnings.extend(sub_result.warnings)
            elif isinstance(data, list):
                for item in data:
                    sub_result = self.validate(item)
                    result.errors.extend(sub_result.errors)
                    result.warnings.extend(sub_result.warnings)
            return self._handle_result(result)
        
        text = str(data)
        
        # Check for SSN
        ssn_matches = self.SSN_PATTERN.findall(text)
        for match in ssn_matches:
            if not self.allow_masked or not self._is_masked_ssn(match):
                result.add_error(f"Unprotected SSN detected: {self._mask_value(match)}")
        
        # Check for phone numbers
        phone_matches = self.PHONE_PATTERN.findall(text)
        for match in phone_matches:
            if not self.allow_masked or not self._is_masked_phone(match):
                result.add_warning(f"Phone number detected: {self._mask_value(match)}")
        
        # Check for email addresses
        email_matches = self.EMAIL_PATTERN.findall(text)
        for match in email_matches:
            result.add_warning(f"Email address detected: {self._mask_value(match)}")
        
        # Check for dates (potential DOB)
        date_matches = self.DATE_PATTERN.findall(text)
        if len(date_matches) > 0:
            result.add_warning("Date values detected (potential DOB)")
        
        # Check for medical record numbers
        for pattern in self.MRN_PATTERNS:
            mrn_matches = pattern.findall(text)
            for match in mrn_matches:
                result.add_warning(f"Medical record number detected: {self._mask_value(match)}")
        
        return self._handle_result(result)
    
    def _is_masked_ssn(self, ssn: str) -> bool:
        """Check if SSN is properly masked."""
        return 'X' in ssn.upper() or '*' in ssn
    
    def _is_masked_phone(self, phone: str) -> bool:
        """Check if phone number is properly masked."""
        return 'X' in phone.upper() or '*' in phone
    
    def _mask_value(self, value: str) -> str:
        """Mask a value for logging purposes."""
        if len(value) <= 4:
            return '*' * len(value)
        return value[:2] + '*' * (len(value) - 4) + value[-2:]


class FHIRValidator(BaseValidator):
    """Validator for FHIR resources and compliance."""
    
    REQUIRED_RESOURCE_FIELDS = {
        'Patient': ['resourceType', 'id'],
        'Observation': ['resourceType', 'status', 'code', 'subject'],
        'Condition': ['resourceType', 'clinicalStatus', 'code', 'subject'],
        'Medication': ['resourceType', 'code'],
        'Encounter': ['resourceType', 'status', 'class', 'subject'],
    }
    
    VALID_STATUSES = {
        'Observation': ['registered', 'preliminary', 'final', 'amended', 'corrected', 'cancelled'],
        'Condition': ['active', 'recurrence', 'relapse', 'inactive', 'remission', 'resolved'],
        'Encounter': ['planned', 'arrived', 'triaged', 'in-progress', 'onleave', 'finished', 'cancelled'],
    }
    
    def __init__(self, resource_type: str = None, strict: bool = True):
        """
        Initialize FHIR validator.
        
        Args:
            resource_type: Specific FHIR resource type to validate
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.resource_type = resource_type
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate FHIR resource structure and content."""
        result = self._create_result()
        
        if not isinstance(data, dict):
            result.add_error("FHIR resource must be a dictionary/object")
            return self._handle_result(result)
        
        # Check resource type
        resource_type = data.get('resourceType')
        if not resource_type:
            result.add_error("FHIR resource must have 'resourceType' field")
            return self._handle_result(result)
        
        if self.resource_type and resource_type != self.resource_type:
            result.add_error(f"Expected resource type '{self.resource_type}', got '{resource_type}'")
        
        # Validate required fields
        required_fields = self.REQUIRED_RESOURCE_FIELDS.get(resource_type, [])
        for field in required_fields:
            if field not in data:
                result.add_error(f"Required field '{field}' missing from {resource_type}")
        
        # Validate status fields
        if resource_type in self.VALID_STATUSES:
            status = data.get('status')
            if status and status not in self.VALID_STATUSES[resource_type]:
                result.add_error(f"Invalid status '{status}' for {resource_type}")
        
        # Validate ID format
        resource_id = data.get('id')
        if resource_id and not self._is_valid_fhir_id(resource_id):
            result.add_error(f"Invalid FHIR ID format: {resource_id}")
        
        # Check for meta information
        if 'meta' in data:
            meta_result = self._validate_meta(data['meta'])
            result.errors.extend(meta_result.errors)
            result.warnings.extend(meta_result.warnings)
        
        return self._handle_result(result)
    
    def _is_valid_fhir_id(self, resource_id: str) -> bool:
        """Validate FHIR ID format."""
        # FHIR IDs must be 1-64 characters, alphanumeric plus - and .
        pattern = re.compile(r'^[A-Za-z0-9\-\.]{1,64}$')
        return bool(pattern.match(resource_id))
    
    def _validate_meta(self, meta: Dict) -> ValidationResult:
        """Validate FHIR meta information."""
        result = self._create_result()
        
        # Check version ID format
        if 'versionId' in meta:
            version_id = meta['versionId']
            if not isinstance(version_id, str) or len(version_id) == 0:
                result.add_error("Meta versionId must be a non-empty string")
        
        # Check last updated timestamp
        if 'lastUpdated' in meta:
            last_updated = meta['lastUpdated']
            try:
                datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            except ValueError:
                result.add_error(f"Invalid lastUpdated timestamp: {last_updated}")
        
        return result


class HL7Validator(BaseValidator):
    """Validator for HL7 message format and content."""
    
    def __init__(self, message_type: str = None, strict: bool = True):
        """
        Initialize HL7 validator.
        
        Args:
            message_type: Expected HL7 message type (e.g., 'ADT^A01')
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.message_type = message_type
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate HL7 message structure."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("HL7 message must be a string")
            return self._handle_result(result)
        
        lines = data.strip().split('\n')
        if not lines:
            result.add_error("HL7 message cannot be empty")
            return self._handle_result(result)
        
        # Check MSH header
        msh_line = lines[0]
        if not msh_line.startswith('MSH'):
            result.add_error("HL7 message must start with MSH segment")
            return self._handle_result(result)
        
        # Parse field separator
        if len(msh_line) < 4:
            result.add_error("MSH segment too short")
            return self._handle_result(result)
        
        field_separator = msh_line[3]
        segments = msh_line.split(field_separator)
        
        if len(segments) < 12:
            result.add_error("MSH segment missing required fields")
        
        # Check message type if specified
        if self.message_type and len(segments) > 9:
            message_type = segments[9]
            if message_type != self.message_type:
                result.add_error(f"Expected message type '{self.message_type}', got '{message_type}'")
        
        # Validate each segment
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            
            segment_result = self._validate_segment(line, field_separator)
            if segment_result.has_errors:
                result.add_error(f"Segment {i+1}: {'; '.join(segment_result.errors)}")
        
        return self._handle_result(result)
    
    def _validate_segment(self, segment: str, field_separator: str) -> ValidationResult:
        """Validate individual HL7 segment."""
        result = self._create_result()
        
        if len(segment) < 3:
            result.add_error("Segment too short")
            return result
        
        segment_type = segment[:3]
        
        # Check segment type format
        if not segment_type.isalpha():
            result.add_error(f"Invalid segment type: {segment_type}")
        
        # Check field separator usage
        if field_separator not in segment[3:]:
            result.add_warning(f"Segment {segment_type} may be missing field separators")
        
        return result


class MedicalRecordValidator(BaseValidator):
    """Validator for medical record numbers and identifiers."""
    
    def __init__(
        self,
        format_pattern: str = None,
        check_digit: bool = False,
        strict: bool = True
    ):
        """
        Initialize medical record validator.
        
        Args:
            format_pattern: Regex pattern for MRN format
            check_digit: Whether to validate check digit (if applicable)
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.format_pattern = re.compile(format_pattern) if format_pattern else None
        self.check_digit = check_digit
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate medical record number format."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("Medical record number must be a string")
            return self._handle_result(result)
        
        mrn = data.strip()
        
        # Check minimum length
        if len(mrn) < 3:
            result.add_error("Medical record number too short")
        
        # Check maximum length
        if len(mrn) > 20:
            result.add_error("Medical record number too long")
        
        # Check format pattern if provided
        if self.format_pattern and not self.format_pattern.match(mrn):
            result.add_error("Medical record number format invalid")
        
        # Check for common invalid patterns
        if mrn.isdigit() and len(set(mrn)) == 1:
            result.add_error("Medical record number cannot be all same digits")
        
        if mrn.lower() in ['test', 'example', 'sample', 'demo']:
            result.add_warning("Medical record number appears to be a test value")
        
        # Validate check digit if enabled
        if self.check_digit and mrn.isdigit():
            if not self._validate_check_digit(mrn):
                result.add_error("Medical record number check digit validation failed")
        
        return self._handle_result(result)
    
    def _validate_check_digit(self, mrn: str) -> bool:
        """Validate check digit using Luhn algorithm."""
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]
            
            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d*2))
            return checksum % 10
        
        return luhn_checksum(mrn) == 0


class ClinicalCodeValidator(BaseValidator):
    """Validator for clinical coding systems (ICD, CPT, SNOMED, etc.)."""
    
    CODE_PATTERNS = {
        'ICD10': re.compile(r'^[A-Z]\d{2}(\.\d{1,3})?$'),
        'ICD9': re.compile(r'^\d{3}(\.\d{1,2})?$'),
        'CPT': re.compile(r'^\d{5}$'),
        'HCPCS': re.compile(r'^[A-Z]\d{4}$'),
        'SNOMED': re.compile(r'^\d{6,18}$'),
        'LOINC': re.compile(r'^\d{4,5}-\d$'),
    }
    
    def __init__(self, code_system: str, strict: bool = True):
        """
        Initialize clinical code validator.
        
        Args:
            code_system: Code system type (ICD10, ICD9, CPT, etc.)
            strict: Strict validation mode
        """
        super().__init__(strict)
        self.code_system = code_system.upper()
        self.pattern = self.CODE_PATTERNS.get(self.code_system)
        
        if not self.pattern:
            raise ValueError(f"Unsupported code system: {code_system}")
    
    def validate(self, data: Any) -> ValidationResult:
        """Validate clinical code format."""
        result = self._create_result()
        
        if not isinstance(data, str):
            result.add_error("Clinical code must be a string")
            return self._handle_result(result)
        
        code = data.strip().upper()
        
        if not self.pattern.match(code):
            result.add_error(f"Invalid {self.code_system} code format: {code}")
        
        # Additional validation for specific code systems
        if self.code_system == 'ICD10':
            result = self._validate_icd10_specific(code, result)
        elif self.code_system == 'CPT':
            result = self._validate_cpt_specific(code, result)
        
        return self._handle_result(result)
    
    def _validate_icd10_specific(self, code: str, result: ValidationResult) -> ValidationResult:
        """Additional ICD-10 specific validation."""
        # Check for valid first character categories
        first_char = code[0]
        valid_first_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        
        if first_char not in valid_first_chars:
            result.add_error(f"Invalid ICD-10 category: {first_char}")
        
        return result
    
    def _validate_cpt_specific(self, code: str, result: ValidationResult) -> ValidationResult:
        """Additional CPT specific validation."""
        # Check for valid CPT code ranges
        code_num = int(code)
        
        valid_ranges = [
            (10021, 69990),  # Medicine
            (70010, 79999),  # Radiology
            (80047, 89398),  # Pathology
            (90281, 99607),  # Medicine
        ]
        
        is_valid_range = any(start <= code_num <= end for start, end in valid_ranges)
        
        if not is_valid_range:
            result.add_warning(f"CPT code {code} may be outside standard ranges")
        
        return result
