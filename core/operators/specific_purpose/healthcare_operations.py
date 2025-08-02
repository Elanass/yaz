"""
Healthcare Operations Manager
Handles healthcare-specific operations including surgery, patient management, and clinical workflows
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from core.models.base import BaseEntity
from core.services.logger import get_logger

logger = get_logger(__name__)


class HealthcareOperationsOperator:
    """Operations manager for healthcare domain"""
    
    def __init__(self):
        self.active_cases = {}
        self.surgery_queue = []
        logger.info("Healthcare operator initialized")
    
    def create_surgical_case(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new surgical case"""
        case_id = f"SURG-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        case = {
            "case_id": case_id,
            "patient_id": patient_data.get("patient_id"),
            "procedure": patient_data.get("procedure", "Gastric Resection"),
            "urgency": patient_data.get("urgency", "routine"),
            "surgeon": patient_data.get("surgeon"),
            "created_at": datetime.now().isoformat(),
            "status": "scheduled"
        }
        
        self.active_cases[case_id] = case
        self.surgery_queue.append(case_id)
        
        logger.info(f"Created surgical case: {case_id}")
        return case
    
    def schedule_surgery(self, case_id: str, surgery_date: str) -> Dict[str, Any]:
        """Schedule surgery for a case"""
        if case_id not in self.active_cases:
            raise ValueError(f"Case {case_id} not found")
        
        self.active_cases[case_id]["surgery_date"] = surgery_date
        self.active_cases[case_id]["status"] = "scheduled"
        
        return self.active_cases[case_id]
    
    def get_surgery_queue(self) -> List[Dict[str, Any]]:
        """Get current surgery queue"""
        return [self.active_cases[case_id] for case_id in self.surgery_queue]
    
    def update_case_status(self, case_id: str, status: str, notes: str = "") -> Dict[str, Any]:
        """Update case status"""
        if case_id not in self.active_cases:
            raise ValueError(f"Case {case_id} not found")
        
        self.active_cases[case_id]["status"] = status
        self.active_cases[case_id]["last_updated"] = datetime.now().isoformat()
        
        if notes:
            self.active_cases[case_id]["notes"] = notes
        
        logger.info(f"Updated case {case_id} status to {status}")
        return self.active_cases[case_id]
