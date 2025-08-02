"""
Insurance API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date

router = APIRouter()


class InsuranceProvider(BaseModel):
    id: Optional[str] = None
    name: str
    type: str  # private, public, self-pay
    coverage_details: Dict[str, Any]
    contact_info: Dict[str, str]
    policy_numbers: List[str] = []


class InsuranceClaim(BaseModel):
    id: Optional[str] = None
    patient_id: str
    provider_id: str
    procedure_code: str
    claim_amount: float
    status: str = "pending"
    submitted_date: datetime
    approval_date: Optional[datetime] = None
    notes: Optional[str] = None


class PreAuthorizationRequest(BaseModel):
    patient_id: str
    provider_id: str
    procedure_code: str
    estimated_cost: float
    urgency: str = "routine"
    clinical_notes: str


class CoverageVerification(BaseModel):
    patient_id: str
    provider_id: str
    service_type: str
    verification_date: date


@router.get("/")
async def insurance_root():
    """Insurance API root"""
    return {
        "message": "Insurance Management API",
        "version": "1.0.0",
        "endpoints": {
            "providers": "/api/v1/insurance/providers",
            "claims": "/api/v1/insurance/claims",
            "preauth": "/api/v1/insurance/preauth",
            "coverage": "/api/v1/insurance/coverage",
            "verification": "/api/v1/insurance/verification",
            "billing": "/api/v1/insurance/billing"
        }
    }


@router.get("/providers")
async def get_insurance_providers():
    """Get all insurance providers"""
    # Mock data for demonstration
    providers = [
        {
            "id": "ins_001",
            "name": "HealthFirst Insurance",
            "type": "private",
            "coverage_details": {"surgery": True, "emergency": True, "consultation": True},
            "contact_info": {"phone": "+1-800-HEALTH", "email": "support@healthfirst.com"}
        },
        {
            "id": "ins_002", 
            "name": "Medicare",
            "type": "public",
            "coverage_details": {"surgery": True, "emergency": True, "consultation": True},
            "contact_info": {"phone": "+1-800-MEDICARE", "email": "info@medicare.gov"}
        }
    ]
    return {"providers": providers, "total": len(providers)}


@router.post("/providers")
async def create_insurance_provider(provider: InsuranceProvider):
    """Create a new insurance provider"""
    # Generate ID if not provided
    if not provider.id:
        provider.id = f"ins_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # In a real application, save to database
    return {
        "message": "Insurance provider created successfully",
        "provider": provider.dict()
    }


@router.get("/providers/{provider_id}")
async def get_insurance_provider(provider_id: str):
    """Get specific insurance provider by ID"""
    # Mock data - in real app, query database
    if provider_id == "ins_001":
        return {
            "id": "ins_001",
            "name": "HealthFirst Insurance",
            "type": "private",
            "coverage_details": {"surgery": True, "emergency": True, "consultation": True},
            "contact_info": {"phone": "+1-800-HEALTH", "email": "support@healthfirst.com"}
        }
    raise HTTPException(status_code=404, detail="Insurance provider not found")


@router.get("/claims")
async def get_insurance_claims(status: Optional[str] = None):
    """Get insurance claims, optionally filtered by status"""
    # Mock data
    claims = [
        {
            "id": "claim_001",
            "patient_id": "pat_001",
            "provider_id": "ins_001",
            "procedure_code": "43644",
            "claim_amount": 15000.00,
            "status": "approved",
            "submitted_date": "2024-01-15T10:00:00Z"
        },
        {
            "id": "claim_002",
            "patient_id": "pat_002", 
            "provider_id": "ins_002",
            "procedure_code": "43770",
            "claim_amount": 12000.00,
            "status": "pending",
            "submitted_date": "2024-01-20T14:30:00Z"
        }
    ]
    
    if status:
        claims = [c for c in claims if c["status"] == status]
    
    return {"claims": claims, "total": len(claims)}


@router.post("/claims")
async def submit_insurance_claim(claim: InsuranceClaim):
    """Submit a new insurance claim"""
    if not claim.id:
        claim.id = f"claim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Insurance claim submitted successfully",
        "claim": claim.dict()
    }


@router.get("/claims/{claim_id}")
async def get_insurance_claim(claim_id: str):
    """Get specific insurance claim by ID"""
    # Mock data - in real app, query database
    if claim_id == "claim_001":
        return {
            "id": "claim_001",
            "patient_id": "pat_001",
            "provider_id": "ins_001",
            "procedure_code": "43644",
            "claim_amount": 15000.00,
            "status": "approved",
            "submitted_date": "2024-01-15T10:00:00Z",
            "approval_date": "2024-01-18T09:15:00Z"
        }
    raise HTTPException(status_code=404, detail="Insurance claim not found")


@router.put("/claims/{claim_id}/status")
async def update_claim_status(claim_id: str, status: str):
    """Update insurance claim status"""
    valid_statuses = ["pending", "approved", "denied", "processing"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    return {
        "message": f"Claim {claim_id} status updated to {status}",
        "claim_id": claim_id,
        "new_status": status,
        "updated_at": datetime.now()
    }


@router.post("/preauth")
async def request_preauthorization(request: PreAuthorizationRequest):
    """Request pre-authorization for a procedure"""
    auth_id = f"preauth_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "message": "Pre-authorization request submitted",
        "authorization_id": auth_id,
        "request": request.dict(),
        "estimated_approval_time": "3-5 business days"
    }


@router.get("/coverage/verify")
async def verify_coverage(patient_id: str, provider_id: str, service_type: str):
    """Verify insurance coverage for a patient and service"""
    # Mock verification logic
    coverage_info = {
        "patient_id": patient_id,
        "provider_id": provider_id,
        "service_type": service_type,
        "is_covered": True,
        "copay_amount": 50.00,
        "deductible_remaining": 500.00,
        "coverage_percentage": 80,
        "verification_date": date.today().isoformat()
    }
    
    return {"coverage": coverage_info}


@router.get("/statistics")
async def get_insurance_statistics():
    """Get insurance-related statistics"""
    return {
        "total_claims": 150,
        "pending_claims": 25,
        "approved_claims": 120,
        "denied_claims": 5,
        "average_claim_amount": 13500.00,
        "total_claim_value": 2025000.00,
        "approval_rate": 80.0,
        "average_processing_time_days": 7.5
    }


@router.get("/verification")
async def get_verification_dashboard():
    """Get coverage verification dashboard - for sidebar link"""
    verification = {
        "pending_verifications": [
            {"patient_id": "PAT001", "insurance": "BlueCross", "procedure": "Gastric Sleeve", "priority": "high"},
            {"patient_id": "PAT002", "insurance": "Aetna", "procedure": "Gastric Bypass", "priority": "medium"},
            {"patient_id": "PAT003", "insurance": "UnitedHealth", "procedure": "Endoscopy", "priority": "low"}
        ],
        "verification_stats": {
            "today": {"completed": 15, "pending": 8, "rejected": 2},
            "this_week": {"completed": 89, "pending": 12, "rejected": 6},
            "success_rate": 93.5
        },
        "insurance_providers": [
            {"name": "BlueCross BlueShield", "response_time": "2.1 hours", "approval_rate": 94},
            {"name": "Aetna", "response_time": "3.2 hours", "approval_rate": 91},
            {"name": "UnitedHealth", "response_time": "1.8 hours", "approval_rate": 96}
        ]
    }
    return verification


@router.get("/billing")
async def get_billing_dashboard():
    """Get billing management dashboard - for sidebar link"""
    billing = {
        "outstanding_bills": [
            {"invoice_id": "INV001", "patient": "John Doe", "amount": 12500, "days_overdue": 15},
            {"invoice_id": "INV002", "patient": "Jane Smith", "amount": 8750, "days_overdue": 8},
            {"invoice_id": "INV003", "patient": "Bob Johnson", "amount": 15200, "days_overdue": 22}
        ],
        "billing_summary": {
            "total_outstanding": 485600,
            "average_collection_days": 32,
            "collection_rate": 87.5,
            "rejected_claims": 15
        },
        "monthly_revenue": {
            "june": 125000,
            "july": 142000,
            "august": 138000
        },
        "payment_methods": {
            "insurance": 78,
            "cash": 12,
            "credit_card": 8,
            "payment_plan": 2
        }
    }
    return billing
