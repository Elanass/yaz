"""
Entities API endpoints for Surgify platform
Handles medical entities and concepts navigation
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/patients")
async def get_patients():
    """Get patient entities"""
    return {
        "status": "success",
        "data": [
            {
                "id": "p001",
                "name": "John Doe",
                "age": 45,
                "surgery_type": "Gastric Sleeve",
                "status": "Pre-operative",
                "scheduled_date": "2025-08-15",
                "surgeon": "Dr. Smith"
            },
            {
                "id": "p002", 
                "name": "Jane Smith",
                "age": 38,
                "surgery_type": "Gastric Bypass",
                "status": "Post-operative",
                "completion_date": "2025-08-12",
                "surgeon": "Dr. Johnson"
            }
        ]
    }

@router.get("/procedures")
async def get_procedures():
    """Get procedure entities"""
    return {
        "status": "success",
        "data": [
            {
                "id": "proc001",
                "name": "Laparoscopic Sleeve Gastrectomy",
                "code": "LSG",
                "category": "Bariatric Surgery",
                "estimated_duration": "90 minutes",
                "complexity": "Moderate"
            },
            {
                "id": "proc002",
                "name": "Roux-en-Y Gastric Bypass",
                "code": "RYGB", 
                "category": "Bariatric Surgery",
                "estimated_duration": "120 minutes",
                "complexity": "High"
            }
        ]
    }

@router.get("/surgeons")
async def get_surgeons():
    """Get surgeon entities"""
    return {
        "status": "success",
        "data": [
            {
                "id": "s001",
                "name": "Dr. Emily Smith",
                "specialty": "Bariatric Surgery",
                "experience_years": 12,
                "cases_completed": 850,
                "current_status": "Available"
            },
            {
                "id": "s002",
                "name": "Dr. Michael Johnson", 
                "specialty": "Bariatric Surgery",
                "experience_years": 8,
                "cases_completed": 520,
                "current_status": "In Surgery"
            }
        ]
    }

@router.get("/diagnoses")
async def get_diagnoses():
    """Get diagnosis entities"""
    return {
        "status": "success",
        "data": [
            {
                "id": "d001",
                "code": "E66.01",
                "description": "Morbid obesity due to excess calories",
                "category": "Endocrine, nutritional and metabolic diseases",
                "severity": "High",
                "treatment_options": ["Bariatric Surgery", "Medical Management"]
            },
            {
                "id": "d002",
                "code": "K21.9",
                "description": "Gastro-esophageal reflux disease",
                "category": "Digestive system diseases", 
                "severity": "Moderate",
                "treatment_options": ["Surgical Intervention", "Medication"]
            }
        ]
    }
