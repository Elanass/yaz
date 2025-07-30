"""
Core Operations Operator
Handles basic business operations that are common across all domains
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class CoreOperationsOperator:
    """Core business operations manager for cross-domain functionality"""
    
    def __init__(self):
        """Initialize core operations operator"""
        self.operations_log = {}
        self.audit_trail = {}
        self.performance_metrics = {}
        logger.info("Core operations operator initialized")
    
    def generate_operation_id(self, operation_type: str) -> str:
        """Generate unique operation ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"{operation_type.upper()}-{timestamp}-{unique_id}"
    
    def log_operation(self, operation_type: str, operation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log any type of operation for audit and tracking"""
        operation_id = self.generate_operation_id(operation_type)
        
        operation_record = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "user_id": operation_data.get("user_id"),
            "session_id": operation_data.get("session_id"),
            "data": operation_data.get("data", {}),
            "metadata": operation_data.get("metadata", {}),
            "status": "logged"
        }
        
        self.operations_log[operation_id] = operation_record
        logger.info(f"Logged operation: {operation_id} ({operation_type})")
        
        return operation_record
    
    def create_audit_entry(self, entity_type: str, entity_id: str, action: str, 
                          changes: Dict[str, Any], user_id: str) -> Dict[str, Any]:
        """Create audit trail entry for any entity change"""
        audit_id = self.generate_operation_id("AUDIT")
        
        audit_entry = {
            "audit_id": audit_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,  # CREATE, UPDATE, DELETE, VIEW
            "changes": changes,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "ip_address": changes.get("ip_address"),
            "user_agent": changes.get("user_agent")
        }
        
        if entity_id not in self.audit_trail:
            self.audit_trail[entity_id] = []
        
        self.audit_trail[entity_id].append(audit_entry)
        logger.info(f"Created audit entry: {audit_id} for {entity_type}:{entity_id}")
        
        return audit_entry
    
    def track_performance_metric(self, metric_name: str, value: float, 
                                tags: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Track performance metrics for any operation"""
        metric_id = self.generate_operation_id("METRIC")
        
        metric_record = {
            "metric_id": metric_id,
            "metric_name": metric_name,
            "value": value,
            "unit": tags.get("unit") if tags else None,
            "tags": tags or {},
            "timestamp": datetime.now().isoformat()
        }
        
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
        
        self.performance_metrics[metric_name].append(metric_record)
        logger.debug(f"Tracked metric: {metric_name} = {value}")
        
        return metric_record
    
    def get_operations_summary(self, time_range: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get summary of operations within time range"""
        if time_range is None:
            time_range = timedelta(days=1)
        
        cutoff_time = datetime.now() - time_range
        recent_operations = []
        
        for operation in self.operations_log.values():
            op_time = datetime.fromisoformat(operation["timestamp"])
            if op_time >= cutoff_time:
                recent_operations.append(operation)
        
        operation_counts = {}
        for op in recent_operations:
            op_type = op["operation_type"]
            operation_counts[op_type] = operation_counts.get(op_type, 0) + 1
        
        return {
            "time_range_hours": time_range.total_seconds() / 3600,
            "total_operations": len(recent_operations),
            "operation_counts": operation_counts,
            "generated_at": datetime.now().isoformat()
        }
    
    def validate_operation_data(self, operation_data: Dict[str, Any], 
                              required_fields: List[str]) -> Dict[str, Any]:
        """Validate operation data has required fields"""
        validation_result = {
            "is_valid": True,
            "missing_fields": [],
            "errors": []
        }
        
        for field in required_fields:
            if field not in operation_data:
                validation_result["missing_fields"].append(field)
                validation_result["is_valid"] = False
        
        if not validation_result["is_valid"]:
            validation_result["errors"].append(
                f"Missing required fields: {', '.join(validation_result['missing_fields'])}"
            )
        
        return validation_result
    
    def cleanup_old_operations(self, retention_days: int = 90) -> Dict[str, Any]:
        """Clean up old operations beyond retention period"""
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        operations_to_remove = []
        for op_id, operation in self.operations_log.items():
            op_time = datetime.fromisoformat(operation["timestamp"])
            if op_time < cutoff_date:
                operations_to_remove.append(op_id)
        
        for op_id in operations_to_remove:
            del self.operations_log[op_id]
        
        cleanup_result = {
            "retention_days": retention_days,
            "operations_cleaned": len(operations_to_remove),
            "remaining_operations": len(self.operations_log),
            "cleanup_timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Cleaned up {len(operations_to_remove)} old operations")
        return cleanup_result
