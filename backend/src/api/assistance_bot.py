from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from ..core.security import get_current_user
from ..services.content_generator_service import get_clinical_content
import logging

# Define a request model for better validation
class BotRequest(BaseModel):
    question: str
    context: Optional[List[str]] = None
    specialty: Optional[str] = None
    user_role: Optional[str] = None

# Define a response model
class BotResponse(BaseModel):
    question: str
    answer: str
    context: List[str] = []
    sources: List[Dict[str, Any]] = []
    confidence: float = 0.0
    follow_up_suggestions: List[str] = []

router = APIRouter(prefix="/bot", tags=["assistance_bot"])

logger = logging.getLogger("assistance_bot")

@router.post("/ask", response_model=BotResponse)
async def ask_bot(
    request: BotRequest = Body(...),
    current_user = Depends(get_current_user)
):
    """
    Handle user queries and provide clinical assistance.
    
    This endpoint supports:
    - Context-aware responses based on previous conversation
    - Role-based answers (different for surgeons vs nurses)
    - Evidence-based responses with source citations
    - Follow-up question suggestions
    """
    try:
        logger.info(f"User {current_user.username} asked: {request.question}")
        
        # Get the user's role from their profile
        user_role = request.user_role or getattr(current_user, "role", "clinician")
        
        # Get tailored clinical content
        content = await get_clinical_content(
            question=request.question,
            context=request.context or [],
            specialty=request.specialty or "gastric-oncology",
            user_role=user_role
        )
        
        # Generate follow-up suggestions based on the context
        follow_ups = generate_follow_up_suggestions(request.question, content["answer"])
        
        response = BotResponse(
            question=request.question,
            answer=content["answer"],
            context=request.context or [],
            sources=content.get("sources", []),
            confidence=content.get("confidence", 0.95),
            follow_up_suggestions=follow_ups
        )
        
        logger.info(f"Response provided with confidence: {response.confidence}")
        return response
    except Exception as e:
        logger.error(f"Failed to process question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process the question: {str(e)}")

def generate_follow_up_suggestions(question: str, answer: str) -> List[str]:
    """Generate contextually relevant follow-up questions."""
    # This is a simple implementation
    # In a real system, this would use NLP to generate relevant follow-ups
    
    if "protocol" in question.lower() or "protocol" in answer.lower():
        return [
            "What are the compliance requirements for this protocol?",
            "How does this protocol integrate with ERAS guidelines?",
            "What is the evidence base for this protocol?"
        ]
    elif "surgery" in question.lower() or "surgery" in answer.lower():
        return [
            "What are the common complications?",
            "What is the typical recovery timeline?",
            "Are there alternative surgical approaches?"
        ]
    elif "dosage" in question.lower() or "medication" in answer.lower():
        return [
            "What are the potential side effects?",
            "Are there any drug interactions to be aware of?",
            "What monitoring is recommended?"
        ]
    else:
        return [
            "Can you provide more clinical context?",
            "How does this affect the treatment plan?",
            "What evidence supports this approach?"
        ]
