"""
Hospitality Module Router
Handles all patient experience and hospitality operations
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
async def hospitality_module_root():
    """Hospitality module root endpoint"""
    return {
        "module": "hospitality",
        "description": "Patient experience and hospitality services",
        "version": "2.0.0",
        "endpoints": {
            "accommodations": "/accommodations",
            "amenities": "/amenities",
            "dining": "/dining",
            "transportation": "/transportation",
            "concierge": "/concierge"
        }
    }

@router.get("/accommodations")
async def get_accommodations():
    """Get patient accommodation options"""
    return {
        "room_types": [
            {
                "type": "private_suite",
                "features": ["private_bathroom", "family_seating", "entertainment_system"],
                "rate_per_night": 450.00,
                "availability": "high"
            },
            {
                "type": "semi_private",
                "features": ["shared_bathroom", "visitor_chair", "tv"],
                "rate_per_night": 250.00,
                "availability": "medium"
            },
            {
                "type": "standard_room",
                "features": ["basic_amenities", "visitor_policies"],
                "rate_per_night": 150.00,
                "availability": "high"
            }
        ]
    }

@router.get("/amenities")
async def get_amenities():
    """Get available patient amenities"""
    return {
        "amenities": [
            {
                "category": "wellness",
                "services": ["spa_treatments", "massage_therapy", "meditation_room"]
            },
            {
                "category": "entertainment",
                "services": ["library", "wifi", "streaming_services", "gaming_console"]
            },
            {
                "category": "comfort",
                "services": ["robes_slippers", "premium_bedding", "temperature_control"]
            },
            {
                "category": "family_support",
                "services": ["family_lounge", "children_area", "overnight_accommodations"]
            }
        ]
    }

@router.get("/dining")
async def get_dining_options():
    """Get dining and nutrition services"""
    return {
        "dining_services": [
            {
                "service": "room_service",
                "hours": "24/7",
                "special_diets": ["post_bariatric", "diabetic", "heart_healthy"]
            },
            {
                "service": "family_dining",
                "location": "cafe_level_1",
                "hours": "6:00 AM - 10:00 PM"
            },
            {
                "service": "nutritionist_consultation",
                "availability": "by_appointment",
                "specialties": ["bariatric_nutrition", "meal_planning"]
            }
        ]
    }

@router.get("/transportation")
async def get_transportation_services():
    """Get transportation services"""
    return {
        "transportation": [
            {
                "type": "airport_shuttle",
                "schedule": "every_2_hours",
                "cost": "complimentary",
                "advance_booking": "24_hours"
            },
            {
                "type": "local_taxi_service",
                "availability": "24/7",
                "cost": "patient_responsibility",
                "booking": "on_demand"
            },
            {
                "type": "medical_transport",
                "for": "wheelchair_assistance",
                "cost": "included",
                "booking": "nursing_staff"
            }
        ]
    }

@router.get("/concierge")
async def get_concierge_services():
    """Get concierge services"""
    return {
        "services": [
            {
                "service": "local_attractions",
                "description": "Information and booking for local tours and activities"
            },
            {
                "service": "personal_shopping",
                "description": "Assistance with personal shopping needs"
            },
            {
                "service": "appointment_coordination",
                "description": "Help scheduling follow-up appointments"
            },
            {
                "service": "special_requests",
                "description": "Assistance with special dietary or accessibility needs"
            }
        ]
    }

@router.post("/book-accommodation")
async def book_accommodation(booking_data: Dict[str, Any]):
    """Book patient accommodation"""
    return {
        "message": "Accommodation booked successfully",
        "booking_id": "HOSP_001",
        "room_type": booking_data.get("room_type", "private_suite"),
        "check_in": "2025-08-14",
        "check_out": "2025-08-17",
        "total_cost": 1350.00
    }

@router.get("/experience/{patient_id}")
async def get_patient_experience(patient_id: str):
    """Get patient experience details"""
    return {
        "patient_id": patient_id,
        "current_stay": {
            "room": "Suite_205",
            "amenities_used": ["spa_treatment", "room_service"],
            "satisfaction_score": 4.8
        },
        "preferences": {
            "dietary": "post_bariatric",
            "room_temperature": 72,
            "quiet_hours": "22:00-06:00"
        }
    }

@router.post("/feedback")
async def submit_feedback(feedback_data: Dict[str, Any]):
    """Submit patient feedback"""
    return {
        "message": "Feedback submitted successfully",
        "feedback_id": "FB_001",
        "follow_up": "within_24_hours"
    }
