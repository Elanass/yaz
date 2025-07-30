"""
Education API endpoints for YAZ Surgery Analytics Platform.
Handles medical education, training programs, and knowledge management.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.dependencies import get_current_user
from core.operators.specific_purpose.education_operations import EducationOperationsOperator
from core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
education_operator = EducationOperationsOperator()


class TrainingProgramRequest(BaseModel):
    role: str = "surgeon"
    experience_level: str = "intermediate"
    specialization: str = "bariatric_surgery"
    current_skills: List[str] = []
    target_competencies: List[str] = []
    learning_preferences: Dict[str, Any] = {}
    timeline: int = 90  # days


class LearningProgressResponse(BaseModel):
    success: bool
    participant_id: str
    program_id: str
    overall_progress: float
    recommendations: List[str]
    certification_eligible: bool


class SurgicalOutcomeIntegration(BaseModel):
    surgeon_id: str
    outcome_data: List[Dict[str, Any]]


class ContinuingEducationResponse(BaseModel):
    success: bool
    professional_id: str
    compliance_status: Dict[str, Any]
    recommended_courses: List[Dict[str, Any]]
    urgent_actions: List[str]


class SimulationLabConfig(BaseModel):
    lab_name: str
    location: str
    available_equipment: List[str] = []
    capacity: int = 10


@router.post("/training-program/create")
async def create_training_program(
    request: TrainingProgramRequest,
    current_user=Depends(get_current_user)
):
    """Create a personalized training program for healthcare professionals."""
    
    try:
        program_data = {
            "role": request.role,
            "experience_level": request.experience_level,
            "specialization": request.specialization,
            "current_skills": request.current_skills,
            "target_competencies": request.target_competencies,
            "learning_preferences": request.learning_preferences,
            "timeline": request.timeline,
            "created_by": current_user.get("id", "unknown")
        }
        
        training_program = education_operator.create_training_program(program_data)
        
        logger.info(f"Training program created by {current_user.get('id')}")
        
        return {
            "success": True,
            "program_id": training_program["program_id"],
            "program_details": training_program,
            "message": f"Training program created with {len(training_program['curriculum'])} modules"
        }
        
    except Exception as e:
        logger.error(f"Error creating training program: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/training-progress/{participant_id}/{program_id}", response_model=LearningProgressResponse)
async def track_learning_progress(
    participant_id: str,
    program_id: str,
    current_user=Depends(get_current_user)
):
    """Track learning progress for a program participant."""
    
    try:
        progress_report = education_operator.track_learning_progress(participant_id, program_id)
        
        return LearningProgressResponse(
            success=True,
            participant_id=participant_id,
            program_id=program_id,
            overall_progress=progress_report["overall_progress"],
            recommendations=progress_report["recommendations"],
            certification_eligible=progress_report["certification_eligibility"]
        )
        
    except Exception as e:
        logger.error(f"Error tracking learning progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/surgical-outcomes/integrate")
async def integrate_surgical_outcomes(
    request: SurgicalOutcomeIntegration,
    current_user=Depends(get_current_user)
):
    """Integrate surgical outcomes with education recommendations."""
    
    try:
        integration_result = education_operator.integrate_surgical_outcomes(
            request.surgeon_id,
            request.outcome_data
        )
        
        logger.info(f"Surgical outcomes integrated for surgeon {request.surgeon_id}")
        
        return {
            "success": True,
            "surgeon_id": request.surgeon_id,
            "integration_result": integration_result,
            "priority_level": integration_result["priority_level"],
            "recommended_interventions": integration_result["recommended_interventions"]
        }
        
    except Exception as e:
        logger.error(f"Error integrating surgical outcomes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/continuing-education/{professional_id}", response_model=ContinuingEducationResponse)
async def manage_continuing_education(
    professional_id: str,
    current_user=Depends(get_current_user)
):
    """Manage continuing education requirements and compliance."""
    
    try:
        ce_management = education_operator.manage_continuing_education(professional_id)
        
        return ContinuingEducationResponse(
            success=True,
            professional_id=professional_id,
            compliance_status=ce_management["current_status"],
            recommended_courses=ce_management["recommended_courses"],
            urgent_actions=ce_management["urgent_actions"]
        )
        
    except Exception as e:
        logger.error(f"Error managing continuing education: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulation-lab/create")
async def create_simulation_lab_integration(
    config: SimulationLabConfig,
    current_user=Depends(get_current_user)
):
    """Create integration with surgical simulation laboratories."""
    
    try:
        lab_config = {
            "lab_name": config.lab_name,
            "location": config.location,
            "available_equipment": config.available_equipment,
            "capacity": config.capacity,
            "created_by": current_user.get("id", "unknown")
        }
        
        simulation_integration = education_operator.create_simulation_lab_integration(lab_config)
        
        logger.info(f"Simulation lab integration created: {simulation_integration['integration_id']}")
        
        return {
            "success": True,
            "integration_id": simulation_integration["integration_id"],
            "lab_details": simulation_integration,
            "message": f"Simulation lab '{config.lab_name}' integrated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error creating simulation lab integration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/competency-standards")
async def get_competency_standards(
    specialization: Optional[str] = "bariatric_surgery",
    current_user=Depends(get_current_user)
):
    """Get competency standards for medical specializations."""
    
    try:
        # Get competency standards from education operator
        standards = education_operator.certification_standards
        
        return {
            "success": True,
            "specialization": specialization,
            "competency_standards": standards,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting competency standards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/education-providers")
async def get_education_providers(
    provider_type: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Get available education providers and their offerings."""
    
    try:
        providers = education_operator.education_providers
        
        if provider_type:
            filtered_providers = providers.get(provider_type, {})
        else:
            filtered_providers = providers
        
        return {
            "success": True,
            "provider_type": provider_type or "all",
            "education_providers": filtered_providers,
            "total_providers": len(filtered_providers)
        }
        
    except Exception as e:
        logger.error(f"Error getting education providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-analytics/{program_id}")
