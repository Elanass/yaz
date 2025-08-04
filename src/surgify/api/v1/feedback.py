"""
Feedback API Endpoints

Handles user feedback, issues, and feature requests
"""

from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/feedback", tags=["Feedback"])

class FeedbackRequest(BaseModel):
    type: str  # feedback, issue, feature
    text: str
    email: Optional[EmailStr] = None
    timestamp: Optional[str] = None

# In-memory storage for demo (replace with database in production)
feedback_submissions = []

@router.post("/")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback, issues, or feature requests"""
    
    feedback_data = {
        "type": feedback.type,
        "text": feedback.text,
        "email": feedback.email,
        "timestamp": feedback.timestamp or datetime.now().isoformat(),
        "id": len(feedback_submissions) + 1
    }
    
    feedback_submissions.append(feedback_data)
    
    logger.info(f"New feedback submission: {feedback.type} from {feedback.email or 'anonymous'}")
    
    return {"message": "Feedback submitted successfully", "status": "success"}

@router.get("/")
async def get_feedback():
    """Get feedback submissions (admin only)"""
    return {
        "total": len(feedback_submissions),
        "by_type": {
            "feedback": len([f for f in feedback_submissions if f["type"] == "feedback"]),
            "issue": len([f for f in feedback_submissions if f["type"] == "issue"]),
            "feature": len([f for f in feedback_submissions if f["type"] == "feature"])
        },
        "submissions": feedback_submissions[-10:]  # Last 10 submissions
    }
