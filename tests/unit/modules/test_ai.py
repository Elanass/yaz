"""
Unit tests for AI integration module
Tests the AI summarization and analysis capabilities
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi.testclient import TestClient

from surgify.api.v1.ai import (
    SummarizeRequest,
    SummarizeResponse,
    _build_summarization_prompt,
    _calculate_confidence_score,
    router,
)


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
