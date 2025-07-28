import pytest
from fastapi.testclient import TestClient
from api.v1.medical_consolidated import app

client = TestClient(app)

def test_adci_predict_endpoint():
    valid_data = {"age": 45, "diagnosis": "Gastric Cancer", "lab_results": {"CEA": 2.5}}
    invalid_data = {"age": 45, "diagnosis": "Gastric Cancer"}  # Missing lab_results

    # Test valid input
    response = client.post("/adci/predict", json=valid_data)
    assert response.status_code == 200
    assert "confidence_score" in response.json()
    assert "recommendation" in response.json()

    # Test invalid input
    response = client.post("/adci/predict", json=invalid_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid input data"
