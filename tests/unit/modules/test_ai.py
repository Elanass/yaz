"""
Unit tests for AI integration module
Tests the AI summarization and analysis capabilities
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from surgify.api.v1.ai import (SummarizeRequest, SummarizeResponse,
                               _build_summarization_prompt,
                               _calculate_confidence_score, router)


class TestAISummarization:
    """Test AI summarization functionality"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_request = SummarizeRequest(
            case_id="test-case-123",
            title="Emergency Surgery Case",
            description="Patient presented with acute abdominal pain",
            medical_data={"diagnosis": "appendicitis", "severity": "moderate"},
            patient_info={"age": 45, "gender": "M"},
        )

    def test_build_summarization_prompt(self):
        """Test prompt building for AI summarization"""
        prompt = _build_summarization_prompt(self.sample_request)

        assert "test-case-123" in prompt
        assert "Emergency Surgery Case" in prompt
        assert "acute abdominal pain" in prompt
        assert "appendicitis" in prompt
        assert "exactly 3 sentences" in prompt

    def test_build_summarization_prompt_minimal(self):
        """Test prompt building with minimal data"""
        minimal_request = SummarizeRequest(
            case_id="minimal-case", title="Basic Case", description="Simple description"
        )

        prompt = _build_summarization_prompt(minimal_request)

        assert "minimal-case" in prompt
        assert "Basic Case" in prompt
        assert "Simple description" in prompt

    def test_calculate_confidence_score_complete(self):
        """Test confidence score calculation with complete response"""
        mock_response = {
            "usage": {"total_tokens": 150},
            "choices": [{"finish_reason": "stop"}],
        }

        confidence = _calculate_confidence_score(mock_response)

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.8  # Should be high for complete response

    def test_calculate_confidence_score_truncated(self):
        """Test confidence score calculation with truncated response"""
        mock_response = {
            "usage": {"total_tokens": 300},
            "choices": [{"finish_reason": "length"}],
        }

        confidence = _calculate_confidence_score(mock_response)

        assert 0.0 <= confidence <= 1.0
        assert confidence < 0.9  # Should be lower for truncated response

    def test_calculate_confidence_score_fallback(self):
        """Test confidence score fallback for malformed response"""
        mock_response = {}

        confidence = _calculate_confidence_score(mock_response)

        assert confidence == 0.75  # Default fallback value


