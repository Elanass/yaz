"""
Cases API - Surgify Platform
Enhanced with optional Universal Research capabilities
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from surgify.core.services.case_service import CaseService
from surgify.core.services.auth_service import get_current_user
from surgify.core.models.user import User

# Universal Research Integration (Optional Enhancement)
try:
    from surgify.modules.universal_research.adapters.legacy_bridge import LegacyBridge
    from surgify.modules.universal_research.adapters.surgify_adapter import SurgifyAdapter
    from surgify.core.database import get_db
    RESEARCH_AVAILABLE = True
    LegacyBridge = LegacyBridge  # Make available for type hints
except ImportError:
    RESEARCH_AVAILABLE = False
    LegacyBridge = None  # Provide None fallback

router = APIRouter(tags=["Cases"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database" / "surgify.db"

class CaseResponse(BaseModel):
    id: int
    case_number: str
    patient_id: str
    procedure_type: str
    surgery_type: Optional[str] = None  # For backward compatibility
    diagnosis: str
    status: str
    risk_score: float
    recommendations: List[str]
    
    def model_post_init(self, __context):
        # Set surgery_type to procedure_type if not provided
        if self.surgery_type is None:
            self.surgery_type = self.procedure_type

class CaseCreate(BaseModel):
    patient_id: str
    procedure_type: str
    diagnosis: str
    status: str = "planned"

# Pydantic models for request/response
class CaseCreateRequest(BaseModel):
    patient_id: str
    surgery_type: str
    procedure_type: Optional[str] = None  # For backward compatibility
    diagnosis: Optional[str] = None
    status: str = "planned"
    pre_op_notes: Optional[str] = None
    post_op_notes: Optional[str] = None

# Dependency
case_service = CaseService()

# Research enhancement dependencies (optional)
def get_legacy_bridge() -> Optional[Any]:
    """Get legacy bridge for research enhancements (optional)"""
    if not RESEARCH_AVAILABLE or LegacyBridge is None:
        return None
    try:
        from sqlalchemy.orm import Session
        db_session = next(get_db())
        surgify_adapter = SurgifyAdapter(db_session)
        return LegacyBridge(case_service, surgify_adapter)
    except Exception:
        return None

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))

@router.get("/cases", response_model=List[CaseResponse])
async def list_cases():
    """List all cases"""
    try:
        cases = case_service.list_cases()
        return [CaseResponse(**case) for case in cases]
    except Exception as e:
        return []

@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(case_id: int):
    """Get a specific case"""
    try:
        case_data = case_service.get_case(case_id)
        return CaseResponse(**case_data)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/cases", response_model=CaseResponse)
async def create_case(request: CaseCreateRequest):
    """Create a new case"""
    try:
        case = case_service.create_case(request)
        return CaseResponse(**case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: int, request: CaseCreateRequest):
    """Update an existing case"""
    try:
        case = case_service.update_case(case_id, request)
        return CaseResponse(**case)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/cases/{case_id}")
async def delete_case(case_id: int):
    """Delete a case"""
    try:
        case_service.delete_case(case_id)
        return {"detail": f"Case {case_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/cases/{case_id}/decision-support")
async def get_decision_support(case_id: int):
    """Get decision support for a case"""
    try:
        # Get case details first
        case_data = case_service.get_case(case_id)
        
        # Generate decision support based on case
        recommendations = generate_recommendations(case_data["procedure_type"], case_data["diagnosis"])
        
        return {
            "case_id": case_id,
            "recommendations": recommendations,
            "risk_assessment": {
                "overall_risk": case_data["risk_score"],
                "risk_factors": get_risk_factors(case_data["diagnosis"]),
                "mitigation_strategies": get_mitigation_strategies(case_data["procedure_type"])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating decision support: {str(e)}")

def generate_recommendations(procedure_type: str, diagnosis: str) -> List[str]:
    """Generate recommendations based on procedure and diagnosis"""
    recommendations = []
    
    if "cancer" in diagnosis.lower():
        recommendations.extend([
            "Consider multidisciplinary team consultation",
            "Evaluate for neoadjuvant therapy",
            "Assess nutritional status pre-operatively"
        ])
    
    if procedure_type == "laparoscopic":
        recommendations.extend([
            "Ensure CO2 insufflation equipment is ready",
            "Prepare for potential conversion to open",
            "Monitor for trocar site complications"
        ])
    elif procedure_type == "gastric_resection":
        recommendations.extend([
            "Plan for intraoperative frozen section",
            "Ensure adequate margins",
            "Prepare for gastric reconstruction"
        ])
    
    return recommendations

def get_risk_factors(diagnosis: str) -> List[str]:
    """Get risk factors based on diagnosis"""
    risk_factors = ["Patient age", "Comorbidities", "Previous surgeries"]
    
    if "cancer" in diagnosis.lower():
        risk_factors.extend(["Tumor stage", "Metastatic potential", "Nutritional status"])
    
    return risk_factors

def get_mitigation_strategies(procedure_type: str) -> List[str]:
    """Get mitigation strategies based on procedure type"""
    strategies = ["Standard monitoring", "Prophylactic antibiotics", "DVT prevention"]
    
    if procedure_type == "laparoscopic":
        strategies.extend(["Monitor for CO2 embolism", "Careful trocar placement"])
    elif procedure_type == "gastric_resection":
        strategies.extend(["Anastomotic leak prevention", "Nutritional support planning"])
    
    return strategies

# Note: These endpoints use the case service for demonstration
# The main endpoints (/, /{case_id}) above use direct database queries
# and are enhanced with optional research capabilities
