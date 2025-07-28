"""
Tests for the Clinical Decision Platform components
"""

import pytest
# from fasthtml.common import *  # removed dependency on fasthtml
from web.components.clinical_platform import (
    create_adaptive_decision_component,
    create_simulation_component,
    create_evidence_synthesis_component,
    create_clinical_dashboard
)

class TestClinicalPlatformComponents:
    """Test suite for the clinical platform components"""
    
    def test_adaptive_decision_component(self):
        """Test that the adaptive decision component renders correctly"""
        # Test data
        patient_data = {
            "patient_id": "P12345",
            "age": 65,
            "gender": "male",
            "tumor_stage": "T3N1M0",
            "tumor_location": "antrum",
            "histology": "intestinal"
        }
        
        # Create component
        component = create_adaptive_decision_component(patient_data)
        
        # Verify structure
        assert isinstance(component, Div)
        assert "Adaptive Decision Component" in str(component)
        assert "Patient Summary" in str(component)
        assert "Decision Analysis" in str(component)
        
        # Test with predictions
        predictions = {
            "recommendation": {
                "treatment": "FLOT + Gastrectomy",
                "confidence": 0.85,
                "explanation": "Based on patient's age, tumor stage, and histology, FLOT followed by gastrectomy is recommended."
            },
            "impact_analysis": {
                "surgery": {
                    "risk_level": "Moderate",
                    "adjusted_risk": 0.45,
                    "color": "yellow"
                },
                "flot": {
                    "risk_level": "Low",
                    "adjusted_risk": 0.25,
                    "color": "green"
                }
            }
        }
        
        component_with_predictions = create_adaptive_decision_component(patient_data, predictions)
        assert "FLOT + Gastrectomy" in str(component_with_predictions)
        assert "0.85" in str(component_with_predictions)
    
    def test_simulation_component(self):
        """Test that the simulation component renders correctly"""
        # Test with default config
        component = create_simulation_component()
        
        # Verify structure
        assert isinstance(component, Div)
        assert "Disease Progression Simulation" in str(component)
        assert "Number of steps:" in str(component)
        assert "Number of simulations:" in str(component)
        
        # Test with custom config
        config = {
            "steps": 10,
            "simulations": 5000,
            "include_confidence": False
        }
        
        custom_component = create_simulation_component(config)
        assert "value=10" in str(custom_component)
        assert "value=5000" in str(custom_component)
        
        # Test with results
        results = {
            "metrics": {
                "survival_rate": 0.72,
                "recurrence_rate": 0.28,
                "median_survival_months": 36.5
            }
        }
        
        component_with_results = create_simulation_component(config, results)
        assert "0.72" in str(component_with_results)
        assert "36.5" in str(component_with_results)
    
    def test_evidence_synthesis_component(self):
        """Test that the evidence synthesis component renders correctly"""
        # Test with default params
        component = create_evidence_synthesis_component()
        
        # Verify structure
        assert isinstance(component, Div)
        assert "Evidence Synthesis" in str(component)
        assert "Search clinical evidence:" in str(component)
        
        # Test with query
        query = "FLOT chemotherapy for stage III gastric cancer"
        query_component = create_evidence_synthesis_component(query)
        assert query in str(query_component)
        
        # Test with evidence items
        evidence_items = [
            {
                "source_type": "Clinical Trial",
                "title": "FLOT4 Trial Results",
                "description": "Perioperative FLOT improves survival compared to ECF/ECX regimen",
                "source": "Journal of Clinical Oncology",
                "url": "https://example.com/flot4",
                "year": 2019,
                "confidence": 0.92
            },
            {
                "source_type": "Meta-analysis",
                "title": "Comprehensive Analysis of Gastric Cancer Treatments",
                "description": "Systematic review of treatments for advanced gastric cancer",
                "source": "The Lancet Oncology",
                "url": "https://example.com/meta",
                "year": 2020,
                "confidence": 0.88
            }
        ]
        
        evidence_component = create_evidence_synthesis_component(query, evidence_items)
        assert "FLOT4 Trial Results" in str(evidence_component)
        assert "0.92" in str(evidence_component)
        assert "The Lancet Oncology" in str(evidence_component)
    
    def test_clinical_dashboard(self):
        """Test that the clinical dashboard renders correctly"""
        # Test data
        patient_data = {
            "patient_id": "P12345",
            "age": 65,
            "gender": "male",
            "tumor_stage": "T3N1M0"
        }
        
        # Test with default params
        component = create_clinical_dashboard(patient_data)
        
        # Verify structure
        assert isinstance(component, Div)
        assert "Clinical Dashboard" in str(component)
        assert "P12345" in str(component)
        assert "No metrics available for this patient" in str(component)
        
        # Test with metrics
        metrics = {
            "survival_probability": 0.78,
            "survival_trend": 0.05,
            "quality_of_life": 7.2,
            "qol_trend": -0.3,
            "recurrence_risk": 0.22,
            "recurrence_trend": -0.04
        }
        
        metrics_component = create_clinical_dashboard(patient_data, metrics)
        assert "78.0%" in str(metrics_component)
        assert "7.2/10" in str(metrics_component)
        assert "22.0%" in str(metrics_component)
