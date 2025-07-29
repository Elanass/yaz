"""
Unit tests for the Impact Metrics Analyzer component
"""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock

# Mock the lifelines module
class MockKaplanMeierFitter:
    def __init__(self):
        self.survival_function_ = MagicMock()
        self.survival_function_.index.tolist.return_value = [0, 6, 12, 18, 24, 30, 36]
        self.survival_function_['KM_estimate'].tolist.return_value = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4]
    
    def fit(self, durations, events):
        return self

# Apply the mock
lifelines_mock = MagicMock()
lifelines_mock.KaplanMeierFitter = MockKaplanMeierFitter
patch('features.analysis.impact_metrics.KaplanMeierFitter', MockKaplanMeierFitter).start()


@pytest.fixture
def impact_analyzer():
    """Create an impact analyzer instance for testing"""
    from features.analysis.impact_metrics import ImpactMetricsAnalyzer
    return ImpactMetricsAnalyzer()


@pytest.fixture
def sample_cohort_data():
    """Sample cohort data for survival analysis"""
    return [
        {"time_to_event": 12, "event": 0},  # Censored at 12 months
        {"time_to_event": 18, "event": 1},  # Event at 18 months
        {"time_to_event": 24, "event": 0},  # Censored at 24 months
    ]


@pytest.fixture
def sample_pre_post_data():
    """Sample pre/post treatment data for effectiveness analysis"""
    return [
        {"pre_score": 75, "post_score": 85, "response": True},
        {"pre_score": 60, "post_score": 80, "response": True},
        {"pre_score": 45, "post_score": 50, "response": False},
        {"pre_score": 80, "post_score": 90, "response": True},
    ]


@pytest.fixture
def sample_qol_surveys():
    """Sample quality of life survey data"""
    return [
        {"score": 85, "functional_status": "good", "patient_id": "P001"},
        {"score": 72, "functional_status": "moderate", "patient_id": "P002"},
        {"score": 65, "functional_status": "moderate", "patient_id": "P003"},
    ]


@pytest.fixture
def sample_resource_data():
    """Sample resource and cost data"""
    return {
        "cost": 25000.0,
        "benefit": 1.5,  # QALY gained
    }


def test_calculate_treatment_effectiveness(impact_analyzer, sample_pre_post_data):
    """Test calculation of treatment effectiveness metrics"""
    # Calculate effectiveness
    effectiveness = impact_analyzer.calculate_treatment_effectiveness(sample_pre_post_data)
    
    # Check structure
    assert "response_rate" in effectiveness
    assert "responders" in effectiveness
    assert "total" in effectiveness
    
    # Check values
    assert effectiveness["total"] == len(sample_pre_post_data)
    assert effectiveness["responders"] == 3  # Count of items with response=True
    assert effectiveness["response_rate"] == 0.75  # 3 out of 4 responded


def test_analyze_quality_of_life_impact(impact_analyzer, sample_qol_surveys):
    """Test analysis of quality of life metrics"""
    # Analyze QoL
    qol_impact = impact_analyzer.analyze_quality_of_life_impact(sample_qol_surveys)
    
    # Check structure
    assert "average_qol_score" in qol_impact
    assert "count" in qol_impact
    
    # Check values
    assert qol_impact["count"] == len(sample_qol_surveys)
    
    # Calculate expected average
    expected_avg = sum(survey["score"] for survey in sample_qol_surveys) / len(sample_qol_surveys)
    assert qol_impact["average_qol_score"] == round(expected_avg, 3)


def test_generate_cost_effectiveness_analysis(impact_analyzer, sample_resource_data):
    """Test generation of cost-effectiveness analysis"""
    # Generate cost-effectiveness analysis
    cea = impact_analyzer.generate_cost_effectiveness_analysis(sample_resource_data)
    
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
