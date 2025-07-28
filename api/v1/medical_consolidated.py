"""
Consolidated Medical API Routes
DRY implementation of all medical endpoints using shared patterns
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from core.dependencies import DatabaseSession, CurrentUser, EncryptionService
from core.models.base import ApiResponse
from core.medical.consolidated import core_medical
from core.medical.utils import (
    validate_all_medical_data, 
    create_secure_medical_record,
    MedicalFormatting,
    MedicalReportGenerator
)
from data.models import Patient, Case, Decision, ClinicalOutcome


router = APIRouter(prefix="/medical", tags=["Medical Core"])


# ========================================
# EMR Endpoints
# ========================================

@router.post("/patients", response_model=ApiResponse[Dict[str, Any]])
async def create_patient(
    patient_data: Dict[str, Any],
    session: DatabaseSession,
    current_user: CurrentUser,
    encryption: EncryptionService
):
    """Create new patient record with full HIPAA compliance"""
    
    try:
        patient = await core_medical.create_patient_record(
            patient_data, session, encryption
        )
        
        return ApiResponse.success_response(
            data={
                "patient_id": str(patient.id),
                "created_at": patient.created_at.isoformat(),
                "message": "Patient record created successfully"
            },
            message="Patient registered in EMR system"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create patient record: {str(e)}"
        )


@router.get("/patients/{patient_id}/history", response_model=ApiResponse[Dict[str, Any]])
async def get_patient_history(
    patient_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
    include_sensitive: bool = Query(False, description="Include sensitive data (requires admin role)")
):
    """Get comprehensive patient history"""
    
    try:
        history = await core_medical.get_patient_history(
            patient_id, session, include_sensitive
        )
        
        return ApiResponse.success_response(
            data=history,
            message=f"Retrieved history for patient {patient_id}"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve patient history: {str(e)}"
        )


# ========================================
# Decision Support Endpoints
# ========================================

@router.post("/decisions/analyze", response_model=ApiResponse[Dict[str, Any]])
async def generate_clinical_decision(
    analysis_request: Dict[str, Any],
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Generate comprehensive clinical decision with ADCI, Surgery, and Precision analysis"""
    
    try:
        # Validate input data
        patient_data = analysis_request.get('patient_data', {})
        clinical_data = analysis_request.get('clinical_data', {})
        context = analysis_request.get('context', {})
        
        validation_errors = validate_all_medical_data({**patient_data, **clinical_data})
        if validation_errors:
            raise ValueError(f"Validation errors: {', '.join(validation_errors)}")
        
        # Generate decision
        decision = await core_medical.generate_clinical_decision(
            patient_data, clinical_data, context
        )
        
        # Save decision to database
        decision_record = Decision(
            patient_id=patient_data.get('id'),
            decision_type='comprehensive_analysis',
            recommendation=decision['consolidated_recommendation']['primary'],
            confidence_score=decision['confidence_score'],
            analysis_data=decision,
            created_by=current_user.id,
            created_at=datetime.utcnow()
        )
        
        session.add(decision_record)
        await session.commit()
        
        return ApiResponse.success_response(
            data=decision,
            message="Clinical decision generated successfully"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate clinical decision: {str(e)}"
        )


