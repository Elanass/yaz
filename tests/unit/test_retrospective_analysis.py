import pytest
from features.analysis.retrospective_analysis import RetrospectiveAnalysis

@pytest.fixture
def retrospective_analysis():
    return RetrospectiveAnalysis()

def test_validate_data(retrospective_analysis):
    valid_data = {"patient_id": 1, "outcome": "survived", "time_to_event": 12}
    invalid_data = {"patient_id": 1, "outcome": "survived"}  # Missing time_to_event

    assert retrospective_analysis.validate_data(valid_data) is True
    assert retrospective_analysis.validate_data(invalid_data) is False

def test_analyze(retrospective_analysis):
    data = {"patient_id": 1, "outcome": "survived", "time_to_event": 12}
    results = retrospective_analysis.analyze(data)

    assert "cox_regression" in results
    assert "logistic_regression" in results
