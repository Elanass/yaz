"""
AI Integration API
Provides AI-powered summarization and analysis capabilities
"""

import logging
import os
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import openai

from ...core.config.unified_config import get_settings
from ...core.services.logger import log_request, log_error

# Setup logging and OpenAI
logger = logging.getLogger(__name__)
settings = get_settings()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/ai", tags=["AI Services"])


class SummarizeRequest(BaseModel):
    """Request model for AI summarization"""

    case_id: str = Field(..., description="Unique case identifier")
    title: str = Field(..., description="Case title")
    description: str = Field(..., description="Case description")
    medical_data: Optional[Dict[str, Any]] = Field(
        None, description="Additional medical data"
    )
    patient_info: Optional[Dict[str, Any]] = Field(
        None, description="Patient information"
    )
    summary_type: str = Field("clinical", description="Type of summary to generate")
    max_length: int = Field(3, description="Maximum number of sentences in summary")


class SummarizeResponse(BaseModel):
    """Response model for AI summarization"""

    summary: str = Field(..., description="Generated AI summary")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    processing_time_ms: int = Field(..., description="Processing time in milliseconds")
    model_used: str = Field(..., description="AI model used for generation")
    case_id: str = Field(..., description="Case ID that was summarized")


class AnalysisRequest(BaseModel):
    """Request model for AI analysis"""

    data: Dict[str, Any] = Field(..., description="Data to analyze")
    analysis_type: str = Field("risk_assessment", description="Type of analysis")
    context: Optional[str] = Field(None, description="Additional context for analysis")


class AnalysisResponse(BaseModel):
    """Response model for AI analysis"""

    analysis: Dict[str, Any] = Field(..., description="Analysis results")
    recommendations: list[str] = Field(..., description="AI recommendations")
    confidence_score: float = Field(..., description="Confidence score (0-1)")
    model_used: str = Field(..., description="AI model used")


