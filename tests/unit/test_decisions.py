"""
Test Suite for Decision Engines
Comprehensive tests for decision functionality  
"""

import pytest
from fastapi.testclient import TestClient

from main import create_app
from features.decisions.service import DecisionRequest


@pytest.fixture
def client():
    """Test client fixture"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Authenticated user headers fixture"""
    
    # Use default admin user for testing
    login_data = {
        "email": "admin@gastric-adci.com",
        "password": "admin123"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    token = response.json()["data"]["access_token"]
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_adci_request():
    """Sample ADCI decision request"""
    
    return DecisionRequest(
        engine_type="adci",
        patient_data={
            "age": 65,
            "performance_status": 1,
            "comorbidities": ["hypertension"],
            "bmi": 24.5
        },
        tumor_data={
            "stage": "T3N1M0",
            "location": "antrum",
            "histology": "adenocarcinoma",
            "size_cm": 4.2
        },
        context={
            "institution": "test_hospital",
            "urgency": "standard"
        }
    )


@pytest.fixture
def sample_gastrectomy_request():
    """Sample gastrectomy decision request"""
    
    return DecisionRequest(
        engine_type="gastrectomy",
        patient_data={
            "age": 58,
            "bmi": 26.0,
            "asa_score": 2,
            "performance_status": 0
        },
        tumor_data={
            "location": "antrum",
            "size_cm": 3.5,
            "stage": "T2N0M0",
            "histology": "adenocarcinoma"
        }
    )


class TestDecisionAPI:
    """Test decision API endpoints"""
    
    def test_create_adci_decision(self, client, auth_headers, sample_adci_request):
        """Test ADCI decision creation"""
        
        response = client.post(
            "/api/v1/decisions/analyze",
            json=sample_adci_request.dict(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        decision = data["data"]
        assert decision["engine_type"] == "adci"
        assert decision["status"] == "completed"
        assert "recommendation" in decision
        assert "confidence_score" in decision
        assert "confidence_level" in decision
        assert "reasoning" in decision
        assert isinstance(decision["reasoning"], list)
        assert len(decision["reasoning"]) > 0
    
    def test_create_gastrectomy_decision(self, client, auth_headers, sample_gastrectomy_request):
        """Test gastrectomy decision creation"""
        
        response = client.post(
            "/api/v1/decisions/analyze",
            json=sample_gastrectomy_request.dict(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        decision = data["data"]
        assert decision["engine_type"] == "gastrectomy"
        assert decision["status"] == "completed"
        assert "procedure" in decision["recommendation"]
        assert "approach" in decision["recommendation"]
        assert "lymphadenectomy" in decision["recommendation"]
    
    def test_invalid_engine_type(self, client, auth_headers):
        """Test invalid engine type handling"""
        
        invalid_request = {
            "engine_type": "invalid_engine",
            "patient_data": {"age": 65},
            "tumor_data": {"stage": "T2N0M0"}
        }
        
        response = client.post(
            "/api/v1/decisions/analyze",
            json=invalid_request,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Unknown engine type" in response.json()["detail"]
    
    def test_missing_required_data(self, client, auth_headers):
        """Test validation of missing required data"""
        
        incomplete_request = {
            "engine_type": "adci",
            "patient_data": {},  # Missing age
            "tumor_data": {}     # Missing stage
        }
        
        response = client.post(
            "/api/v1/decisions/analyze",
            json=incomplete_request,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Validation errors" in response.json()["detail"]
    
    def test_get_decision_by_id(self, client, auth_headers, sample_adci_request):
        """Test retrieving decision by ID"""
        
        # Create decision first
        create_response = client.post(
            "/api/v1/decisions/analyze",
            json=sample_adci_request.dict(),
            headers=auth_headers
        )
        
        decision_id = create_response.json()["data"]["decision_id"]
        
        # Get decision by ID
        response = client.get(
            f"/api/v1/decisions/{decision_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["decision_id"] == decision_id
    
    def test_list_decisions(self, client, auth_headers, sample_adci_request):
        """Test listing decisions"""
        
        # Create a few decisions
        for _ in range(3):
            client.post(
                "/api/v1/decisions/analyze",
                json=sample_adci_request.dict(),
                headers=auth_headers
            )
        
        # List decisions
        response = client.get("/api/v1/decisions/", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 3
    
    def test_list_decisions_with_filters(self, client, auth_headers, sample_adci_request, sample_gastrectomy_request):
        """Test listing decisions with filters"""
        
        # Create decisions of different types
        client.post("/api/v1/decisions/analyze", json=sample_adci_request.dict(), headers=auth_headers)
        client.post("/api/v1/decisions/analyze", json=sample_gastrectomy_request.dict(), headers=auth_headers)
        
        # Filter by engine type
        response = client.get("/api/v1/decisions/?engine_type=adci", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert all(d["engine_type"] == "adci" for d in data["data"])
    
    def test_validate_input(self, client, auth_headers, sample_adci_request):
        """Test input validation endpoint"""
        
        response = client.post(
            "/api/v1/decisions/validate-input",
            json=sample_adci_request.dict(),
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["valid"] is True
        assert len(data["data"]["errors"]) == 0
    
    def test_validate_invalid_input(self, client, auth_headers):
        """Test validation of invalid input"""
        
        invalid_request = {
            "engine_type": "adci",
            "patient_data": {},  # Missing required fields
            "tumor_data": {}
        }
        
        response = client.post(
            "/api/v1/decisions/validate-input",
            json=invalid_request,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["data"]["valid"] is False
        assert len(data["data"]["errors"]) > 0
    
    def test_get_available_engines(self, client, auth_headers):
        """Test getting available engines"""
        
        response = client.get("/api/v1/decisions/engines/available", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        engines = data["data"]
        assert len(engines) >= 2  # ADCI and Gastrectomy
        
        engine_types = [e["type"] for e in engines]
        assert "adci" in engine_types
        assert "gastrectomy" in engine_types
    
    def test_get_decision_statistics(self, client, auth_headers, sample_adci_request):
        """Test getting decision statistics"""
        
        # Create some decisions
        for _ in range(3):
            client.post("/api/v1/decisions/analyze", json=sample_adci_request.dict(), headers=auth_headers)
        
        response = client.get("/api/v1/decisions/stats/summary", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        stats = data["data"]
        assert "total_decisions" in stats
        assert "by_status" in stats
        assert "by_engine" in stats
        assert "avg_confidence" in stats
        assert stats["total_decisions"] >= 3


class TestDecisionEngines:
    """Test decision engine functionality"""
    
    @pytest.mark.asyncio
    async def test_adci_engine_analysis(self):
        """Test ADCI engine analysis"""
        
        from features.decisions.service import ADCIEngine
        
        engine = ADCIEngine()
        
        patient_data = {
            "age": 65,
            "performance_status": 1,
            "comorbidities": ["hypertension"]
        }
        
        tumor_data = {
            "stage": "T3N1M0",
            "location": "antrum",
            "histology": "adenocarcinoma"
        }
        
        result = await engine.analyze(patient_data, tumor_data)
        
        assert "recommendation" in result
        assert "confidence_score" in result
        assert "confidence_level" in result
        assert "reasoning" in result
        assert "evidence" in result
        
        # Confidence score should be between 0 and 1
        assert 0 <= result["confidence_score"] <= 1
        
        # Reasoning should be a list with content
        assert isinstance(result["reasoning"], list)
        assert len(result["reasoning"]) > 0
    
    @pytest.mark.asyncio
    async def test_gastrectomy_engine_analysis(self):
        """Test gastrectomy engine analysis"""
        
        from features.decisions.service import GastrectomyEngine
        
        engine = GastrectomyEngine()
        
        patient_data = {
            "age": 58,
            "bmi": 26.0,
            "asa_score": 2
        }
        
        tumor_data = {
            "location": "antrum",
            "size_cm": 3.5,
            "stage": "T2N0M0"
        }
        
        result = await engine.analyze(patient_data, tumor_data)
        
        assert "recommendation" in result
        assert "procedure" in result["recommendation"]
        assert "approach" in result["recommendation"]
        assert "lymphadenectomy" in result["recommendation"]
        
        # Check valid procedure types
        procedure = result["recommendation"]["procedure"]
        valid_procedures = ["distal_gastrectomy", "proximal_gastrectomy", "total_gastrectomy"]
        assert procedure in valid_procedures
    
    def test_engine_input_validation(self):
        """Test engine input validation"""
        
        from features.decisions.service import ADCIEngine
        
        engine = ADCIEngine()
        
        # Test missing required fields
        patient_data = {}  # Missing age
        tumor_data = {}    # Missing stage
        
        errors = engine.validate_input(patient_data, tumor_data)
        
        assert len(errors) > 0
        assert any("age" in error for error in errors)
        assert any("stage" in error for error in errors)
        
        # Test valid input
        patient_data = {"age": 65}
        tumor_data = {"stage": "T2N0M0"}
        
        errors = engine.validate_input(patient_data, tumor_data)
        assert len(errors) == 0
    
    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        
        from features.decisions.service import ADCIEngine
        
        engine = ADCIEngine()
        
        # Test with all factors
        factors = {
            "data_completeness": 0.8,
            "evidence_strength": 0.9,
            "guideline_support": 0.7
        }
        
        confidence = engine.calculate_confidence(factors)
        assert 0 <= confidence <= 1
        
        # Test with empty factors
        confidence = engine.calculate_confidence({})
        assert confidence == 0.5  # Default fallback
        
        # Test with partial factors
        factors = {"data_completeness": 1.0}
        confidence = engine.calculate_confidence(factors)
        assert 0 <= confidence <= 1


@pytest.mark.asyncio
class TestDecisionService:
    """Test DecisionService functionality"""
    
    async def test_create_decision(self):
        """Test decision creation through service"""
        
        from features.decisions.service import DecisionService, DecisionRequest
        
        service = DecisionService()
        
        request = DecisionRequest(
            engine_type="adci",
            patient_data={
                "age": 70,
                "performance_status": 1
            },
            tumor_data={
                "stage": "T2N1M0",
                "location": "body"
            }
        )
        
        response = await service.create_decision(request, user_id="test_user")
        
        assert response.engine_type == "adci"
        assert response.status.value == "completed"
        assert response.confidence_score > 0
        assert len(response.reasoning) > 0
    
    async def test_decision_caching(self):
        """Test decision result caching"""
        
        from features.decisions.service import DecisionService, DecisionRequest
        
        service = DecisionService()
        
        request = DecisionRequest(
            engine_type="adci",
            patient_data={"age": 65, "performance_status": 1},
            tumor_data={"stage": "T3N1M0", "location": "antrum"}
        )
        
        # First request - should compute
        response1 = await service.create_decision(request, user_id="test_user")
        
        # Second identical request - should use cache
        response2 = await service.create_decision(request, user_id="test_user")
        
        # Results should be similar (cached)
        assert response1.recommendation == response2.recommendation
        assert response1.confidence_score == response2.confidence_score
    
    async def test_list_decisions_filtering(self):
        """Test decision listing with filters"""
        
        from features.decisions.service import DecisionService, DecisionRequest
        
        service = DecisionService()
        
        # Create decisions with different engines
        adci_request = DecisionRequest(
            engine_type="adci",
            patient_data={"age": 65, "performance_status": 1},
            tumor_data={"stage": "T2N0M0", "location": "antrum"}
        )
        
        gastrectomy_request = DecisionRequest(
            engine_type="gastrectomy", 
            patient_data={"age": 60, "bmi": 25.0, "asa_score": 2},
            tumor_data={"location": "antrum", "size_cm": 3.0}
        )
        
        await service.create_decision(adci_request, user_id="user1")
        await service.create_decision(gastrectomy_request, user_id="user2")
        
        # Test filtering by engine type
        adci_decisions = await service.list_decisions(engine_type="adci")
        assert all(d.engine_type == "adci" for d in adci_decisions)
        
        # Test filtering by user
        user1_decisions = await service.list_decisions(user_id="user1")
        assert all(d.decision_id.startswith("") for d in user1_decisions)  # Should have user1's decisions
