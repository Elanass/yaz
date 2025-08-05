"""
Case Service for the Surgify Platform
Handles all case-related operations
"""

from typing import Dict, Any, List, Optional
from surgify.core.models.case import Case
import uuid
import json

class CaseService:
    """
    Case processing service for surgical case management
    """
    def __init__(self):
        # Simple in-memory storage for testing
        self.cases = {}
        self.next_id = 1

    def create_case(self, request):
        # Create a structured case response for testing
        procedure_type = getattr(request, 'procedure_type', None) or getattr(request, 'surgery_type', 'General Surgery')
        diagnosis = getattr(request, 'diagnosis', None) or "To be determined"
        
        case_data = {
            "id": self.next_id,
            "case_number": f"CASE-{uuid.uuid4().hex[:8].upper()}",
            "patient_id": request.patient_id,
            "procedure_type": procedure_type,
            "surgery_type": procedure_type,  # For backward compatibility
            "diagnosis": diagnosis,
            "status": request.status,
            "risk_score": 0.5,  # Default risk score
            "recommendations": ["Standard pre-operative assessment", "Monitor vital signs"]
        }
        self.cases[self.next_id] = case_data
        self.next_id += 1
        return case_data

    def list_cases(self):
        # Return all cases with proper structure
        return list(self.cases.values())

    def get_case(self, case_id):
        # Get a specific case
        if case_id not in self.cases:
            raise Exception("Case not found")
        return self.cases[case_id]

    def update_case(self, case_id, request):
        # Update an existing case
        if case_id not in self.cases:
            raise Exception("Case not found")
        
        procedure_type = getattr(request, 'procedure_type', None) or getattr(request, 'surgery_type', 'General Surgery')
        diagnosis = getattr(request, 'diagnosis', None) or "To be determined"
        
        case_data = self.cases[case_id]
        case_data.update({
            "patient_id": request.patient_id,
            "procedure_type": procedure_type,
            "surgery_type": procedure_type,  # For backward compatibility
            "diagnosis": diagnosis,
            "status": request.status,
        })
        return case_data

    def delete_case(self, case_id):
        # Delete a case
        if case_id not in self.cases:
            raise Exception("Case not found")
        del self.cases[case_id]
