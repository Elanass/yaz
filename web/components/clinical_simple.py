"""
Clinical Platform Components - Simplified
"""

from fasthtml.common import *
from typing import Dict, Any

def create_patient_summary(patient_data: Dict[str, Any]):
    """Simple patient summary component"""
    return Div(
        H3("Patient Summary"),
        *[P(f"{k.replace('_', ' ').title()}: {v}") for k, v in patient_data.items()],
        class_="patient-summary"
    )

def create_decision_component(decision_data: Dict[str, Any]):
    """Simple decision component"""
    return Div(
        H3("Decision Recommendation"),
        P(f"Treatment: {decision_data.get('treatment', 'Pending')}"),
        P(f"Confidence: {decision_data.get('confidence', 0):.1%}"),
        class_="decision-component"
    )

def create_clinical_form():
    """Simple clinical data form"""
    return Form(
        Input(type="text", name="patient_id", placeholder="Patient ID", required=True),
        Select(
            Option("T1", value="T1"),
            Option("T2", value="T2"), 
            Option("T3", value="T3"),
            Option("T4", value="T4"),
            name="tumor_stage"
        ),
        Button("Submit", type="submit"),
        action="/api/v1/cases",
        method="post"
    )
