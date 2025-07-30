"""
Surgery Operations Operator
Specialized operations for surgical procedures, OR management, and surgical workflows
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class SurgeryType(Enum):
    """Types of surgical procedures"""
    LAPAROSCOPIC = "laparoscopic"
    OPEN = "open"
    ROBOTIC = "robotic"
    ENDOSCOPIC = "endoscopic"
    MINIMALLY_INVASIVE = "minimally_invasive"


class SurgeryUrgency(Enum):
    """Surgery urgency levels"""
    ELECTIVE = "elective"
    URGENT = "urgent"
    EMERGENCY = "emergency"
    EMERGENT = "emergent"


class SurgeryStatus(Enum):
    """Surgery status types"""
    SCHEDULED = "scheduled"
    PREP = "prep"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    POSTPONED = "postponed"


class SurgeryOperationsOperator:
    """Specialized operations manager for surgical procedures"""
    
    def __init__(self):
        """Initialize surgery operations operator"""
        self.surgery_schedule = {}
        self.operating_rooms = {}
        self.surgical_equipment = {}
        self.surgical_teams = {}
        self.surgery_protocols = {}
        self.complications_log = {}
        logger.info("Surgery operations operator initialized")
    
    def schedule_surgery(self, surgery_data: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule a surgical procedure"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        surgery_id = core_ops.generate_operation_id("SURGERY")
        
        # Validate required fields
        required_fields = ["patient_id", "procedure_name", "surgeon_id", "scheduled_date"]
        validation = core_ops.validate_operation_data(surgery_data, required_fields)
        
        if not validation["is_valid"]:
            raise ValueError(f"Invalid surgery data: {validation['errors']}")
        
        surgery = {
            "surgery_id": surgery_id,
            "patient_id": surgery_data["patient_id"],
            "case_id": surgery_data.get("case_id"),
            "procedure_name": surgery_data["procedure_name"],
            "procedure_code": surgery_data.get("procedure_code"),
            "surgery_type": surgery_data.get("surgery_type", SurgeryType.OPEN.value),
            "urgency": surgery_data.get("urgency", SurgeryUrgency.ELECTIVE.value),
            "surgeon_id": surgery_data["surgeon_id"],
            "assistant_surgeons": surgery_data.get("assistant_surgeons", []),
            "anesthesiologist_id": surgery_data.get("anesthesiologist_id"),
            "scheduled_date": surgery_data["scheduled_date"],
            "estimated_duration_minutes": surgery_data.get("estimated_duration", 120),
            "operating_room": surgery_data.get("operating_room"),
            "equipment_requirements": surgery_data.get("equipment_requirements", []),
            "special_instructions": surgery_data.get("special_instructions", ""),
            "pre_op_requirements": surgery_data.get("pre_op_requirements", []),
            "status": SurgeryStatus.SCHEDULED.value,
            "created_at": datetime.now().isoformat(),
            "created_by": surgery_data.get("user_id"),
            "last_updated": datetime.now().isoformat()
        }
        
        self.surgery_schedule[surgery_id] = surgery
        
        # Reserve operating room
        if surgery["operating_room"]:
            self._reserve_operating_room(surgery["operating_room"], surgery_data["scheduled_date"], 
                                       surgery["estimated_duration_minutes"])
        
        # Log the operation
        core_ops.log_operation("surgery_scheduled", {
            "user_id": surgery_data.get("user_id"),
            "data": {
                "surgery_id": surgery_id,
                "patient_id": surgery_data["patient_id"],
                "procedure": surgery_data["procedure_name"]
            }
        })
        
        logger.info(f"Surgery scheduled: {surgery_id} - {surgery['procedure_name']}")
        return surgery
    
    def start_surgery(self, surgery_id: str, start_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mark surgery as started"""
        if surgery_id not in self.surgery_schedule:
            raise ValueError(f"Surgery {surgery_id} not found")
        
        surgery = self.surgery_schedule[surgery_id]
        
        if surgery["status"] != SurgeryStatus.SCHEDULED.value:
            raise ValueError(f"Cannot start surgery with status: {surgery['status']}")
        
        surgery.update({
            "status": SurgeryStatus.IN_PROGRESS.value,
            "actual_start_time": datetime.now().isoformat(),
            "surgical_team_present": start_data.get("team_present", []),
            "anesthesia_start_time": start_data.get("anesthesia_start"),
            "incision_time": start_data.get("incision_time"),
            "last_updated": datetime.now().isoformat()
        })
        
        logger.info(f"Surgery started: {surgery_id}")
        return surgery
    
    def complete_surgery(self, surgery_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mark surgery as completed"""
        if surgery_id not in self.surgery_schedule:
            raise ValueError(f"Surgery {surgery_id} not found")
        
        surgery = self.surgery_schedule[surgery_id]
        
        if surgery["status"] != SurgeryStatus.IN_PROGRESS.value:
            raise ValueError(f"Cannot complete surgery with status: {surgery['status']}")
        
        end_time = datetime.now()
        start_time = datetime.fromisoformat(surgery.get("actual_start_time", surgery["created_at"]))
        actual_duration = (end_time - start_time).total_seconds() / 60  # minutes
        
        surgery.update({
            "status": SurgeryStatus.COMPLETED.value,
            "actual_end_time": end_time.isoformat(),
            "actual_duration_minutes": round(actual_duration, 2),
            "procedure_outcome": completion_data.get("outcome", "successful"),
            "complications": completion_data.get("complications", []),
            "blood_loss_ml": completion_data.get("blood_loss"),
            "specimens_collected": completion_data.get("specimens", []),
            "implants_used": completion_data.get("implants", []),
            "closure_method": completion_data.get("closure_method"),
            "post_op_instructions": completion_data.get("post_op_instructions", ""),
            "recovery_room_time": completion_data.get("recovery_start"),
            "surgeon_notes": completion_data.get("surgeon_notes", ""),
            "last_updated": datetime.now().isoformat()
        })
        
        # Log complications if any
        if completion_data.get("complications"):
            self._log_complications(surgery_id, completion_data["complications"])
        
        # Release operating room
        if surgery.get("operating_room"):
            self._release_operating_room(surgery["operating_room"], end_time.isoformat())
        
        logger.info(f"Surgery completed: {surgery_id} - Duration: {actual_duration:.1f} minutes")
        return surgery
    
    def _log_complications(self, surgery_id: str, complications: List[Dict[str, Any]]) -> None:
        """Log surgical complications"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        for complication in complications:
            complication_id = core_ops.generate_operation_id("COMPLICATION")
            
            complication_record = {
                "complication_id": complication_id,
                "surgery_id": surgery_id,
                "type": complication.get("type"),
                "description": complication.get("description"),
                "severity": complication.get("severity", "minor"),  # minor, moderate, major, critical
                "detected_at": complication.get("detected_at", datetime.now().isoformat()),
                "resolution": complication.get("resolution"),
                "outcome": complication.get("outcome"),
                "reported_by": complication.get("reported_by"),
                "logged_at": datetime.now().isoformat()
            }
            
            self.complications_log[complication_id] = complication_record
            logger.warning(f"Surgical complication logged: {complication_id} for surgery {surgery_id}")
    
    def create_surgical_team(self, team_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create surgical team configuration"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        team_id = core_ops.generate_operation_id("SURGTEAM")
        
        surgical_team = {
            "team_id": team_id,
            "name": team_data["name"],
            "lead_surgeon_id": team_data["lead_surgeon_id"],
            "assistant_surgeons": team_data.get("assistant_surgeons", []),
            "anesthesiologist_id": team_data.get("anesthesiologist_id"),
            "circulating_nurse_id": team_data.get("circulating_nurse_id"),
            "scrub_nurse_id": team_data.get("scrub_nurse_id"),
            "technicians": team_data.get("technicians", []),
            "specialties": team_data.get("specialties", []),
            "certifications": team_data.get("certifications", []),
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        self.surgical_teams[team_id] = surgical_team
        logger.info(f"Surgical team created: {team_data['name']} ({team_id})")
        return surgical_team
    
    def manage_operating_room(self, room_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manage operating room configuration and availability"""
        from ..general_purpose.core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        room_id = room_data.get("room_id") or core_ops.generate_operation_id("OR")
        
        operating_room = {
            "room_id": room_id,
            "room_number": room_data["room_number"],
            "room_type": room_data.get("room_type", "general"),  # general, cardiac, neuro, etc.
            "equipment_available": room_data.get("equipment", []),
            "capacity": room_data.get("capacity", 8),  # max people
            "sterile_processing_time_minutes": room_data.get("sterile_time", 30),
            "status": room_data.get("status", "available"),  # available, occupied, maintenance, cleaning
            "schedule": room_data.get("schedule", {}),
            "maintenance_schedule": room_data.get("maintenance", []),
            "last_updated": datetime.now().isoformat()
        }
        
        self.operating_rooms[room_id] = operating_room
        logger.info(f"Operating room managed: {room_data['room_number']} ({room_id})")
        return operating_room
    
    def _reserve_operating_room(self, room_id: str, scheduled_date: str, duration_minutes: int) -> None:
        """Reserve operating room for surgery"""
        if room_id in self.operating_rooms:
            room = self.operating_rooms[room_id]
            if "reservations" not in room:
                room["reservations"] = []
            
            room["reservations"].append({
                "start_time": scheduled_date,
                "duration_minutes": duration_minutes,
                "reserved_at": datetime.now().isoformat()
            })
    
    def _release_operating_room(self, room_id: str, completion_time: str) -> None:
        """Release operating room after surgery completion"""
        if room_id in self.operating_rooms:
            room = self.operating_rooms[room_id]
            room["status"] = "cleaning"
            room["last_surgery_completed"] = completion_time
    
    def get_surgery_schedule(self, date_range: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """Get surgery schedule for date range"""
        surgeries = list(self.surgery_schedule.values())
        
        if date_range:
            start_date = datetime.fromisoformat(date_range.get("start_date", "1900-01-01T00:00:00"))
            end_date = datetime.fromisoformat(date_range.get("end_date", "2100-12-31T23:59:59"))
            
            surgeries = [
                surgery for surgery in surgeries
                if start_date <= datetime.fromisoformat(surgery["scheduled_date"]) <= end_date
            ]
        
        # Sort by scheduled date
        surgeries.sort(key=lambda x: x["scheduled_date"])
        return surgeries
    
    def get_surgical_metrics(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get surgical performance metrics"""
        if time_period is None:
            time_period = timedelta(days=30)
        
        cutoff_date = datetime.now() - time_period
        
        # Filter surgeries within time period
        period_surgeries = [
            surgery for surgery in self.surgery_schedule.values()
            if datetime.fromisoformat(surgery["created_at"]) >= cutoff_date
        ]
        
        total_surgeries = len(period_surgeries)
        completed_surgeries = len([s for s in period_surgeries if s["status"] == SurgeryStatus.COMPLETED.value])
        cancelled_surgeries = len([s for s in period_surgeries if s["status"] == SurgeryStatus.CANCELLED.value])
        
        # Calculate average duration for completed surgeries
        completed_with_duration = [
            s for s in period_surgeries 
            if s["status"] == SurgeryStatus.COMPLETED.value and s.get("actual_duration_minutes")
        ]
        
        avg_duration = 0
        if completed_with_duration:
            avg_duration = sum(s["actual_duration_minutes"] for s in completed_with_duration) / len(completed_with_duration)
        
        # Count complications
        period_complications = [
            comp for comp in self.complications_log.values()
            if datetime.fromisoformat(comp["logged_at"]) >= cutoff_date
        ]
        
        complication_rate = (len(period_complications) / completed_surgeries * 100) if completed_surgeries > 0 else 0
        
        # Surgery types breakdown
        surgery_types = {}
        for surgery in period_surgeries:
            surgery_type = surgery.get("surgery_type", "unknown")
            surgery_types[surgery_type] = surgery_types.get(surgery_type, 0) + 1
        
        return {
            "period_days": time_period.days,
            "total_surgeries": total_surgeries,
            "completed_surgeries": completed_surgeries,
            "cancelled_surgeries": cancelled_surgeries,
            "completion_rate_percent": round((completed_surgeries / total_surgeries * 100) if total_surgeries > 0 else 100, 2),
            "average_duration_minutes": round(avg_duration, 2),
            "total_complications": len(period_complications),
            "complication_rate_percent": round(complication_rate, 2),
            "surgery_types_breakdown": surgery_types,
            "generated_at": datetime.now().isoformat()
        }
