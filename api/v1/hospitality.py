"""
Hospitality API endpoints for YAZ Surgery Analytics Platform.
Handles patient experience, accommodation, and hospitality services.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.dependencies import get_current_user
from core.operators.specific_purpose.hospitality_operations import HospitalityOperationsOperator, ServiceTier, AccommodationType
from core.services.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
hospitality_operator = HospitalityOperationsOperator()


class HospitalityPlanRequest(BaseModel):
    patient_id: str
    name: str
    insurance_type: str = "standard"
    special_needs: List[str] = []
    mobility_assistance: bool = False
    dietary_restrictions: List[str] = []
    family_members: int = 0
    surgery_details: Dict[str, Any]


class PatientExperienceUpdate(BaseModel):
    feedback_type: str
    rating: float
    comments: str = ""
    requires_response: bool = False


class FamilyMember(BaseModel):
    name: str
    relationship: str
    age: Optional[int] = None
    special_needs: List[str] = []
    accommodation_needed: bool = True


class FamilyServicesRequest(BaseModel):
    patient_id: str
    family_members: List[FamilyMember]
    duration_days: int
    special_arrangements: List[str] = []


class DietaryRequirementsRequest(BaseModel):
    patient_id: str
    dietary_restrictions: List[str] = []
    allergies: List[str] = []
    cultural_preferences: List[str] = []
    surgery_type: str
    recovery_phase: str = "pre_surgery"


class TransportationRequest(BaseModel):
    patient_id: str
    pickup_location: str
    destination: str
    transport_type: str = "standard"
    accessibility_needs: List[str] = []
    scheduled_time: datetime
    return_trip_needed: bool = False


@router.post("/hospitality-plan/create")
async def create_hospitality_plan(
    request: HospitalityPlanRequest,
    current_user=Depends(get_current_user)
):
    """Create comprehensive hospitality plan for patient journey."""
    
    try:
        patient_data = {
            "patient_id": request.patient_id,
            "name": request.name,
            "insurance_type": request.insurance_type,
            "special_needs": request.special_needs,
            "mobility_assistance": request.mobility_assistance,
            "dietary_restrictions": request.dietary_restrictions,
            "family_members": request.family_members
        }
        
        hospitality_plan = hospitality_operator.create_patient_hospitality_plan(
            patient_data, 
            request.surgery_details
        )
        
        logger.info(f"Hospitality plan created for patient {request.patient_id}")
        
        return {
            "success": True,
            "plan_id": hospitality_plan["plan_id"],
            "hospitality_plan": hospitality_plan,
            "estimated_cost": hospitality_plan["cost_analysis"]["estimated_total"],
            "service_tier": hospitality_plan["service_tier"]
        }
        
    except Exception as e:
        logger.error(f"Error creating hospitality plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospitality-plan/{plan_id}")
async def get_hospitality_plan(
    plan_id: str,
    current_user=Depends(get_current_user)
):
    """Get hospitality plan details."""
    
    try:
        # In a full implementation, this would load from database
        plan = hospitality_operator._load_hospitality_plan(plan_id)
        
        return {
            "success": True,
            "plan": plan
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Hospitality plan {plan_id} not found")
    except Exception as e:
        logger.error(f"Error getting hospitality plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patient-experience/{plan_id}/update")
async def update_patient_experience(
    plan_id: str,
    experience_update: PatientExperienceUpdate,
    current_user=Depends(get_current_user)
):
    """Update patient experience with feedback and manage services."""
    
    try:
        feedback_data = {
            "feedback_type": experience_update.feedback_type,
            "rating": experience_update.rating,
            "comments": experience_update.comments,
            "timestamp": datetime.now().isoformat(),
            "reported_by": current_user.get("id", "unknown")
        }
        
        experience_report = hospitality_operator.manage_patient_experience(
            plan_id, 
            feedback_data
        )
        
        logger.info(f"Patient experience updated for plan {plan_id}")
        
        return {
            "success": True,
            "experience_report": experience_report,
            "satisfaction_score": experience_report["satisfaction_score"],
            "recommendations": experience_report["real_time_recommendations"],
            "escalation_needed": experience_report["escalation_required"]
        }
        
    except Exception as e:
        logger.error(f"Error updating patient experience: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/family-services/coordinate")
async def coordinate_family_services(
    request: FamilyServicesRequest,
    current_user=Depends(get_current_user)
):
    """Coordinate hospitality services for patient family members."""
    
    try:
        family_data = [
            {
                "name": member.name,
                "relationship": member.relationship,
                "age": member.age,
                "special_needs": member.special_needs,
                "accommodation_needed": member.accommodation_needed
            }
            for member in request.family_members
        ]
        
        family_coordination = hospitality_operator.coordinate_family_services(
            request.patient_id,
            family_data
        )
        
        logger.info(f"Family services coordinated for patient {request.patient_id}")
        
        return {
            "success": True,
            "coordination_id": family_coordination["coordination_id"],
            "family_coordination": family_coordination,
            "estimated_costs": family_coordination["estimated_costs"],
            "family_members_served": family_coordination["family_members"]
        }
        
    except Exception as e:
        logger.error(f"Error coordinating family services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dietary-services/manage")
async def manage_dietary_services(
    request: DietaryRequirementsRequest,
    current_user=Depends(get_current_user)
):
    """Manage specialized dietary services for surgery patients."""
    
    try:
        dietary_requirements = {
            "dietary_restrictions": request.dietary_restrictions,
            "allergies": request.allergies,
            "cultural_preferences": request.cultural_preferences,
            "surgery_type": request.surgery_type,
            "recovery_phase": request.recovery_phase
        }
        
        dietary_management = hospitality_operator.manage_dietary_services(
            request.patient_id,
            dietary_requirements
        )
        
        logger.info(f"Dietary services managed for patient {request.patient_id}")
        
        return {
            "success": True,
            "plan_id": dietary_management["plan_id"],
            "dietary_plan": dietary_management,
            "nutrition_consultation": dietary_management["nutrition_consultation"],
            "monitoring_schedule": dietary_management["monitoring_schedule"]
        }
        
    except Exception as e:
        logger.error(f"Error managing dietary services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transportation/coordinate")
async def coordinate_transportation(
    request: TransportationRequest,
    current_user=Depends(get_current_user)
):
    """Coordinate transportation services for patients and families."""
    
    try:
        transport_needs = {
            "pickup_location": request.pickup_location,
            "destination": request.destination,
            "transport_type": request.transport_type,
            "accessibility_needs": request.accessibility_needs,
            "scheduled_time": request.scheduled_time.isoformat(),
            "return_trip_needed": request.return_trip_needed
        }
        
        transportation_plan = hospitality_operator.coordinate_transportation(
            request.patient_id,
            transport_needs
        )
        
        logger.info(f"Transportation coordinated for patient {request.patient_id}")
        
        return {
            "success": True,
            "transport_id": transportation_plan["transport_id"],
            "transportation_plan": transportation_plan,
            "estimated_cost": transportation_plan["total_estimated_cost"],
            "insurance_coverage": transportation_plan["insurance_coverage"]
        }
        
    except Exception as e:
        logger.error(f"Error coordinating transportation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/accommodation/availability")
async def check_accommodation_availability(
    check_in_date: datetime,
    check_out_date: datetime,
    accommodation_type: AccommodationType = AccommodationType.STANDARD_ROOM,
    special_requirements: List[str] = [],
    current_user=Depends(get_current_user)
):
    """Check accommodation availability for specified dates."""
    
    try:
        # Get accommodation inventory
        inventory = hospitality_operator.accommodation_inventory
        
        # Simulate availability check
        availability_data = {
            "check_in_date": check_in_date.isoformat(),
            "check_out_date": check_out_date.isoformat(),
            "accommodation_type": accommodation_type.value,
            "special_requirements": special_requirements,
            "available_rooms": {
                "on_campus": {
                    "patient_hotel": {
                        "standard": 15,
                        "suite": 5,
                        "accessible": 2
                    },
                    "family_housing": {
                        "studio": 3,
                        "one_bedroom": 4,
                        "two_bedroom": 1
                    }
                },
                "partner_facilities": [
                    {
                        "name": "Medical Center Inn",
                        "available_rooms": 12,
                        "rate_per_night": 149.00,
                        "distance_miles": 0.5
                    },
                    {
                        "name": "Recovery Suites",
                        "available_rooms": 8,
                        "rate_per_night": 199.00,
                        "distance_miles": 1.2
                    }
                ]
            },
            "recommended_option": {
                "facility": "patient_hotel",
                "room_type": accommodation_type.value,
                "rate_per_night": 129.00,
                "amenities_included": ["wifi", "meal_service", "transportation"]
            }
        }
        
        return {
            "success": True,
            "availability": availability_data,
            "total_nights": (check_out_date - check_in_date).days,
            "booking_deadline": "48 hours before check-in"
        }
        
    except Exception as e:
        logger.error(f"Error checking accommodation availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/satisfaction-metrics")
async def get_satisfaction_metrics(
    timeframe_days: int = 30,
    service_area: Optional[str] = None,
    current_user=Depends(get_current_user)
):
    """Get patient satisfaction metrics across hospitality services."""
    
    try:
        satisfaction_report = hospitality_operator.track_satisfaction_metrics(timeframe_days)
        
        if service_area:
            # Filter metrics for specific service area
            filtered_metrics = satisfaction_report["service_area_metrics"].get(service_area, {})
            satisfaction_report["filtered_service_area"] = service_area
            satisfaction_report["filtered_metrics"] = filtered_metrics
        
        return {
            "success": True,
            "satisfaction_report": satisfaction_report,
            "timeframe_days": timeframe_days,
            "overall_satisfaction": satisfaction_report["overall_satisfaction"]
        }
        
    except Exception as e:
        logger.error(f"Error getting satisfaction metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-catalog")
async def get_service_catalog(
    service_tier: Optional[ServiceTier] = None,
    current_user=Depends(get_current_user)
):
    """Get available hospitality services catalog."""
    
    try:
        service_catalog = hospitality_operator.amenity_catalog
        
        if service_tier:
            # Filter catalog by service tier
            tier_amenities = service_catalog["room_amenities"].get(service_tier.value, [])
            filtered_catalog = {
                "service_tier": service_tier.value,
                "room_amenities": tier_amenities,
                "medical_support": service_catalog["medical_support"],
                "comfort_services": service_catalog["comfort_services"]
            }
        else:
            filtered_catalog = service_catalog
        
        return {
            "success": True,
            "service_catalog": filtered_catalog,
            "service_tiers_available": [tier.value for tier in ServiceTier],
            "accommodation_types_available": [acc_type.value for acc_type in AccommodationType]
        }
        
    except Exception as e:
        logger.error(f"Error getting service catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/concierge-request")
async def submit_concierge_request(
    patient_id: str,
    service_type: str,
    request_details: Dict[str, Any],
    priority: str = "normal",
    current_user=Depends(get_current_user)
):
    """Submit a request to concierge services."""
    
    try:
        # Create concierge request
        concierge_request = {
            "patient_id": patient_id,
            "service_type": service_type,
            "request_details": request_details,
            "priority": priority,
            "requested_by": current_user.get("id", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
        
        # In a full implementation, this would use the HospitalityConcierge class
        request_id = f"concierge_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        response = {
            "request_id": request_id,
            "status": "received",
            "estimated_completion": "2 hours",
            "assigned_staff": "hospitality_coordinator",
            "contact_info": {
                "phone": "+1-555-CONCIERGE",
                "email": "concierge@yaz-platform.com"
            }
        }
        
        logger.info(f"Concierge request submitted: {request_id}")
        
        return {
            "success": True,
            "concierge_response": response,
            "message": f"Your {service_type} request has been received and will be handled within 2 hours"
        }
        
    except Exception as e:
        logger.error(f"Error submitting concierge request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospitality-dashboard")
async def get_hospitality_dashboard(
    current_user=Depends(get_current_user)
):
    """Get hospitality services dashboard for administrators."""
    
    try:
        dashboard_data = {
            "overview": {
                "active_patients": 156,
                "average_satisfaction": 4.7,
                "occupancy_rate": 78.5,
                "service_requests_today": 23
            },
            "accommodation_metrics": {
                "total_rooms": 170,
                "occupied_rooms": 133,
                "available_rooms": 37,
                "average_length_stay": 4.2,
                "revenue_per_room": 167.50
            },
            "service_performance": {
                "concierge_response_time": "1.8 hours",
                "dietary_satisfaction": 4.6,
                "transportation_on_time": 94.2,
                "family_services_utilization": 67.8
            },
            "recent_feedback": [
                {
                    "patient_id": "P12345",
                    "service": "accommodation",
                    "rating": 5,
                    "comment": "Excellent room and very helpful staff"
                },
                {
                    "patient_id": "P12346",
                    "service": "dietary",
                    "rating": 4,
                    "comment": "Good meal options, would like more variety"
                }
            ],
            "financial_summary": {
                "daily_revenue": 28450.00,
                "monthly_revenue": 785600.00,
                "cost_per_patient": 245.30,
                "profit_margin": 18.7
            }
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting hospitality dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))
