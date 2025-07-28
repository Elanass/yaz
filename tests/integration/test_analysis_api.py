"""
Integration tests for analysis API endpoints
"""

import pytest
from fastapi.testclient import TestClient
import io
import pandas as pd
import numpy as np

from app import create_app


@pytest.fixture
def client():
    """Create a test client"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def mock_csv_file():
    """Create a mock CSV file for testing"""
    # Generate sample data
    np.random.seed(42)
    n = 50
    
    # Time to event data
    time = np.random.exponential(scale=30, size=n)
    
    # Censoring indicator (1=event, 0=censored)
    event = np.random.binomial(n=1, p=0.7, size=n)
    
    # Outcome
    outcome = np.random.binomial(n=1, p=0.6, size=n)
    
    # Covariates
    age = np.random.normal(loc=65, scale=10, size=n)
    stage = np.random.choice([1, 2, 3, 4], size=n, p=[0.2, 0.3, 0.3, 0.2])
    treatment = np.random.choice([0, 1], size=n, p=[0.5, 0.5])
    
    # Create DataFrame
    df = pd.DataFrame({
        'time': time,
        'event': event,
        'outcome': outcome,
        'age': age,
        'stage': stage,
        'treatment': treatment
    })
    
    # Convert to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    
    return csv_buffer.getvalue()


@pytest.fixture
def auth_headers():
    """Mock authentication headers"""
    # In a real test, this would generate or retrieve a valid token
    return {"Authorization": "Bearer test_token"}


class TestRetrospectiveAnalysisAPI:
    """Tests for retrospective analysis API endpoints"""
    
    def test_cox_regression(self, client, mock_csv_file, auth_headers, monkeypatch):
        """Test Cox regression endpoint"""
        # Mock authentication and permissions
        monkeypatch.setattr("features.auth.service.require_role", lambda *args, **kwargs: lambda: {"id": "test_user"})
        
        # Prepare file for upload
        files = {
            "file": ("test.csv", mock_csv_file, "text/csv")
        }
        
        # Send request
        response = client.post(
            "/api/v1/analysis/retrospective/cox",
            files=files,
            data={
                "time_column": "time",
                "event_column": "event",
                "covariates": "age,stage,treatment"
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "summary" in data
        assert "concordance" in data
        assert "interpretation" in data
    
    def test_logistic_regression(self, client, mock_csv_file, auth_headers, monkeypatch):
        """Test logistic regression endpoint"""
        # Mock authentication and permissions
        monkeypatch.setattr("features.auth.service.require_role", lambda *args, **kwargs: lambda: {"id": "test_user"})
        
        # Prepare file for upload
        files = {
            "file": ("test.csv", mock_csv_file, "text/csv")
        }
        
        # Send request
        response = client.post(
            "/api/v1/analysis/retrospective/logistic",
            files=files,
            data={
                "outcome_column": "outcome",
                "covariates": "age,stage,treatment"
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "summary" in data
        assert "auc" in data
        assert "accuracy" in data
        assert "interpretation" in data


class TestProspectiveAnalysisAPI:
    """Tests for prospective analysis API endpoints"""
    
    def test_random_forest(self, client, mock_csv_file, auth_headers, monkeypatch):
        """Test random forest endpoint"""
        # Mock authentication and permissions
        monkeypatch.setattr("features.auth.service.require_role", lambda *args, **kwargs: lambda: {"id": "test_user"})
        
        # Prepare file for upload
        files = {
            "file": ("test.csv", mock_csv_file, "text/csv")
        }
        
        # Send request
        response = client.post(
            "/api/v1/analysis/prospective/random-forest",
            files=files,
            data={
                "outcome_column": "outcome",
                "feature_columns": "age,stage,treatment",
                "n_estimators": 100,
                "test_size": 0.2
            },
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "metrics" in data
        assert "feature_importance" in data
        assert "interpretation" in data
    
    def test_predict(self, client, auth_headers, monkeypatch):
        """Test prediction endpoint"""
        # Mock authentication and permissions
        monkeypatch.setattr("features.auth.service.require_role", lambda *args, **kwargs: lambda: {"id": "test_user"})
        
        # Prepare patient data
        patient_data = {
            "id": "P12345",
            "age": 67,
            "tumor_stage": "T2N0M0",
            "comorbidities": "hypertension,diabetes",
            "performance_status": 1
        }
        
        # Send request
        response = client.post(
            "/api/v1/analysis/prospective/predict",
            json={"patient_data": patient_data, "model_type": "random_forest"},
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "prediction" in data
        assert "confidence" in data
        assert "recommendations" in data
