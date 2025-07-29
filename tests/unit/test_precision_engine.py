import pytest
from features.decisions.precision_engine import PrecisionEngine

@pytest.fixture
def sample_patient():
    return {
        "age": 75,
        "comorbidities": ["hypertension", "diabetes"],
        "tumor_stage": "T3N1M0",
        "tumor_location": "proximal",
        "performance_status": 2
    }

def test_precision_engine_mcda_and_confidence(sample_patient):
    engine = PrecisionEngine()
    insights = engine.analyze([sample_patient])
    assert isinstance(insights, list) and len(insights) == 1

    surgery = insights[0]['surgery']
    flot = insights[0]['flot']

    # Check MCDA score presence and bounds
    for option in (surgery, flot):
        assert 'mcda_score' in option
        assert 0.0 <= option['mcda_score'] <= 1.0
        assert 'confidence_interval' in option
        ci = option['confidence_interval']
        assert isinstance(ci, list) and len(ci) == 2
        assert 0.0 <= ci[0] <= ci[1] <= 1.0

    # Check that a recommendation key exists
    assert 'recommended' in surgery and isinstance(surgery['recommended'], bool)
    assert 'recommended' in flot and isinstance(flot['recommended'], bool)