@router.get("/decisions/{decision_id}", response_model=ApiResponse[Dict[str, Any]])
async def get_decision(
    decision_id: str,
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Get specific clinical decision"""
    
    try:
        result = await session.execute(
            select(Decision)
            .options(selectinload(Decision.patient))
            .where(Decision.id == decision_id)
        )
        decision = result.scalar_one_or_none()
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found"
            )
        
        return ApiResponse.success_response(
            data={
                "decision_id": str(decision.id),
                "patient_id": str(decision.patient_id),
                "recommendation": decision.recommendation,
                "confidence_score": decision.confidence_score,
                "analysis_data": decision.analysis_data,
                "created_at": decision.created_at.isoformat(),
                "created_by": decision.created_by
            },
            message="Decision retrieved successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve decision: {str(e)}"
        )


# ========================================
# Surgery Workflow Endpoints
# ========================================

@router.put("/cases/{case_id}/workflow", response_model=ApiResponse[Dict[str, Any]])
async def update_surgery_workflow(
    case_id: str,
    workflow_update: Dict[str, Any],
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Update gastric surgery workflow stage"""
    
    try:
        workflow_stage = workflow_update.get('stage')
        stage_data = workflow_update.get('data', {})
        
        if not workflow_stage:
            raise ValueError("Workflow stage is required")
        
        workflow_result = await core_medical.manage_surgery_workflow(
            case_id, workflow_stage, session, stage_data
        )
        
        return ApiResponse.success_response(
            data=workflow_result,
            message=f"Workflow updated to {workflow_stage}"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update workflow: {str(e)}"
        )


@router.get("/cases/{case_id}/workflow", response_model=ApiResponse[Dict[str, Any]])
async def get_workflow_status(
    case_id: str,
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Get current workflow status for a case"""
    
    try:
        result = await session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found"
            )
        
        workflow_status = {
            "case_id": str(case.id),
            "current_stage": case.workflow_stage or "pre_operative_assessment",
            "status": case.status,
            "created_at": case.created_at.isoformat(),
            "updated_at": case.updated_at.isoformat() if case.updated_at else None,
            "completion_percentage": core_medical._calculate_workflow_completion(
                case.workflow_stage or "pre_operative_assessment"
            )
        }
        
        return ApiResponse.success_response(
            data=workflow_status,
            message="Workflow status retrieved"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve workflow status: {str(e)}"
        )


# ========================================
# Impact Analysis Endpoints  
# ========================================

@router.post("/analysis/impact", response_model=ApiResponse[Dict[str, Any]])
async def analyze_clinical_impact(
    impact_request: Dict[str, Any],
    session: DatabaseSession,
    current_user: CurrentUser,
    timeframe_days: int = Query(30, description="Analysis timeframe in days")
):
    """Analyze impact of clinical interventions"""
    
    try:
        intervention_data = impact_request.get('intervention', {})
        patient_cohort = impact_request.get('patient_cohort', [])
        
        if not patient_cohort:
            raise ValueError("Patient cohort is required for impact analysis")
        
        impact_analysis = await core_medical.analyze_clinical_impact(
            intervention_data, patient_cohort, session, timeframe_days
        )
        
        return ApiResponse.success_response(
            data=impact_analysis,
            message="Impact analysis completed"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze impact: {str(e)}"
        )


# ========================================
# Reporting Endpoints
# ========================================

@router.get("/reports/patient/{patient_id}", response_model=ApiResponse[Dict[str, Any]])
async def generate_patient_report(
    patient_id: str,
    session: DatabaseSession,
    current_user: CurrentUser,
    report_type: str = Query("summary", description="Type of report to generate")
):
    """Generate patient report"""
    
    try:
        # Get patient data
        result = await session.execute(
            select(Patient)
            .options(
                selectinload(Patient.cases),
                selectinload(Patient.decisions)
            )
            .where(Patient.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient not found"
            )
        
        # Generate report based on type
        if report_type == "summary":
            report = MedicalReportGenerator.generate_patient_summary(patient.__dict__)
        else:
            raise ValueError(f"Unsupported report type: {report_type}")
        
        return ApiResponse.success_response(
            data=report,
            message=f"Patient {report_type} report generated"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/reports/decisions/{decision_id}", response_model=ApiResponse[Dict[str, Any]])
async def generate_decision_report(
    decision_id: str,
    session: DatabaseSession,
    current_user: CurrentUser
):
    """Generate decision report"""
    
    try:
        result = await session.execute(
            select(Decision).where(Decision.id == decision_id)
        )
        decision = result.scalar_one_or_none()
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Decision not found"
            )
        
        report = MedicalReportGenerator.generate_decision_report(decision.__dict__)
        
        return ApiResponse.success_response(
            data=report,
            message="Decision report generated"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate decision report: {str(e)}"
        )


# ========================================
# Utility Endpoints
# ========================================

@router.post("/validate", response_model=ApiResponse[Dict[str, Any]])
async def validate_medical_data(
    validation_request: Dict[str, Any],
    current_user: CurrentUser
):
    """Validate medical data before processing"""
    
    try:
        data = validation_request.get('data', {})
        validation_errors = validate_all_medical_data(data)
        
        validation_result = {
            "is_valid": len(validation_errors) == 0,
            "errors": validation_errors,
            "validated_at": datetime.utcnow().isoformat()
        }
        
        return ApiResponse.success_response(
            data=validation_result,
            message="Data validation completed"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


@router.get("/health", response_model=ApiResponse[Dict[str, Any]])
async def medical_module_health(current_user: CurrentUser):
    """Check health status of medical modules"""
    
    health_status = {
        "emr_status": "operational",
        "decision_engine_status": "operational", 
        "surgery_workflow_status": "operational",
        "impact_analyzer_status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
    
    return ApiResponse.success_response(
        data=health_status,
        message="All medical modules operational"
    )
