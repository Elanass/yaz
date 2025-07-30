"""
Communication Operations Operator
Handles internal and external communications, notifications, and messaging
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class CommunicationType(Enum):
    """Types of communications"""
    EMAIL = "email"
    SMS = "sms"
    PUSH_NOTIFICATION = "push_notification"
    IN_APP_MESSAGE = "in_app_message"
    PHONE_CALL = "phone_call"
    VIDEO_CONFERENCE = "video_conference"
    INTERNAL_MEMO = "internal_memo"
    EXTERNAL_COMMUNICATION = "external_communication"


class CommunicationPriority(Enum):
    """Communication priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class CommunicationOperationsOperator:
    """Communication operations manager for all types of messaging and notifications"""
    
    def __init__(self):
        """Initialize communication operations operator"""
        self.communications_log = {}
        self.notification_templates = {}
        self.communication_channels = {}
        self.delivery_status = {}
        logger.info("Communication operations operator initialized")
    
    def send_communication(self, communication_data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a communication through specified channel"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        comm_id = core_ops.generate_operation_id("COMM")
        
        # Validate required fields
        required_fields = ["recipient", "message", "communication_type"]
        validation = core_ops.validate_operation_data(communication_data, required_fields)
        
        if not validation["is_valid"]:
            raise ValueError(f"Invalid communication data: {validation['errors']}")
        
        communication = {
            "communication_id": comm_id,
            "recipient": communication_data["recipient"],
            "sender": communication_data.get("sender", "system"),
            "communication_type": communication_data["communication_type"],
            "priority": communication_data.get("priority", CommunicationPriority.NORMAL.value),
            "subject": communication_data.get("subject", ""),
            "message": communication_data["message"],
            "attachments": communication_data.get("attachments", []),
            "metadata": communication_data.get("metadata", {}),
            "reference_id": communication_data.get("reference_id"),
            "reference_type": communication_data.get("reference_type"),
            "scheduled_time": communication_data.get("scheduled_time"),
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "created_by": communication_data.get("user_id")
        }
        
        # Store communication
        self.communications_log[comm_id] = communication
        
        # Attempt to deliver communication
        delivery_result = self._deliver_communication(communication)
        communication.update(delivery_result)
        
        # Log the operation
        core_ops.log_operation("communication_sent", {
            "user_id": communication_data.get("user_id"),
            "data": {
                "communication_id": comm_id,
                "type": communication_data["communication_type"],
                "recipient": communication_data["recipient"]
            }
        })
        
        logger.info(f"Sent communication: {comm_id} to {communication['recipient']}")
        return communication
    
    def _deliver_communication(self, communication: Dict[str, Any]) -> Dict[str, Any]:
        """Deliver communication through appropriate channel"""
        comm_type = communication["communication_type"]
        
        delivery_result = {
            "delivery_attempted_at": datetime.now().isoformat(),
            "delivery_method": comm_type,
            "delivery_status": "pending"
        }
        
        try:
            if comm_type == CommunicationType.EMAIL.value:
                delivery_result.update(self._send_email(communication))
            elif comm_type == CommunicationType.SMS.value:
                delivery_result.update(self._send_sms(communication))
            elif comm_type == CommunicationType.PUSH_NOTIFICATION.value:
                delivery_result.update(self._send_push_notification(communication))
            elif comm_type == CommunicationType.IN_APP_MESSAGE.value:
                delivery_result.update(self._send_in_app_message(communication))
            else:
                delivery_result.update({
                    "delivery_status": "failed",
                    "error": f"Unsupported communication type: {comm_type}"
                })
        
        except Exception as e:
            delivery_result.update({
                "delivery_status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            })
            logger.error(f"Failed to deliver communication {communication['communication_id']}: {e}")
        
        return delivery_result
    
    def _send_email(self, communication: Dict[str, Any]) -> Dict[str, Any]:
        """Send email communication (mock implementation)"""
        # In a real implementation, this would integrate with email service
        return {
            "delivery_status": "delivered",
            "delivery_provider": "email_service",
            "delivered_at": datetime.now().isoformat(),
            "tracking_id": f"email_{communication['communication_id']}"
        }
    
    def _send_sms(self, communication: Dict[str, Any]) -> Dict[str, Any]:
        """Send SMS communication (mock implementation)"""
        # In a real implementation, this would integrate with SMS service
        return {
            "delivery_status": "delivered",
            "delivery_provider": "sms_service",
            "delivered_at": datetime.now().isoformat(),
            "tracking_id": f"sms_{communication['communication_id']}"
        }
    
    def _send_push_notification(self, communication: Dict[str, Any]) -> Dict[str, Any]:
        """Send push notification (mock implementation)"""
        # In a real implementation, this would integrate with push notification service
        return {
            "delivery_status": "delivered",
            "delivery_provider": "push_service",
            "delivered_at": datetime.now().isoformat(),
            "tracking_id": f"push_{communication['communication_id']}"
        }
    
    def _send_in_app_message(self, communication: Dict[str, Any]) -> Dict[str, Any]:
        """Send in-app message"""
        return {
            "delivery_status": "delivered",
            "delivery_provider": "in_app_messaging",
            "delivered_at": datetime.now().isoformat(),
            "tracking_id": f"inapp_{communication['communication_id']}"
        }
    
    def create_notification_template(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a reusable notification template"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        template_id = core_ops.generate_operation_id("TEMPLATE")
        
        template = {
            "template_id": template_id,
            "name": template_data["name"],
            "communication_type": template_data["communication_type"],
            "subject_template": template_data.get("subject_template", ""),
            "message_template": template_data["message_template"],
            "variables": template_data.get("variables", []),
            "default_priority": template_data.get("priority", CommunicationPriority.NORMAL.value),
            "created_at": datetime.now().isoformat(),
            "created_by": template_data.get("user_id"),
            "active": True
        }
        
        self.notification_templates[template_id] = template
        logger.info(f"Created notification template: {template_id}")
        return template
    
    def send_from_template(self, template_id: str, recipient: str, 
                          variables: Dict[str, Any]) -> Dict[str, Any]:
        """Send communication using a template"""
        if template_id not in self.notification_templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.notification_templates[template_id]
        
        # Replace variables in template
        message = template["message_template"]
        subject = template.get("subject_template", "")
        
        for var_name, var_value in variables.items():
            message = message.replace(f"{{{var_name}}}", str(var_value))
            subject = subject.replace(f"{{{var_name}}}", str(var_value))
        
        communication_data = {
            "recipient": recipient,
            "communication_type": template["communication_type"],
            "priority": template["default_priority"],
            "subject": subject,
            "message": message,
            "metadata": {
                "template_id": template_id,
                "variables_used": variables
            }
        }
        
        return self.send_communication(communication_data)
    
    def get_communication_history(self, reference_id: str, 
                                 reference_type: str = None) -> List[Dict[str, Any]]:
        """Get communication history for a specific reference"""
        history = []
        
        for communication in self.communications_log.values():
            if communication.get("reference_id") == reference_id:
                if reference_type is None or communication.get("reference_type") == reference_type:
                    history.append(communication)
        
        # Sort by creation time, most recent first
        history.sort(key=lambda x: x["created_at"], reverse=True)
        return history
    
    def get_delivery_statistics(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get delivery statistics for communications"""
        if time_period is None:
            time_period = timedelta(days=7)
        
        cutoff_date = datetime.now() - time_period
        
        period_communications = [
            comm for comm in self.communications_log.values()
            if datetime.fromisoformat(comm["created_at"]) >= cutoff_date
        ]
        
        total_sent = len(period_communications)
        delivered = len([c for c in period_communications if c.get("delivery_status") == "delivered"])
        failed = len([c for c in period_communications if c.get("delivery_status") == "failed"])
        pending = len([c for c in period_communications if c.get("delivery_status") == "pending"])
        
        delivery_rate = (delivered / total_sent * 100) if total_sent > 0 else 0
        
        # Statistics by communication type
        by_type = {}
        for comm in period_communications:
            comm_type = comm["communication_type"]
            if comm_type not in by_type:
                by_type[comm_type] = {"sent": 0, "delivered": 0, "failed": 0}
            
            by_type[comm_type]["sent"] += 1
            if comm.get("delivery_status") == "delivered":
                by_type[comm_type]["delivered"] += 1
            elif comm.get("delivery_status") == "failed":
                by_type[comm_type]["failed"] += 1
        
        return {
            "period_days": time_period.days,
            "total_sent": total_sent,
            "delivered": delivered,
            "failed": failed,
            "pending": pending,
            "delivery_rate_percent": round(delivery_rate, 2),
            "by_communication_type": by_type,
            "generated_at": datetime.now().isoformat()
        }
