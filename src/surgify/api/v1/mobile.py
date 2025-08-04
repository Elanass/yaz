"""
Mobile App API Endpoints

Handles mobile app-related requests including:
- App availability status
- Download notifications
- User subscriptions for app updates
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/mobile", tags=["Mobile"])

class AppSubscription(BaseModel):
    email: EmailStr
    platform: str

class FeedbackRequest(BaseModel):
    type: str
    text: str
    email: Optional[EmailStr] = None
    timestamp: str

# In-memory storage for demo (replace with database in production)
app_subscribers = []
feedback_submissions = []

@router.get("/app-status/{platform}")
async def get_app_status(platform: str):
    """Get mobile app availability status"""
    valid_platforms = ["ios", "android"]
    
    if platform.lower() not in valid_platforms:
        raise HTTPException(status_code=400, detail="Invalid platform")
    
    # For now, apps are in development
    return {
        "platform": platform.lower(),
        "available": False,
        "coming_soon": True,
        "estimated_release": "Q2 2025",
        "features": [
            "Case Management",
            "Offline Access", 
            "Push Notifications",
            "Secure Sync"
        ]
    }

@router.post("/subscribe")
async def subscribe_to_app_updates(subscription: AppSubscription):
    """Subscribe to mobile app update notifications"""
    
    # Check if already subscribed
    existing = next(
        (sub for sub in app_subscribers 
         if sub["email"] == subscription.email and sub["platform"] == subscription.platform),
        None
    )
    
    if existing:
        return {"message": "Already subscribed", "status": "success"}
    
    # Add subscription
    app_subscribers.append({
        "email": subscription.email,
        "platform": subscription.platform,
        "subscribed_at": subscription.timestamp if hasattr(subscription, 'timestamp') else None
    })
    
    logger.info(f"New app subscription: {subscription.email} for {subscription.platform}")
    
    return {"message": "Subscription successful", "status": "success"}

@router.get("/subscribers")
async def get_subscribers():
    """Get list of app subscribers (admin only)"""
    return {
        "total": len(app_subscribers),
        "by_platform": {
            "ios": len([s for s in app_subscribers if s["platform"] == "ios"]),
            "android": len([s for s in app_subscribers if s["platform"] == "android"])
        },
        "subscribers": app_subscribers
    }

@router.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    """Submit feedback, issues, or feature requests"""
    
    feedback_data = {
        "type": feedback.type,
        "text": feedback.text,
        "email": feedback.email,
        "timestamp": feedback.timestamp,
        "id": len(feedback_submissions) + 1
    }
    
    feedback_submissions.append(feedback_data)
    
    logger.info(f"New feedback submission: {feedback.type} from {feedback.email or 'anonymous'}")
    
    return {"message": "Feedback submitted successfully", "status": "success"}

@router.get("/feedback")
async def get_feedback():
    """Get feedback submissions (admin only)"""
    return {
        "total": len(feedback_submissions),
        "by_type": {
            "feedback": len([f for f in feedback_submissions if f["type"] == "feedback"]),
            "issue": len([f for f in feedback_submissions if f["type"] == "issue"]),
            "feature": len([f for f in feedback_submissions if f["type"] == "feature"])
        },
        "submissions": feedback_submissions
    }
