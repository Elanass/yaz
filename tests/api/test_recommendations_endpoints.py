import pytest
from fastapi.testclient import TestClient

from surgify.main import app

client = TestClient(app)


class TestRecommendationsEndpoints:
    def test_assess_risk(self):
        """Test risk assessment endpoint."""
        patient_data = {
            "age": 45,
            "medical_history": ["diabetes", "hypertension"],
            "surgery_type": "appendectomy",
        }

        response = client.post(
            "/api/v1/recommendations/recommendations/risk", json=patient_data
        )
        assert response.status_code == 200

        risk_score = response.json()
        assert isinstance(risk_score, float)
        assert 0 <= risk_score <= 1

    def test_get_recommendations(self):
        """Test recommendations endpoint."""
        patient_data = {
            "age": 35,
            "medical_history": [],
            "surgery_type": "cholecystectomy",
        }

        response = client.post(
            "/api/v1/recommendations/recommendations", json=patient_data
        )
        assert response.status_code == 200

        recommendations = response.json()
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    def test_predict_outcome(self):
        """Test outcome prediction endpoint."""
        patient_data = {
            "age": 55,
            "medical_history": ["diabetes"],
            "surgery_type": "hernia_repair",
        }

        response = client.post(
            "/api/v1/recommendations/recommendations/outcome", json=patient_data
        )
        assert response.status_code == 200

        outcome = response.json()
        assert "success_probability" in outcome
        assert "complication_probability" in outcome
        assert isinstance(outcome["success_probability"], float)
        assert isinstance(outcome["complication_probability"], float)

    def test_generate_alerts(self):
        """Test alerts generation endpoint."""
        patient_data = {
            "age": 70,
            "medical_history": ["heart_disease", "diabetes"],
            "surgery_type": "major_surgery",
        }

        response = client.post(
            "/api/v1/recommendations/recommendations/alerts", json=patient_data
        )
        assert response.status_code == 200

        alerts = response.json()
        assert isinstance(alerts, list)
