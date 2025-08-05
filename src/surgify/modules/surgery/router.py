"""
Surgery Module Router
Handles all surgery-related operations
"""

from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/")
async def surgery_module_root():
    """Surgery module root endpoint"""
    return {
        "module": "surgery",
        "description": "Surgical procedure planning and execution",
        "version": "2.0.0",
        "endpoints": {
            "procedures": "/procedures",
            "planning": "/planning",
            "protocols": "/protocols",
            "equipment": "/equipment",
        },
    }


@router.get("/procedures")
async def get_procedures():
    """Get available surgical procedures"""
    return {
        "procedures": [
            {
                "id": "gastric_sleeve",
                "name": "Gastric Sleeve Surgery",
                "type": "bariatric",
                "duration_minutes": 60,
                "complexity": "intermediate",
            },
            {
                "id": "gastric_bypass",
                "name": "Gastric Bypass Surgery",
                "type": "bariatric",
                "duration_minutes": 120,
                "complexity": "advanced",
            },
        ]
    }


@router.get("/planning")
async def get_surgical_planning():
    """Get surgical planning tools"""
    return {
        "planning_tools": [
            "pre_operative_assessment",
            "risk_stratification",
            "resource_allocation",
            "timeline_optimization",
        ]
    }


@router.get("/protocols")
async def get_protocols():
    """Get surgical protocols"""
    return {
        "protocols": [
            {
                "name": "ERAS Protocol",
                "type": "Enhanced Recovery After Surgery",
                "applicable_procedures": ["gastric_sleeve", "gastric_bypass"],
            }
        ]
    }


@router.get("/equipment")
async def get_equipment():
    """Get surgical equipment requirements"""
    return {
        "equipment_categories": [
            "laparoscopic_tools",
            "monitoring_devices",
            "safety_equipment",
            "backup_systems",
        ]
    }


# Add routes from existing surgery.py
@router.post("/case")
async def create_surgical_case(case_data: Dict[str, Any]):
    """Create a new surgical case"""
    return {
        "message": "Surgical case created successfully",
        "case_id": "SURG_001",
        "status": "scheduled",
    }


@router.get("/cases")
async def get_surgical_cases():
    """Get all surgical cases"""
    return {
        "cases": [
            {
                "id": "SURG_001",
                "patient": "John Doe",
                "procedure": "Gastric Sleeve",
                "status": "scheduled",
                "date": "2025-08-15",
            }
        ]
    }