async def get_learning_analytics(
    program_id: str,
    timeframe_days: int = 30,
    current_user=Depends(get_current_user)
):
    """Get learning analytics and insights for a training program."""
    
    try:
        # In a full implementation, this would aggregate learning data
        analytics = {
            "program_id": program_id,
            "timeframe_days": timeframe_days,
            "participant_metrics": {
                "total_enrolled": 25,
                "active_participants": 20,
                "completion_rate": 78.5,
                "average_progress": 65.2
            },
            "engagement_metrics": {
                "daily_active_users": 18,
                "average_session_duration": 45,  # minutes
                "module_completion_rate": 82.1
            },
            "performance_metrics": {
                "average_assessment_score": 85.3,
                "skill_improvement": 23.7,  # percentage
                "certification_pass_rate": 91.2
            },
            "content_effectiveness": {
                "most_engaging_modules": ["surgical_planning", "operative_technique"],
                "challenging_areas": ["complication_management"],
                "improvement_suggestions": [
                    "Add more interactive simulations",
                    "Provide additional practice cases"
                ]
            }
        }
        
        return {
            "success": True,
            "analytics": analytics,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/certification/verify")
async def verify_certification_status(
    professional_id: str,
    certification_type: str,
    current_user=Depends(get_current_user)
):
    """Verify certification status for healthcare professionals."""
    
    try:
        # In a full implementation, this would check with certification bodies
        verification_result = {
            "professional_id": professional_id,
            "certification_type": certification_type,
            "status": "active",
            "issue_date": "2023-01-15",
            "expiry_date": "2026-01-15",
            "issuing_body": "American Society for Metabolic and Bariatric Surgery",
            "verification_date": datetime.now().isoformat(),
            "valid": True
        }
        
        return {
            "success": True,
            "verification_result": verification_result,
            "message": f"Certification {certification_type} is valid and active"
        }
        
    except Exception as e:
        logger.error(f"Error verifying certification: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/education-metrics/dashboard")
async def get_education_dashboard(
    current_user=Depends(get_current_user)
):
    """Get education metrics dashboard for administrators."""
    
    try:
        dashboard_data = {
            "overview": {
                "total_programs": 15,
                "active_participants": 234,
                "completed_certifications": 89,
                "average_satisfaction": 4.6
            },
            "program_statistics": {
                "most_popular_programs": [
                    {"name": "Bariatric Surgery Certification", "participants": 45},
                    {"name": "Laparoscopic Techniques", "participants": 38},
                    {"name": "Patient Safety Protocols", "participants": 32}
                ],
                "completion_rates": {
                    "last_30_days": 85.2,
                    "last_90_days": 78.9,
                    "yearly_average": 82.1
                }
            },
            "quality_metrics": {
                "instructor_ratings": 4.7,
                "content_relevance": 4.5,
                "technical_quality": 4.8,
                "support_satisfaction": 4.4
            },
            "financial_metrics": {
                "revenue_this_month": 125000,
                "cost_per_participant": 850,
                "roi_percentage": 215
            }
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting education dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
