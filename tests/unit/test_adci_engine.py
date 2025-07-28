import pytest
from features.decisions.adci_engine import ADCIEngine

@pytest.fixture
def adci_engine():
    return ADCIEngine()

def test_validate_input(adci_engine):
    valid_data = {"age": 45, "diagnosis": "Gastric Cancer", "lab_results": {"CEA": 2.5}}
    invalid_data = {"age": 45, "diagnosis": "Gastric Cancer"}  # Missing lab_results

    assert adci_engine.validate_input(valid_data) is True
    assert adci_engine.validate_input(invalid_data) is False

def test_predict(adci_engine):
    patient_data = {"age": 45, "diagnosis": "Gastric Cancer", "lab_results": {"CEA": 2.5}}
    prediction = adci_engine.predict(patient_data)

    assert "confidence_score" in prediction
    assert "recommendation" in prediction
