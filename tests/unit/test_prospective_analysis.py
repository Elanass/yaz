import pytest
from features.analysis.prospective_analysis import ProspectiveAnalysis

@pytest.fixture
def prospective_analysis():
    return ProspectiveAnalysis()

def test_validate_data(prospective_analysis):
    valid_data = {"features": [1, 2, 3], "labels": [0, 1, 0]}
    invalid_data = {"features": [1, 2, 3]}  # Missing labels

    assert prospective_analysis.validate_data(valid_data) is True
    assert prospective_analysis.validate_data(invalid_data) is False

def test_analyze(prospective_analysis):
    data = {"features": [1, 2, 3], "labels": [0, 1, 0]}
    results = prospective_analysis.analyze(data)

    assert "random_forest" in results
