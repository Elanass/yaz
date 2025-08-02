from fastapi.testclient import TestClient
# Ensure project root is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from main import app  # import app from main.py

client = TestClient(app)

def test_health_endpoint():
    """Integration test for the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"
    # Ensure version and environment fields exist
    assert "version" in data
    assert "environment" in data
    assert "database_connected" in data
    assert "api_available" in data