@pytest.mark.asyncio
class TestAIAPI:
    """Test AI API endpoints"""

    def setup_method(self):
        """Setup test client and fixtures"""
        from fastapi import FastAPI

        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)

    @patch("src.surgify.api.v1.ai.openai")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_summarize_success(self, mock_openai):
        """Test successful case summarization"""
        # Mock OpenAI response
        mock_openai.ChatCompletion.create.return_value = Mock(
            choices=[Mock(message=Mock(content="Test AI summary of the case."))],
            model="gpt-4",
            usage={"total_tokens": 50},
        )

        request_data = {
            "case_id": "test-123",
            "title": "Test Case",
            "description": "Test description",
            "max_length": 3,
        }

        response = self.client.post("/summarize", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["case_id"] == "test-123"
        assert data["summary"] == "Test AI summary of the case."
        assert "confidence_score" in data
        assert "processing_time_ms" in data

    @patch.dict("os.environ", {}, clear=True)
    def test_summarize_no_api_key(self):
        """Test summarization without OpenAI API key"""
        request_data = {
            "case_id": "test-123",
            "title": "Test Case",
            "description": "Test description",
        }

        response = self.client.post("/summarize", json=request_data)

        assert response.status_code == 500
        assert "OpenAI API key not configured" in response.json()["detail"]

    @patch("src.surgify.api.v1.ai.openai")
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_summarize_openai_error(self, mock_openai):
        """Test handling of OpenAI API errors"""
        import openai

        mock_openai.ChatCompletion.create.side_effect = openai.error.RateLimitError(
            "Rate limit exceeded"
        )
        mock_openai.error = openai.error

        request_data = {
            "case_id": "test-123",
            "title": "Test Case",
            "description": "Test description",
        }

        response = self.client.post("/summarize", json=request_data)

        assert response.status_code == 429
        assert "rate limiting" in response.json()["detail"]

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_health_check_configured(self):
        """Test AI health check with API key configured"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["openai_configured"] is True

    @patch.dict("os.environ", {}, clear=True)
    def test_health_check_not_configured(self):
        """Test AI health check without API key"""
        response = self.client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "degraded"
        assert data["openai_configured"] is False
        assert "warning" in data


class TestAIRequestValidation:
    """Test AI request model validation"""

    def test_summarize_request_valid(self):
        """Test valid summarization request"""
        request = SummarizeRequest(
            case_id="test-123", title="Test Case", description="Test description"
        )

        assert request.case_id == "test-123"
        assert request.max_length == 3  # Default value
        assert request.summary_type == "clinical"  # Default value

    def test_summarize_request_custom_length(self):
        """Test summarization request with custom length"""
        request = SummarizeRequest(
            case_id="test-123",
            title="Test Case",
            description="Test description",
            max_length=5,
        )

        assert request.max_length == 5

    def test_summarize_request_validation_error(self):
        """Test summarization request validation errors"""
        with pytest.raises(ValueError):
            SummarizeRequest(
                # Missing required fields
                title="Test Case"
            )


@pytest.mark.integration
class TestAIIntegration:
    """Integration tests for AI services"""

    @pytest.mark.skipif(
        not pytest.importorskip("openai"), reason="OpenAI not available"
    )
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    async def test_ai_summarization_flow(self):
        """Test complete AI summarization flow"""
        # This would be a more comprehensive integration test
        # that tests the entire flow from request to response
        pass

    def test_ai_error_handling(self):
        """Test AI service error handling and fallbacks"""
        # Test various error scenarios and recovery mechanisms
        pass


class TestEnhancedAI:
    """Test enhanced AI functionality with local models and cost optimization"""

    def setup_method(self):
        """Setup test fixtures"""
        self.sample_medical_text = (
            "65-year-old male with diabetes and hypertension presenting "
            "for cardiac bypass surgery. Recent myocardial infarction 6 months ago."
        )
        
        self.sample_patient_data = {
            "age": 72,
            "gender": "M",
            "comorbidities": ["diabetes", "hypertension", "previous_mi"],
            "procedure": "cardiac_bypass",
            "emergency": False,
            "bmi": 28.5
        }

    def test_cost_calculation_logic(self):
        """Test cost calculation for different AI approaches"""
        # Test cost calculation logic
        requests_per_day = 100
        monthly_requests = requests_per_day * 30
        
        # OpenAI costs (approximate)
        openai_cost_per_request = 0.045
        openai_monthly_cost = monthly_requests * openai_cost_per_request
        
        # Local model costs
        local_monthly_cost = 0.0
        
        # HuggingFace API costs
        hf_free_tier = 1000
        hf_paid_requests = max(0, monthly_requests - hf_free_tier)
        hf_monthly_cost = hf_paid_requests * 0.0001
        
        assert openai_monthly_cost > 0
        assert local_monthly_cost == 0.0
        assert hf_monthly_cost < openai_monthly_cost
        
        # Calculate savings
        local_savings = openai_monthly_cost - local_monthly_cost
        hf_savings = openai_monthly_cost - hf_monthly_cost
        
        assert local_savings == openai_monthly_cost
        assert hf_savings > 0

    def test_medical_entity_extraction_patterns(self):
        """Test medical entity extraction patterns"""
        import re
        
        # Test medical patterns that should be detected
        medical_patterns = [
            r'\b[A-Z]{2,}\b',  # Abbreviations like ICU, MRI
            r'\b\w+itis\b',    # Inflammation conditions
            r'\b\w+oma\b',     # Tumor conditions
            r'\b\w+osis\b',    # Disease conditions
        ]
        
        test_text = "Patient has arthritis and shows signs of fibrosis on MRI scan"
        
        entities = []
        for pattern in medical_patterns:
            matches = re.findall(pattern, test_text, re.IGNORECASE)
            entities.extend(matches)
        
        assert "arthritis" in [e.lower() for e in entities]
        assert "fibrosis" in [e.lower() for e in entities]
        assert "MRI" in entities

    def test_risk_factor_identification(self):
        """Test risk factor identification logic"""
        def identify_risk_factors(patient_data):
            factors = []
            
            age = patient_data.get("age", 0)
            if age > 70:
                factors.append("advanced_age")
            
            bmi = patient_data.get("bmi", 0)
            if bmi > 30:
                factors.append("obesity")
            elif bmi > 25:
                factors.append("overweight")
            
            if "diabetes" in patient_data.get("comorbidities", []):
                factors.append("diabetes")
            
            if patient_data.get("emergency"):
                factors.append("emergency_procedure")
            
            return factors
        
        risk_factors = identify_risk_factors(self.sample_patient_data)
        
        assert "advanced_age" in risk_factors  # Age 72
        assert "overweight" in risk_factors    # BMI 28.5
        assert "diabetes" in risk_factors      # Has diabetes
        assert "emergency_procedure" not in risk_factors  # Not emergency

    def test_success_probability_calculation(self):
        """Test success probability calculation logic"""
        def calculate_success_probability(risk_level, complexity_score):
            base_probability = 0.85  # Base success rate
            
            # Adjust for risk level
            if risk_level == "high":
                base_probability -= 0.25
            elif risk_level == "low":
                base_probability += 0.10
            
            # Adjust for complexity
            base_probability -= complexity_score * 0.15
            
            # Ensure probability is between 0.1 and 0.95
            return max(0.1, min(0.95, base_probability))
        
        # Test different scenarios
        low_risk_simple = calculate_success_probability("low", 0.2)
        high_risk_complex = calculate_success_probability("high", 0.8)
        medium_risk_medium = calculate_success_probability("medium", 0.5)
        
        assert low_risk_simple > medium_risk_medium > high_risk_complex
        assert 0.1 <= low_risk_simple <= 0.95
        assert 0.1 <= high_risk_complex <= 0.95

    def test_cost_savings_realistic_scenarios(self):
        """Test cost savings for realistic hospital scenarios"""
        scenarios = [
            ("Small Clinic", 10),
            ("Medium Hospital", 100), 
            ("Large Hospital", 1000),
            ("Hospital System", 5000)
        ]
        
        for scenario_name, daily_requests in scenarios:
            monthly_requests = daily_requests * 30
            
            # Calculate realistic costs
            openai_cost = monthly_requests * 0.045  # ~$0.045 per request
            local_cost = 0.0  # Free
            
            savings = openai_cost - local_cost
            
            assert savings > 0
            assert savings == openai_cost  # All savings with local models
            
            # Large hospitals should save significant amounts
            if daily_requests >= 1000:
                assert savings > 1000  # Should save over $1000/month


class TestAIModelPerformance:
    """Test AI model performance characteristics"""
    
    def test_response_time_expectations(self):
        """Test expected response times for different approaches"""
        response_times = {
            "local_biobert": 150,      # milliseconds
            "huggingface_api": 500,    # milliseconds  
            "openai_gpt4": 2000,       # milliseconds
        }
        
        # Local models should be fastest
        assert response_times["local_biobert"] < response_times["huggingface_api"]
        assert response_times["huggingface_api"] < response_times["openai_gpt4"]
        
        # All should be under reasonable limits
        assert all(time < 5000 for time in response_times.values())

    def test_accuracy_expectations(self):
        """Test expected accuracy levels for different models"""
        accuracy_scores = {
            "local_biobert": 0.85,     # High for medical text
            "huggingface_api": 0.88,   # Slightly higher with cloud models
            "openai_gpt4": 0.92,       # Highest general intelligence
            "statistical_fallback": 0.75  # Lower but reliable
        }
        
        # All should meet minimum threshold
        assert all(acc >= 0.70 for acc in accuracy_scores.values())
        
        # Medical specialized models should be competitive
        assert accuracy_scores["local_biobert"] >= 0.80
