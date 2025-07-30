"""
Monitoring Operations Operator
Handles application monitoring, metrics collection, and alerting
"""

from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from collections import defaultdict
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class MonitoringOperationsOperator:
    """Monitoring operations manager for application metrics and alerting"""
    
    def __init__(self):
        """Initialize monitoring operations operator"""
        self.metric_definitions = {}
        self.metric_data = defaultdict(list)
        self.alert_rules = {}
        self.dashboards = {}
        self.monitors = {}
        logger.info("Monitoring operations operator initialized")
    
    def define_metric(self, metric_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Define a new metric for monitoring"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        metric_id = core_ops.generate_operation_id("METRICDEF")
        
        metric_def = {
            "metric_id": metric_id,
            "name": metric_definition["name"],
            "description": metric_definition.get("description", ""),
            "unit": metric_definition.get("unit", "count"),
            "type": metric_definition.get("type", "gauge"),  # gauge, counter, histogram
            "tags": metric_definition.get("tags", []),
            "retention_days": metric_definition.get("retention_days", 30),
            "aggregation_methods": metric_definition.get("aggregation_methods", ["avg", "sum", "min", "max"]),
            "created_at": datetime.now().isoformat(),
            "active": True
        }
        
        self.metric_definitions[metric_definition["name"]] = metric_def
        logger.info(f"Defined metric: {metric_definition['name']} ({metric_id})")
        return metric_def
    
    def record_metric(self, metric_name: str, value: float, 
                     tags: Optional[Dict[str, str]] = None,
                     timestamp: Optional[datetime] = None) -> Dict[str, Any]:
        """Record a metric value"""
        if metric_name not in self.metric_definitions:
            # Auto-create metric definition if it doesn't exist
            self.define_metric({
                "name": metric_name,
                "description": f"Auto-generated metric: {metric_name}"
            })
        
        if timestamp is None:
            timestamp = datetime.now()
        
        metric_record = {
            "metric_name": metric_name,
            "value": value,
            "tags": tags or {},
            "timestamp": timestamp.isoformat()
        }
        
        self.metric_data[metric_name].append(metric_record)
        
        # Check alert rules for this metric
        self._check_alert_rules(metric_name, value, tags)
        
        logger.debug(f"Recorded metric: {metric_name} = {value}")
        return metric_record
    
    def create_alert_rule(self, rule_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert rule for a metric"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        rule_id = core_ops.generate_operation_id("ALERTRULE")
        
        alert_rule = {
            "rule_id": rule_id,
            "name": rule_definition["name"],
            "metric_name": rule_definition["metric_name"],
            "condition": rule_definition["condition"],  # >, <, >=, <=, ==, !=
            "threshold": rule_definition["threshold"],
            "duration_minutes": rule_definition.get("duration_minutes", 5),
            "severity": rule_definition.get("severity", "warning"),
            "description": rule_definition.get("description", ""),
            "tags_filter": rule_definition.get("tags_filter", {}),
            "notification_channels": rule_definition.get("notification_channels", []),
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        
        if rule_definition["metric_name"] not in self.alert_rules:
            self.alert_rules[rule_definition["metric_name"]] = []
        
        self.alert_rules[rule_definition["metric_name"]].append(alert_rule)
        logger.info(f"Created alert rule: {rule_definition['name']} ({rule_id})")
        return alert_rule
    
    def _check_alert_rules(self, metric_name: str, value: float, tags: Optional[Dict[str, str]]) -> None:
        """Check if metric value triggers any alert rules"""
        if metric_name not in self.alert_rules:
            return
        
        for rule in self.alert_rules[metric_name]:
            if not rule["active"]:
                continue
            
            # Check if tags match filter
            if rule["tags_filter"]:
                if not tags or not all(
                    tags.get(k) == v for k, v in rule["tags_filter"].items()
                ):
                    continue
            
            # Check condition
            condition_met = self._evaluate_condition(value, rule["condition"], rule["threshold"])
            
            if condition_met:
                self._trigger_alert(rule, metric_name, value, tags)
    
    def _evaluate_condition(self, value: float, condition: str, threshold: float) -> bool:
        """Evaluate alert condition"""
        if condition == ">":
            return value > threshold
        elif condition == "<":
            return value < threshold
        elif condition == ">=":
            return value >= threshold
        elif condition == "<=":
            return value <= threshold
        elif condition == "==":
            return value == threshold
        elif condition == "!=":
            return value != threshold
        else:
            logger.warning(f"Unknown condition: {condition}")
            return False
    
    def _trigger_alert(self, rule: Dict[str, Any], metric_name: str, 
                      value: float, tags: Optional[Dict[str, str]]) -> None:
        """Trigger an alert based on rule"""
        from .infrastructure_operations import InfrastructureOperationsOperator
        infra_ops = InfrastructureOperationsOperator()
        
        alert_data = {
            "title": f"Alert: {rule['name']}",
            "description": f"Metric {metric_name} value {value} {rule['condition']} {rule['threshold']}",
            "severity": rule["severity"],
            "source": "monitoring_system",
            "metric_name": metric_name,
            "metric_value": value,
            "threshold": rule["threshold"],
            "metadata": {
                "rule_id": rule["rule_id"],
                "tags": tags or {}
            }
        }
        
        infra_ops.create_alert(alert_data)
    
    def create_dashboard(self, dashboard_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create a monitoring dashboard"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        dashboard_id = core_ops.generate_operation_id("DASHBOARD")
        
        dashboard = {
            "dashboard_id": dashboard_id,
            "name": dashboard_definition["name"],
            "description": dashboard_definition.get("description", ""),
            "widgets": dashboard_definition.get("widgets", []),
            "layout": dashboard_definition.get("layout", {}),
            "refresh_interval_seconds": dashboard_definition.get("refresh_interval_seconds", 60),
            "created_at": datetime.now().isoformat(),
            "created_by": dashboard_definition.get("user_id")
        }
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"Created dashboard: {dashboard_definition['name']} ({dashboard_id})")
        return dashboard
    
    def get_metric_data(self, metric_name: str, time_range: Optional[timedelta] = None,
                       aggregation: str = "avg", tags_filter: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Get metric data with optional aggregation and filtering"""
        if metric_name not in self.metric_data:
            return {
                "metric_name": metric_name,
                "data": [],
                "message": "No data found for metric"
            }
        
        data = self.metric_data[metric_name]
        
        # Apply time range filter
        if time_range:
            cutoff_time = datetime.now() - time_range
            data = [
                record for record in data
                if datetime.fromisoformat(record["timestamp"]) >= cutoff_time
            ]
        
        # Apply tags filter
        if tags_filter:
            data = [
                record for record in data
                if all(record.get("tags", {}).get(k) == v for k, v in tags_filter.items())
            ]
        
        # Calculate aggregation
        if data and aggregation != "raw":
            values = [record["value"] for record in data]
            
            if aggregation == "avg":
                aggregated_value = sum(values) / len(values)
            elif aggregation == "sum":
                aggregated_value = sum(values)
            elif aggregation == "min":
                aggregated_value = min(values)
            elif aggregation == "max":
                aggregated_value = max(values)
            elif aggregation == "count":
                aggregated_value = len(values)
            else:
                aggregated_value = None
                logger.warning(f"Unknown aggregation method: {aggregation}")
            
            return {
                "metric_name": metric_name,
                "aggregation": aggregation,
                "value": aggregated_value,
                "data_points": len(data),
                "time_range_hours": time_range.total_seconds() / 3600 if time_range else None,
                "generated_at": datetime.now().isoformat()
            }
        
        return {
            "metric_name": metric_name,
            "data": data,
            "data_points": len(data),
            "time_range_hours": time_range.total_seconds() / 3600 if time_range else None
        }
    
    def create_monitor(self, monitor_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Create a custom monitor"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        monitor_id = core_ops.generate_operation_id("MONITOR")
        
        monitor = {
            "monitor_id": monitor_id,
            "name": monitor_definition["name"],
            "type": monitor_definition["type"],  # health_check, metric_threshold, custom
            "target": monitor_definition.get("target"),  # service, endpoint, metric
            "check_interval_minutes": monitor_definition.get("check_interval_minutes", 5),
            "timeout_seconds": monitor_definition.get("timeout_seconds", 30),
            "configuration": monitor_definition.get("configuration", {}),
            "alert_on_failure": monitor_definition.get("alert_on_failure", True),
            "active": True,
            "created_at": datetime.now().isoformat(),
            "last_check": None,
            "status": "unknown"
        }
        
        self.monitors[monitor_id] = monitor
        logger.info(f"Created monitor: {monitor_definition['name']} ({monitor_id})")
        return monitor
    
    def execute_monitor(self, monitor_id: str) -> Dict[str, Any]:
        """Execute a monitor check"""
        if monitor_id not in self.monitors:
            raise ValueError(f"Monitor {monitor_id} not found")
        
        monitor = self.monitors[monitor_id]
        
        if not monitor["active"]:
            return {"status": "skipped", "reason": "monitor_inactive"}
        
        start_time = datetime.now()
        
        try:
            # Execute monitor based on type
            if monitor["type"] == "health_check":
                result = self._execute_health_check_monitor(monitor)
            elif monitor["type"] == "metric_threshold":
                result = self._execute_metric_threshold_monitor(monitor)
            elif monitor["type"] == "custom":
                result = self._execute_custom_monitor(monitor)
            else:
                result = {"success": False, "error": f"Unknown monitor type: {monitor['type']}"}
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            # Update monitor status
            monitor["last_check"] = start_time.isoformat()
            monitor["status"] = "healthy" if result.get("success", False) else "unhealthy"
            monitor["last_result"] = result
            monitor["execution_time_seconds"] = execution_time
            
            # Record execution as metric
            self.record_metric(
                f"monitor_execution_time_{monitor['name']}",
                execution_time,
                {"monitor_id": monitor_id, "status": monitor["status"]}
            )
            
            logger.info(f"Executed monitor: {monitor_id} - {monitor['status']}")
            return result
            
        except Exception as e:
            monitor["status"] = "error"
            monitor["last_check"] = start_time.isoformat()
            monitor["last_error"] = str(e)
            
            logger.error(f"Monitor execution failed: {monitor_id} - {e}")
            return {"success": False, "error": str(e)}
    
    def _execute_health_check_monitor(self, monitor: Dict[str, Any]) -> Dict[str, Any]:
        """Execute health check monitor"""
        # In a real implementation, this would make HTTP requests or check services
        return {"success": True, "response_time_ms": 150, "status_code": 200}
    
    def _execute_metric_threshold_monitor(self, monitor: Dict[str, Any]) -> Dict[str, Any]:
        """Execute metric threshold monitor"""
        config = monitor["configuration"]
        metric_name = config.get("metric_name")
        threshold = config.get("threshold")
        condition = config.get("condition", ">")
        
        if not metric_name or threshold is None:
            return {"success": False, "error": "Missing metric_name or threshold in configuration"}
        
        # Get recent metric data
        recent_data = self.get_metric_data(
            metric_name,
            time_range=timedelta(minutes=monitor["check_interval_minutes"])
        )
        
        if recent_data.get("value") is not None:
            value = recent_data["value"]
            condition_met = self._evaluate_condition(value, condition, threshold)
            
            return {
                "success": not condition_met,  # Success means threshold not breached
                "metric_value": value,
                "threshold": threshold,
                "condition": condition,
                "threshold_breached": condition_met
            }
        
        return {"success": False, "error": "No recent metric data available"}
    
    def _execute_custom_monitor(self, monitor: Dict[str, Any]) -> Dict[str, Any]:
        """Execute custom monitor"""
        # In a real implementation, this would execute custom monitoring logic
        return {"success": True, "custom_check": "passed"}
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get overall monitoring system summary"""
        # Count metrics
        total_metrics = len(self.metric_definitions)
        active_metrics = len([m for m in self.metric_definitions.values() if m["active"]])
        
        # Count alert rules
        total_alert_rules = sum(len(rules) for rules in self.alert_rules.values())
        active_alert_rules = sum(
            len([r for r in rules if r["active"]])
            for rules in self.alert_rules.values()
        )
        
        # Count monitors
        total_monitors = len(self.monitors)
        active_monitors = len([m for m in self.monitors.values() if m["active"]])
        healthy_monitors = len([m for m in self.monitors.values() if m["status"] == "healthy"])
        
        # Count dashboards
        total_dashboards = len(self.dashboards)
        
        return {
            "metrics": {
                "total": total_metrics,
                "active": active_metrics
            },
            "alert_rules": {
                "total": total_alert_rules,
                "active": active_alert_rules
            },
            "monitors": {
                "total": total_monitors,
                "active": active_monitors,
                "healthy": healthy_monitors,
                "health_percentage": round((healthy_monitors / total_monitors * 100) if total_monitors > 0 else 100, 2)
            },
            "dashboards": {
                "total": total_dashboards
            },
            "generated_at": datetime.now().isoformat()
        }
