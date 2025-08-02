"""
Concepts API endpoints for Surgify platform
Handles business concepts and domain knowledge
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/workflows")
async def get_workflows():
    """Get workflow concepts"""
    return {
        "status": "success",
        "data": [
            {
                "id": "wf001",
                "name": "Pre-operative Assessment",
                "description": "Complete patient evaluation before surgery",
                "steps": ["Medical History", "Physical Exam", "Lab Tests", "Imaging"],
                "estimated_duration": "2-3 days",
                "responsible_team": "Surgery Team"
            },
            {
                "id": "wf002",
                "name": "Post-operative Care",
                "description": "Patient recovery and follow-up protocol",
                "steps": ["Recovery Room", "Floor Transfer", "Daily Rounds", "Discharge Planning"],
                "estimated_duration": "2-5 days",
                "responsible_team": "Nursing & Surgery Team"
            }
        ]
    }

@router.get("/protocols")
async def get_protocols():
    """Get protocol concepts"""
    return {
        "status": "success",
        "data": [
            {
                "id": "prot001",
                "name": "ERAS Protocol",
                "description": "Enhanced Recovery After Surgery",
                "category": "Perioperative Care",
                "evidence_level": "Level I",
                "implementation_rate": "85%"
            },
            {
                "id": "prot002",
                "name": "Antibiotic Prophylaxis",
                "description": "Surgical site infection prevention",
                "category": "Infection Control",
                "evidence_level": "Level I", 
                "implementation_rate": "98%"
            }
        ]
    }

@router.get("/resources")
async def get_resources():
    """Get resource concepts"""
    return {
        "status": "success",
        "data": [
            {
                "id": "res001",
                "name": "Operating Room 1",
                "type": "Surgical Suite",
                "status": "Available",
                "equipment": ["Laparoscopic Tower", "C-Arm", "Anesthesia Machine"],
                "capacity": "1 case"
            },
            {
                "id": "res002",
                "name": "Recovery Bay A",
                "type": "Post-Anesthesia Care",
                "status": "Occupied",
                "equipment": ["Monitoring", "Oxygen", "IV Pumps"],
                "capacity": "4 patients"
            }
        ]
    }

@router.get("/quality")
async def get_quality_metrics():
    """Get quality metric concepts"""
    return {
        "status": "success",
        "data": [
            {
                "id": "qm001",
                "name": "Surgical Site Infection Rate",
                "value": "2.1%",
                "target": "<2.5%",
                "trend": "Decreasing",
                "period": "Last 30 days"
            },
            {
                "id": "qm002",
                "name": "Length of Stay",
                "value": "2.3 days",
                "target": "<3.0 days",
                "trend": "Stable",
                "period": "Last 30 days"
            }
        ]
    }