@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_case(request: SummarizeRequest) -> SummarizeResponse:
    """
    Generate AI-powered case summary using OpenAI GPT models

    This endpoint accepts case information and returns a concise, clinical summary
    suitable for medical professionals and stakeholders.
    """
    import time

    start_time = time.time()

    try:
        logger.info(f"🤖 Generating AI summary for case: {request.case_id}")

        # Validate OpenAI API key
        if not openai.api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.",
            )

        # Prepare the prompt based on available data
        prompt = _build_summarization_prompt(request)

        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI assistant. Provide concise, accurate clinical summaries. Focus on key medical findings, diagnoses, and treatment recommendations. Keep summaries to exactly 3 sentences unless specified otherwise.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.3,  # Lower temperature for more consistent medical summaries
                top_p=0.9,
            )

            # Extract the summary
            summary = response.choices[0].message.content.strip()

            # Calculate confidence score based on response metadata
            confidence_score = _calculate_confidence_score(response)

            processing_time = int((time.time() - start_time) * 1000)

            logger.info(
                f"✅ AI summary generated successfully for case {request.case_id} in {processing_time}ms"
            )

            return SummarizeResponse(
                summary=summary,
                confidence_score=confidence_score,
                processing_time_ms=processing_time,
                model_used=response.model,
                case_id=request.case_id,
            )

        except openai.error.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            raise HTTPException(
                status_code=429,
                detail="AI service temporarily unavailable due to rate limiting. Please try again later.",
            )
        except openai.error.AuthenticationError:
            logger.error("OpenAI API authentication failed")
            raise HTTPException(
                status_code=500,
                detail="AI service authentication failed. Please check API configuration.",
            )
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {str(openai_error)}")
            raise HTTPException(
                status_code=500, detail=f"AI service error: {str(openai_error)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        log_error(f"❌ Failed to generate AI summary for case {request.case_id}", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to generate summary: {str(e)}"
        )


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_data(request: AnalysisRequest) -> AnalysisResponse:
    """
    Perform AI-powered analysis on provided data

    Supports various analysis types including risk assessment,
    outcome prediction, and clinical decision support.
    """
    try:
        logger.info(f"🔍 Performing AI analysis: {request.analysis_type}")

        # Validate OpenAI API key
        if not openai.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")

        # Build analysis prompt
        prompt = _build_analysis_prompt(request)

        # Call OpenAI API for analysis
        response = openai.ChatCompletion.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[
                {
                    "role": "system",
                    "content": f"You are a medical AI analyst specializing in {request.analysis_type}. Provide structured analysis with specific recommendations. Format your response as JSON with 'analysis' and 'recommendations' fields.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.2,
        )

        # Parse the response
        content = response.choices[0].message.content.strip()

        # Try to parse as JSON, fallback to structured text
        try:
            import json

            parsed_content = json.loads(content)
            analysis = parsed_content.get("analysis", content)
            recommendations = parsed_content.get("recommendations", [])
        except json.JSONDecodeError:
            analysis = {"summary": content}
            recommendations = ["Review analysis with medical professional"]

        confidence_score = _calculate_confidence_score(response)

        logger.info(f"✅ AI analysis completed: {request.analysis_type}")

        return AnalysisResponse(
            analysis=analysis,
            recommendations=recommendations,
            confidence_score=confidence_score,
            model_used=response.model,
        )

    except Exception as e:
        log_error(f"❌ Failed to perform AI analysis: {request.analysis_type}", e)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


def _build_summarization_prompt(request: SummarizeRequest) -> str:
    """Build a comprehensive prompt for case summarization"""

    prompt_parts = [
        f"Please provide a {request.max_length}-sentence clinical summary of the following case:",
        f"\nCase ID: {request.case_id}",
        f"Title: {request.title}",
        f"Description: {request.description}",
    ]

    if request.patient_info:
        prompt_parts.append(f"Patient Information: {request.patient_info}")

    if request.medical_data:
        prompt_parts.append(f"Medical Data: {request.medical_data}")

    prompt_parts.extend(
        [
            f"\nSummary Type: {request.summary_type}",
            "\nFocus on:",
            "1. Key clinical findings and diagnoses",
            "2. Critical treatment decisions or recommendations",
            "3. Important outcomes or prognosis",
            f"\nProvide exactly {request.max_length} sentences in your summary.",
        ]
    )

    return "\n".join(prompt_parts)


def _build_analysis_prompt(request: AnalysisRequest) -> str:
    """Build a comprehensive prompt for data analysis"""

    prompt_parts = [
        f"Please perform a {request.analysis_type} analysis on the following data:",
        f"\nData: {request.data}",
    ]

    if request.context:
        prompt_parts.append(f"Context: {request.context}")

    prompt_parts.extend(
        [
            f"\nAnalysis Type: {request.analysis_type}",
            "\nProvide:",
            "1. Detailed analysis of the data",
            "2. Specific actionable recommendations",
            "3. Risk factors or considerations",
            "4. Confidence level in your analysis",
        ]
    )

    return "\n".join(prompt_parts)


def _calculate_confidence_score(openai_response) -> float:
    """
    Calculate confidence score based on OpenAI response metadata
    This is a simplified heuristic - in production you might use more sophisticated methods
    """
    try:
        # Use token usage and finish reason as confidence indicators
        usage = openai_response.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        finish_reason = openai_response.choices[0].get("finish_reason", "")

        # Base confidence
        confidence = 0.8

        # Adjust based on completion status
        if finish_reason == "stop":
            confidence += 0.1
        elif finish_reason == "length":
            confidence -= 0.1

        # Adjust based on response length (more tokens generally indicate more detailed response)
        if total_tokens > 100:
            confidence += 0.05
        elif total_tokens < 50:
            confidence -= 0.05

        # Clamp between 0 and 1
        return max(0.0, min(1.0, confidence))

    except Exception:
        # Default confidence score if metadata is unavailable
        return 0.75


# Health check endpoint for AI services
@router.get("/health")
async def ai_health_check() -> Dict[str, Any]:
    """Check AI service health and configuration"""

    health_status = {
        "status": "healthy",
        "openai_configured": bool(openai.api_key),
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "timestamp": "{{ new Date().toISOString() }}",
    }

    if not openai.api_key:
        health_status["status"] = "degraded"
        health_status["warning"] = "OpenAI API key not configured"

    return health_status
