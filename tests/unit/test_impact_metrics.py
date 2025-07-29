"""
Unit tests for the Impact Metrics Analyzer
Tests survival curves, treatment effectiveness, QoL, and cost-effectiveness analytics
"""

import pytest
import numpy as np
from features.analysis.impact_metrics import ImpactMetricsAnalyzer


@pytest.fixture
def sample_cohort_data():
    """Sample cohort data for survival analysis"""
    return [
        {"time_to_event": 12, "event": 0},  # Censored at 12 months
        {"time_to_event": 18, "event": 1},  # Event at 18 months
        {"time_to_event": 24, "event": 0},  # Censored at 24 months
        {"time_to_event": 6, "event": 1},   # Event at 6 months
        {"time_to_event": 36, "event": 1},  # Event at 36 months
        {"time_to_event": 30, "event": 0},  # Censored at 30 months
        {"time_to_event": 24, "event": 1},  # Event at 24 months
        {"time_to_event": 15, "event": 1},  # Event at 15 months
        {"time_to_event": 9, "event": 0},   # Censored at 9 months
        {"time_to_event": 42, "event": 0},  # Censored at 42 months
    ]


@pytest.fixture
def sample_pre_post_data():
    """Sample pre/post treatment data for effectiveness analysis"""
    return [
        {"pre_score": 75, "post_score": 85, "response": True},
        {"pre_score": 60, "post_score": 80, "response": True},
        {"pre_score": 45, "post_score": 50, "response": False},
        {"pre_score": 80, "post_score": 90, "response": True},
        {"pre_score": 70, "post_score": 65, "response": False},
        {"pre_score": 50, "post_score": 75, "response": True},
        {"pre_score": 65, "post_score": 85, "response": True},
    ]


@pytest.fixture
def sample_qol_surveys():
    """Sample quality of life survey data"""
    return [
        {"score": 85, "functional_status": "good", "patient_id": "P001"},
        {"score": 72, "functional_status": "moderate", "patient_id": "P002"},
        {"score": 65, "functional_status": "moderate", "patient_id": "P003"},
        {"score": 90, "functional_status": "excellent", "patient_id": "P004"},
        {"score": 78, "functional_status": "good", "patient_id": "P005"},
    ]


@pytest.fixture
def sample_resource_data():
    """Sample resource and cost data"""
    return {
        "cost": 25000.0,
        "benefit": 1.5,  # QALY gained
        "intervention": "FLOT",
        "comparator": "Surgery alone"
    }


def test_generate_survival_curves(sample_cohort_data):
    """Test generation of Kaplan-Meier survival curves"""
    analyzer = ImpactMetricsAnalyzer()
    
    # Generate survival curves
    survival = analyzer.generate_survival_curves(sample_cohort_data)
    
    # Check structure
    assert "timeline" in survival
    assert "survival_probabilities" in survival
    
    # Check data types
    assert isinstance(survival["timeline"], list)
    assert isinstance(survival["survival_probabilities"], list)
    
    # Check lengths match
    assert len(survival["timeline"]) == len(survival["survival_probabilities"])
    
    # Check survival probabilities are within valid range
    assert all(0.0 <= prob <= 1.0 for prob in survival["survival_probabilities"])
    
    # Verify survival probabilities are monotonically decreasing
    for i in range(1, len(survival["survival_probabilities"])):
        assert survival["survival_probabilities"][i] <= survival["survival_probabilities"][i-1]


def test_calculate_treatment_effectiveness(sample_pre_post_data):
    """Test calculation of treatment effectiveness metrics"""
    analyzer = ImpactMetricsAnalyzer()
    
    # Calculate effectiveness
    effectiveness = analyzer.calculate_treatment_effectiveness(sample_pre_post_data)
    
    # Check structure
    assert "response_rate" in effectiveness
    assert "responders" in effectiveness
    assert "total" in effectiveness
    
    # Check values
    assert effectiveness["total"] == len(sample_pre_post_data)
    assert effectiveness["responders"] == 5  # Count of items with response=True
    assert effectiveness["response_rate"] == round(5 / 7, 3)  # 5 out of 7 responded
    
    # Test empty data handling
    empty_effectiveness = analyzer.calculate_treatment_effectiveness([])
    assert empty_effectiveness["response_rate"] == 0.0
    assert empty_effectiveness["responders"] == 0
    assert empty_effectiveness["total"] == 0


def test_analyze_quality_of_life_impact(sample_qol_surveys):
    """Test analysis of quality of life metrics"""
    analyzer = ImpactMetricsAnalyzer()
    
    # Analyze QoL
    qol_impact = analyzer.analyze_quality_of_life_impact(sample_qol_surveys)
    
    # Check structure
    assert "average_qol_score" in qol_impact
    assert "count" in qol_impact
    
    # Check values
    assert qol_impact["count"] == len(sample_qol_surveys)
    
    # Calculate expected average
    expected_avg = sum(survey["score"] for survey in sample_qol_surveys) / len(sample_qol_surveys)
    assert qol_impact["average_qol_score"] == round(expected_avg, 3)
    
    # Test empty data handling
    empty_qol = analyzer.analyze_quality_of_life_impact([])
    assert empty_qol["average_qol_score"] == 0.0
    assert empty_qol["count"] == 0


def test_generate_cost_effectiveness_analysis(sample_resource_data):
    """Test generation of cost-effectiveness analysis"""
    analyzer = ImpactMetricsAnalyzer()
    
    # Generate cost-effectiveness analysis
    cea = analyzer.generate_cost_effectiveness_analysis(sample_resource_data)
    
    # Check structure
    assert "cost" in cea
    assert "benefit" in cea
    assert "cost_effectiveness_ratio" in cea
    
    # Check values
    assert cea["cost"] == sample_resource_data["cost"]
    assert cea["benefit"] == sample_resource_data["benefit"]
    
    # Calculate expected ICER
    expected_icer = sample_resource_data["cost"] / sample_resource_data["benefit"]
    assert cea["cost_effectiveness_ratio"] == round(expected_icer, 3)
    
    # Test zero benefit handling
    zero_benefit = analyzer.generate_cost_effectiveness_analysis({
        "cost": 10000.0,
        "benefit": 0.0
    })
    assert zero_benefit["cost_effectiveness_ratio"] is None


def test_analyze_surgical_outcomes(sample_cohort_data, sample_pre_post_data):
    """Test comprehensive surgical outcomes analysis"""
    analyzer = ImpactMetricsAnalyzer()
    
    # Create test patient data
    patient_data = {
        "cohort": sample_cohort_data,
        "pre_post_data": sample_pre_post_data
    }
    
    # Analyze surgical outcomes
    outcomes = analyzer.analyze_surgical_outcomes(patient_data, "gastrectomy")
    
    # Check structure
    assert "procedure_type" in outcomes
    assert "survival_curve" in outcomes
    assert "effectiveness" in outcomes
    
    # Check procedure type
    assert outcomes["procedure_type"] == "gastrectomy"
    
    # Check survival curve structure
    assert "timeline" in outcomes["survival_curve"]
    assert "survival_probabilities" in outcomes["survival_curve"]
    
    # Check effectiveness structure
    assert "response_rate" in outcomes["effectiveness"]
    assert "responders" in outcomes["effectiveness"]
    assert "total" in outcomes["effectiveness"]
