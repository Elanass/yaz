"""
Cases API - Surgify Platform
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/cases", tags=["Cases"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database" / "surgify.db"

class CaseResponse(BaseModel):
    id: int
    case_number: str
    patient_id: str
    procedure_type: str
    diagnosis: str
    status: str
    risk_score: float
    recommendations: List[str]

class CaseCreate(BaseModel):
    patient_id: str
    procedure_type: str
    diagnosis: str
    status: str = "planned"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))

@router.get("/", response_model=List[CaseResponse])
async def get_cases():
    """Get all cases"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.case_number, p.patient_id, c.procedure_type, 
                   c.diagnosis, c.status, c.risk_score, c.recommendations
            FROM cases c
            JOIN patients p ON c.patient_id = p.id
            ORDER BY c.created_at DESC
        """)
        
        cases = []
        for row in cursor.fetchall():
            import json
            recommendations = json.loads(row[7]) if row[7] else []
            cases.append(CaseResponse(
                id=row[0],
                case_number=row[1],
                patient_id=row[2],
                procedure_type=row[3],
                diagnosis=row[4],
                status=row[5],
                risk_score=row[6] or 0.0,
                recommendations=recommendations
            ))
        
        conn.close()
        return cases
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(case_id: int):
    """Get a specific case"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.case_number, p.patient_id, c.procedure_type, 
                   c.diagnosis, c.status, c.risk_score, c.recommendations
            FROM cases c
            JOIN patients p ON c.patient_id = p.id
            WHERE c.id = ?
        """, (case_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        import json
        recommendations = json.loads(row[7]) if row[7] else []
        case = CaseResponse(
            id=row[0],
            case_number=row[1],
            patient_id=row[2],
            procedure_type=row[3],
            diagnosis=row[4],
            status=row[5],
            risk_score=row[6] or 0.0,
            recommendations=recommendations
        )
        
        conn.close()
        return case
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/{case_id}/decision-support")
async def get_decision_support(case_id: int):
    """Get decision support for a case"""
    try:
        # Get case details first
        case = await get_case(case_id)
        
        # Generate decision support based on case
        recommendations = generate_recommendations(case.procedure_type, case.diagnosis)
        
        return {
            "case_id": case_id,
            "recommendations": recommendations,
            "risk_assessment": {
                "overall_risk": case.risk_score,
                "risk_factors": get_risk_factors(case.diagnosis),
                "mitigation_strategies": get_mitigation_strategies(case.procedure_type)
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
