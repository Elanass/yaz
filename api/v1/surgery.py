"""
Surgery API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

router = APIRouter()


class SurgeryProcedure(BaseModel):
    id: Optional[str] = None
    name: str
    type: str
    duration_minutes: int
    complexity_level: str
    surgeon_id: str
    patient_id: str
    scheduled_date: datetime
    status: str = "scheduled"


class SurgeryRequest(BaseModel):
    procedure_type: str
    patient_id: str
    surgeon_id: str
    preferred_date: datetime
    urgency_level: str = "routine"
    notes: Optional[str] = None


class SurgeryOutcome(BaseModel):
    surgery_id: str
    outcome: str
    complications: Optional[List[str]] = None
    duration_actual: int
    notes: Optional[str] = None


@router.get("/")
async def surgery_root():
    """Surgery API root"""
    return {
        "message": "Surgery Management API",
        "version": "1.0.0",
        "endpoints": {
            "procedures": "/api/v1/surgery/procedures",
            "schedule": "/api/v1/surgery/schedule",
            "outcomes": "/api/v1/surgery/outcomes"
        }
    }


@router.get("/procedures")
async def get_procedures():
    """Get all surgery procedures - for sidebar link"""
    procedures = [
        {
            "id": "SURG001",
            "name": "Gastric Sleeve Surgery",
            "type": "Bariatric",
            "duration_minutes": 120,
            "complexity_level": "moderate",
            "surgeon_id": "DR001",
            "patient_id": "PAT001",
            "scheduled_date": "2025-08-15T09:00:00",
            "status": "scheduled"
        },
        {
            "id": "SURG002", 
            "name": "Gastric Bypass Surgery",
            "type": "Bariatric",
            "duration_minutes": 180,
            "complexity_level": "high",
            "surgeon_id": "DR002",
            "patient_id": "PAT002",
            "scheduled_date": "2025-08-16T10:00:00",
            "status": "scheduled"
        }
    ]
    return {"procedures": procedures, "total": len(procedures)}


@router.post("/procedures", response_model=Dict[str, Any])
async def schedule_surgery(surgery_request: SurgeryRequest):
    """Schedule a new surgery"""
    # Mock implementation
    surgery_id = f"surg-{len(str(surgery_request.patient_id)) + 100}"
    
    scheduled_surgery = {
        "id": surgery_id,
        "procedure_type": surgery_request.procedure_type,
        "patient_id": surgery_request.patient_id,
        "surgeon_id": surgery_request.surgeon_id,
        "scheduled_date": surgery_request.preferred_date.isoformat(),
        "urgency_level": surgery_request.urgency_level,
        "status": "scheduled",
        "notes": surgery_request.notes
    }
    
    return {
        "message": "Surgery scheduled successfully",
        "surgery": scheduled_surgery
    }


@router.get("/schedule")
async def get_surgery_schedule():
    """Get surgery schedule"""
    schedule = {
        "today": [
            {
                "id": "surg-003",
                "procedure": "Gastric Sleeve",
                "surgeon": "Dr. Smith",
                "time": "09:00",
                "duration": "120 min",
                "status": "scheduled"
            }
        ],
        "upcoming": [
            {
                "id": "surg-001",
                "procedure": "Laparoscopic Gastrectomy",
                "surgeon": "Dr. Johnson", 
                "date": "2025-08-05",
                "time": "09:00",
                "duration": "240 min"
            }
        ]
    }
    return schedule


@router.get("/scheduling")
async def get_surgery_scheduling():
    """Get surgery scheduling dashboard - for sidebar link"""
    schedule = {
        "today": [
            {"time": "09:00", "procedure": "Gastric Sleeve", "surgeon": "Dr. Smith", "room": "OR-1"},
            {"time": "11:30", "procedure": "Gastric Bypass", "surgeon": "Dr. Johnson", "room": "OR-2"}
        ],
        "upcoming": [
            {"date": "2025-08-03", "procedures": 3},
            {"date": "2025-08-04", "procedures": 2},
            {"date": "2025-08-05", "procedures": 4}
        ],
        "availability": {
            "or_rooms": {"total": 4, "available": 2},
            "surgeons": {"total": 8, "available": 5}
        }
    }
    return schedule


@router.get("/resources")
async def get_surgery_resources():
    """Get surgery resource management - for sidebar link"""
    resources = {
        "equipment": {
            "laparoscopes": {"total": 6, "available": 4, "maintenance": 1},
            "monitors": {"total": 12, "available": 8, "in_use": 4},
            "surgical_robots": {"total": 2, "available": 1, "scheduled": 1}
        },
        "personnel": {
            "surgeons": {"total": 8, "available": 5, "on_call": 2},
            "nurses": {"total": 20, "available": 12, "scheduled": 8},
            "anesthesiologists": {"total": 6, "available": 4, "on_call": 1}
        },
        "rooms": {
            "operating_rooms": {"total": 6, "available": 3, "occupied": 2, "maintenance": 1},
            "recovery_rooms": {"total": 10, "available": 6, "occupied": 4}
        }
    }
    return resources


@router.post("/outcomes")
async def record_surgery_outcome(outcome: SurgeryOutcome):
    """Record surgery outcome"""
    return {
        "message": "Surgery outcome recorded successfully",
        "outcome": outcome.dict()
    }


@router.get("/outcomes/{surgery_id}")
async def get_surgery_outcome(surgery_id: str):
    """Get surgery outcome by ID"""
    # Mock outcome data
    outcome = {
        "surgery_id": surgery_id,
        "outcome": "successful",
        "complications": [],
        "duration_actual": 220,
        "recovery_notes": "Patient recovering well",
        "discharge_date": "2025-08-07"
    }
    return outcome


@router.get("/statistics")
async def get_surgery_statistics():
    """Get surgery statistics"""
    stats = {
        "total_surgeries": 150,
        "success_rate": 96.5,
        "average_duration": 180,
        "by_type": {
            "laparoscopic": 85,
            "open": 35,
            "endoscopic": 30
        },
        "monthly_trend": [
            {"month": "June", "count": 45},
            {"month": "July", "count": 52},
            {"month": "August", "count": 53}
        ]
    }
    return stats
