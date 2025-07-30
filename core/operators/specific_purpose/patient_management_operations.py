"""
Patient Management Operations Operator
Specialized operations for patient registration, demographics, and care coordination
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class PatientStatus(Enum):
    """Patient status types"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCHARGED = "discharged"
    DECEASED = "deceased"
    TRANSFERRED = "transferred"


class PatientPriority(Enum):
    """Patient priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class PatientManagementOperationsOperator:
    """Specialized operations manager for patient management"""
    
    def __init__(self):
        """Initialize patient management operations operator"""
        self.patients = {}
        self.patient_visits = {}
        self.care_plans = {}
        self.patient_alerts = {}
        self.emergency_contacts = {}
        logger.info("Patient management operations operator initialized")
    
    def register_patient(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new patient in the system"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        patient_id = core_ops.generate_operation_id("PATIENT")
        
        # Validate required fields
        required_fields = ["first_name", "last_name", "date_of_birth"]
        validation = core_ops.validate_operation_data(patient_data, required_fields)
        
        if not validation["is_valid"]:
            raise ValueError(f"Invalid patient data: {validation['errors']}")
        
        patient = {
            "patient_id": patient_id,
            "medical_record_number": patient_data.get("mrn") or f"MRN-{patient_id[-8:]}",
            "first_name": patient_data["first_name"],
            "last_name": patient_data["last_name"],
            "middle_name": patient_data.get("middle_name", ""),
            "date_of_birth": patient_data["date_of_birth"],
            "gender": patient_data.get("gender"),
            "address": patient_data.get("address", {}),
            "phone_numbers": patient_data.get("phone_numbers", []),
            "email": patient_data.get("email"),
            "emergency_contacts": patient_data.get("emergency_contacts", []),
            "insurance_information": patient_data.get("insurance", []),
            "primary_language": patient_data.get("primary_language", "English"),
            "preferred_communication": patient_data.get("preferred_communication", "phone"),
            "allergies": patient_data.get("allergies", []),
            "medical_conditions": patient_data.get("conditions", []),
            "medications": patient_data.get("medications", []),
            "status": PatientStatus.ACTIVE.value,
            "priority": patient_data.get("priority", PatientPriority.NORMAL.value),
            "registration_date": datetime.now().isoformat(),
            "registered_by": patient_data.get("user_id"),
            "last_updated": datetime.now().isoformat(),
            "notes": patient_data.get("notes", "")
        }
        
        self.patients[patient_id] = patient
        
        # Store emergency contacts separately for quick access
        for contact in patient_data.get("emergency_contacts", []):
            contact_id = core_ops.generate_operation_id("CONTACT")
            self.emergency_contacts[contact_id] = {
                "contact_id": contact_id,
                "patient_id": patient_id,
                **contact
            }
        
        # Log the operation
        core_ops.log_operation("patient_registered", {
            "user_id": patient_data.get("user_id"),
            "data": {
                "patient_id": patient_id,
                "mrn": patient["medical_record_number"],
                "name": f"{patient['first_name']} {patient['last_name']}"
            }
        })
        
        logger.info(f"Patient registered: {patient_id} - {patient['first_name']} {patient['last_name']}")
        return patient
    
    def update_patient(self, patient_id: str, update_data: Dict[str, Any], 
                      updated_by: str) -> Dict[str, Any]:
        """Update patient information"""
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")
        
        patient = self.patients[patient_id]
        
        # Track changes for audit
        changes = {}
        for field, new_value in update_data.items():
            if field in patient and patient[field] != new_value:
                changes[field] = {"old": patient[field], "new": new_value}
                patient[field] = new_value
        
        patient["last_updated"] = datetime.now().isoformat()
        patient["last_updated_by"] = updated_by
        
        # Create audit entry
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        core_ops.create_audit_entry(
            entity_type="patient",
            entity_id=patient_id,
            action="UPDATE",
            changes=changes,
            user_id=updated_by
        )
        
        logger.info(f"Patient updated: {patient_id} - {len(changes)} fields changed")
        return patient
    
    def create_visit(self, visit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new patient visit record"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        visit_id = core_ops.generate_operation_id("VISIT")
        
        if visit_data["patient_id"] not in self.patients:
            raise ValueError(f"Patient {visit_data['patient_id']} not found")
        
        visit = {
            "visit_id": visit_id,
            "patient_id": visit_data["patient_id"],
            "visit_type": visit_data.get("visit_type", "outpatient"),
            "department": visit_data.get("department"),
            "provider_id": visit_data.get("provider_id"),
            "chief_complaint": visit_data.get("chief_complaint", ""),
            "visit_date": visit_data.get("visit_date", datetime.now().isoformat()),
            "check_in_time": visit_data.get("check_in_time"),
            "check_out_time": visit_data.get("check_out_time"),
            "status": visit_data.get("status", "scheduled"),
            "diagnosis_codes": visit_data.get("diagnosis_codes", []),
            "procedure_codes": visit_data.get("procedure_codes", []),
            "visit_notes": visit_data.get("notes", ""),
            "created_at": datetime.now().isoformat(),
            "created_by": visit_data.get("user_id")
        }
        
        self.patient_visits[visit_id] = visit
        
        logger.info(f"Patient visit created: {visit_id} for patient {visit_data['patient_id']}")
        return visit
    
    def create_care_plan(self, care_plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create care plan for patient"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        plan_id = core_ops.generate_operation_id("CAREPLAN")
        
        if care_plan_data["patient_id"] not in self.patients:
            raise ValueError(f"Patient {care_plan_data['patient_id']} not found")
        
        care_plan = {
            "plan_id": plan_id,
            "patient_id": care_plan_data["patient_id"],
            "plan_name": care_plan_data["plan_name"],
            "diagnosis": care_plan_data.get("diagnosis"),
            "goals": care_plan_data.get("goals", []),
            "interventions": care_plan_data.get("interventions", []),
            "medications": care_plan_data.get("medications", []),
            "appointments": care_plan_data.get("appointments", []),
            "monitoring_parameters": care_plan_data.get("monitoring", []),
            "care_team": care_plan_data.get("care_team", []),
            "start_date": care_plan_data.get("start_date", datetime.now().isoformat()),
            "end_date": care_plan_data.get("end_date"),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "created_by": care_plan_data.get("user_id"),
            "last_reviewed": datetime.now().isoformat()
        }
        
        self.care_plans[plan_id] = care_plan
        
        logger.info(f"Care plan created: {plan_id} for patient {care_plan_data['patient_id']}")
        return care_plan
    
    def create_patient_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create patient-specific alert"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        alert_id = core_ops.generate_operation_id("PTALERT")
        
        if alert_data["patient_id"] not in self.patients:
            raise ValueError(f"Patient {alert_data['patient_id']} not found")
        
        alert = {
            "alert_id": alert_id,
            "patient_id": alert_data["patient_id"],
            "alert_type": alert_data["alert_type"],  # allergy, condition, medication, etc.
            "severity": alert_data.get("severity", "medium"),
            "title": alert_data["title"],
            "description": alert_data.get("description", ""),
            "expiry_date": alert_data.get("expiry_date"),
            "active": True,
            "created_at": datetime.now().isoformat(),
            "created_by": alert_data.get("user_id")
        }
        
        self.patient_alerts[alert_id] = alert
        
        logger.info(f"Patient alert created: {alert_id} for patient {alert_data['patient_id']}")
        return alert
    
    def search_patients(self, search_criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search for patients based on criteria"""
        results = []
        
        for patient in self.patients.values():
            match = True
            
            # Check name match
            if search_criteria.get("name"):
                name_search = search_criteria["name"].lower()
                full_name = f"{patient['first_name']} {patient['last_name']}".lower()
                if name_search not in full_name:
                    match = False
            
            # Check MRN match
            if search_criteria.get("mrn"):
                if search_criteria["mrn"] != patient["medical_record_number"]:
                    match = False
            
            # Check date of birth match
            if search_criteria.get("date_of_birth"):
                if search_criteria["date_of_birth"] != patient["date_of_birth"]:
                    match = False
            
            # Check status match
            if search_criteria.get("status"):
                if search_criteria["status"] != patient["status"]:
                    match = False
            
            if match:
                results.append(patient)
        
        return results
    
    def get_patient_summary(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive patient summary"""
        if patient_id not in self.patients:
            raise ValueError(f"Patient {patient_id} not found")
        
        patient = self.patients[patient_id]
        
        # Get recent visits
        recent_visits = [
            visit for visit in self.patient_visits.values()
            if visit["patient_id"] == patient_id
        ]
        recent_visits.sort(key=lambda x: x["visit_date"], reverse=True)
        
        # Get active care plans
        active_care_plans = [
            plan for plan in self.care_plans.values()
            if plan["patient_id"] == patient_id and plan["status"] == "active"
        ]
        
        # Get active alerts
        active_alerts = [
            alert for alert in self.patient_alerts.values()
            if alert["patient_id"] == patient_id and alert["active"]
        ]
        
        return {
            "patient": patient,
            "recent_visits": recent_visits[:5],  # Last 5 visits
            "active_care_plans": active_care_plans,
            "active_alerts": active_alerts,
            "total_visits": len(recent_visits),
            "summary_generated_at": datetime.now().isoformat()
        }
    
    def get_patient_statistics(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get patient management statistics"""
        if time_period is None:
            time_period = timedelta(days=30)
        
        cutoff_date = datetime.now() - time_period
        
        # Count new registrations
        new_registrations = [
            patient for patient in self.patients.values()
            if datetime.fromisoformat(patient["registration_date"]) >= cutoff_date
        ]
        
        # Count visits in period
        period_visits = [
            visit for visit in self.patient_visits.values()
            if datetime.fromisoformat(visit["created_at"]) >= cutoff_date
        ]
        
        # Patient status breakdown
        status_breakdown = {}
        for patient in self.patients.values():
            status = patient["status"]
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        
        # Priority breakdown
        priority_breakdown = {}
        for patient in self.patients.values():
            priority = patient["priority"]
            priority_breakdown[priority] = priority_breakdown.get(priority, 0) + 1
        
        return {
            "period_days": time_period.days,
            "total_patients": len(self.patients),
            "new_registrations": len(new_registrations),
            "total_visits": len(period_visits),
            "active_care_plans": len([p for p in self.care_plans.values() if p["status"] == "active"]),
            "active_alerts": len([a for a in self.patient_alerts.values() if a["active"]]),
            "patient_status_breakdown": status_breakdown,
            "patient_priority_breakdown": priority_breakdown,
            "generated_at": datetime.now().isoformat()
        }
