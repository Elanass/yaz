"""
Insurance Module Router
Handles all insurance-related operations
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

@router.get("/")
async def insurance_module_root():
    """Insurance module root endpoint"""
    return {
        "module": "insurance",
        "description": "Insurance coverage and authorization",
        "version": "2.0.0",
        "endpoints": {
            "coverage": "/coverage",
            "authorization": "/authorization",
            "claims": "/claims",
            "eligibility": "/eligibility"
        }
    }

@router.get("/coverage")
async def get_coverage_info():
    """Get insurance coverage information"""
    return {
        "coverage_types": [
            {
                "type": "bariatric_surgery",
                "covered_procedures": ["gastric_sleeve", "gastric_bypass"],
                "requirements": ["BMI >= 40", "comorbidities", "6_month_diet"]
            }
        ]
    }

@router.get("/authorization")
async def get_authorization_status():
    """Get authorization status for procedures"""
    return {
        "authorizations": [
            {
                "case_id": "SURG_001",
                "procedure": "gastric_sleeve",
                "status": "approved",
                "auth_number": "AUTH_123456"
            }
        ]
    }

@router.post("/authorization")
async def request_authorization(auth_request: Dict[str, Any]):
    """Request insurance authorization"""
    return {
        "message": "Authorization request submitted",
        "request_id": "REQ_001",
        "estimated_response": "3-5 business days"
    }

@router.get("/claims")
async def get_claims():
    """Get insurance claims"""
    return {
        "claims": [
            {
                "claim_id": "CLM_001",
                "case_id": "SURG_001",
                "amount": 25000.00,
                "status": "processed",
                "payment_date": "2025-08-20"
            }
        ]
    }

@router.get("/eligibility")
async def check_eligibility():
    """Check patient eligibility"""
    return {
        "eligibility_criteria": [
            "active_coverage",
            "met_deductible",
            "prior_authorization",
            "in_network_provider"
        ]
    }
