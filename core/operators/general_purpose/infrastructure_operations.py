"""
Infrastructure Operations Operator
Handles system infrastructure, monitoring, and operational health
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import psutil
import platform
import logging
from core.services.logger import get_logger

logger = get_logger(__name__)


class InfrastructureOperationsOperator:
    """Infrastructure operations manager for system health and monitoring"""
    
    def __init__(self):
        """Initialize infrastructure operations operator"""
        self.system_metrics = {}
        self.health_checks = {}
        self.alerts = {}
        self.service_status = {}
        logger.info("Infrastructure operations operator initialized")
    
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        metric_id = core_ops.generate_operation_id("SYSMETRIC")
        
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            # Memory metrics
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Disk metrics
            disk_usage = psutil.disk_usage('/')
            disk_io = psutil.disk_io_counters()
            
            # Network metrics
            network_io = psutil.net_io_counters()
            
            # Process metrics
            process_count = len(psutil.pids())
            
            metrics = {
                "metric_id": metric_id,
                "timestamp": datetime.now().isoformat(),
                "system_info": {
                    "platform": platform.platform(),
                    "processor": platform.processor(),
                    "architecture": platform.architecture()[0]
                },
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": cpu_count,
                    "frequency_mhz": cpu_freq.current if cpu_freq else None
                },
                "memory": {
                    "total_bytes": memory.total,
                    "available_bytes": memory.available,
                    "used_bytes": memory.used,
                    "usage_percent": memory.percent,
                    "swap_total_bytes": swap.total,
                    "swap_used_bytes": swap.used,
                    "swap_usage_percent": swap.percent
                },
                "disk": {
                    "total_bytes": disk_usage.total,
                    "used_bytes": disk_usage.used,
                    "free_bytes": disk_usage.free,
                    "usage_percent": (disk_usage.used / disk_usage.total) * 100,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                },
                "network": {
                    "bytes_sent": network_io.bytes_sent,
                    "bytes_received": network_io.bytes_recv,
                    "packets_sent": network_io.packets_sent,
                    "packets_received": network_io.packets_recv
                },
                "processes": {
                    "count": process_count
                }
            }
            
            self.system_metrics[metric_id] = metrics
            
            # Track as performance metrics
            core_ops.track_performance_metric("cpu_usage_percent", cpu_percent)
            core_ops.track_performance_metric("memory_usage_percent", memory.percent)
            core_ops.track_performance_metric("disk_usage_percent", metrics["disk"]["usage_percent"])
            
            logger.debug(f"Collected system metrics: {metric_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {
                "metric_id": metric_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "failed"
            }
    
    def perform_health_check(self, service_name: str, check_function: callable) -> Dict[str, Any]:
        """Perform health check for a service"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        check_id = core_ops.generate_operation_id("HEALTHCHECK")
        
        start_time = datetime.now()
        
        try:
            # Execute the health check function
            check_result = check_function()
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            health_check = {
                "check_id": check_id,
                "service_name": service_name,
                "status": "healthy" if check_result.get("success", False) else "unhealthy",
                "response_time_seconds": response_time,
                "check_result": check_result,
                "timestamp": start_time.isoformat(),
                "completed_at": end_time.isoformat()
            }
            
        except Exception as e:
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds()
            
            health_check = {
                "check_id": check_id,
                "service_name": service_name,
                "status": "unhealthy",
                "response_time_seconds": response_time,
                "error": str(e),
                "timestamp": start_time.isoformat(),
                "completed_at": end_time.isoformat()
            }
            
            logger.error(f"Health check failed for {service_name}: {e}")
        
        # Store health check result
        if service_name not in self.health_checks:
            self.health_checks[service_name] = []
        
        self.health_checks[service_name].append(health_check)
        
        # Track response time as performance metric
        core_ops.track_performance_metric(
            f"health_check_response_time_{service_name}",
            response_time,
            {"unit": "seconds", "service": service_name}
        )
        
        logger.info(f"Health check completed for {service_name}: {health_check['status']}")
        return health_check
    
    def create_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create system alert"""
        from .core_operations import CoreOperationsOperator
        core_ops = CoreOperationsOperator()
        
        alert_id = core_ops.generate_operation_id("ALERT")
        
        alert = {
            "alert_id": alert_id,
            "severity": alert_data.get("severity", "warning"),  # info, warning, error, critical
            "source": alert_data.get("source", "system"),
            "title": alert_data["title"],
            "description": alert_data.get("description", ""),
            "metric_name": alert_data.get("metric_name"),
            "metric_value": alert_data.get("metric_value"),
            "threshold": alert_data.get("threshold"),
            "service_affected": alert_data.get("service_affected"),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "acknowledged": False,
            "resolved": False,
            "metadata": alert_data.get("metadata", {})
        }
        
        self.alerts[alert_id] = alert
        
        # Log the alert creation
        core_ops.log_operation("alert_created", {
            "data": {
                "alert_id": alert_id,
                "severity": alert["severity"],
                "source": alert["source"]
            }
        })
        
        logger.warning(f"Alert created: {alert_id} - {alert['title']} ({alert['severity']})")
        return alert
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> Dict[str, Any]:
        """Acknowledge an alert"""
        if alert_id not in self.alerts:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert = self.alerts[alert_id]
        alert["acknowledged"] = True
        alert["acknowledged_by"] = acknowledged_by
        alert["acknowledged_at"] = datetime.now().isoformat()
        
        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return alert
    
    def resolve_alert(self, alert_id: str, resolved_by: str, resolution_notes: str = "") -> Dict[str, Any]:
        """Resolve an alert"""
        if alert_id not in self.alerts:
            raise ValueError(f"Alert {alert_id} not found")
        
        alert = self.alerts[alert_id]
        alert["resolved"] = True
        alert["resolved_by"] = resolved_by
        alert["resolved_at"] = datetime.now().isoformat()
        alert["resolution_notes"] = resolution_notes
        alert["status"] = "resolved"
        
        logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
        return alert
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """Get current status of a service"""
        recent_checks = self.health_checks.get(service_name, [])
        
        if not recent_checks:
            return {
                "service_name": service_name,
                "status": "unknown",
                "last_check": None,
                "message": "No health checks performed"
            }
        
        # Get the most recent health check
        latest_check = max(recent_checks, key=lambda x: x["timestamp"])
        
        # Get recent checks within last hour
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_hour_checks = [
            check for check in recent_checks
            if datetime.fromisoformat(check["timestamp"]) >= one_hour_ago
        ]
        
        # Calculate uptime percentage
        healthy_checks = len([c for c in recent_hour_checks if c["status"] == "healthy"])
        uptime_percent = (healthy_checks / len(recent_hour_checks) * 100) if recent_hour_checks else 0
        
        return {
            "service_name": service_name,
            "status": latest_check["status"],
            "last_check": latest_check["timestamp"],
            "response_time_seconds": latest_check.get("response_time_seconds", 0),
            "uptime_percent_last_hour": round(uptime_percent, 2),
            "total_checks_last_hour": len(recent_hour_checks),
            "last_check_result": latest_check.get("check_result", {})
        }
    
    def get_infrastructure_summary(self) -> Dict[str, Any]:
        """Get overall infrastructure health summary"""
        # Get latest system metrics
        latest_metrics = None
        if self.system_metrics:
            latest_metrics = max(self.system_metrics.values(), key=lambda x: x["timestamp"])
        
        # Get active alerts by severity
        active_alerts = [alert for alert in self.alerts.values() if not alert["resolved"]]
        alerts_by_severity = {}
        for alert in active_alerts:
            severity = alert["severity"]
            alerts_by_severity[severity] = alerts_by_severity.get(severity, 0) + 1
        
        # Get service statuses
        service_statuses = {}
        for service_name in self.health_checks.keys():
            service_statuses[service_name] = self.get_service_status(service_name)
        
        # Overall health score (0-100)
        health_score = 100
        
        # Deduct points for system resource usage
        if latest_metrics:
            cpu_usage = latest_metrics.get("cpu", {}).get("usage_percent", 0)
            memory_usage = latest_metrics.get("memory", {}).get("usage_percent", 0)
            disk_usage = latest_metrics.get("disk", {}).get("usage_percent", 0)
            
            if cpu_usage > 90:
                health_score -= 20
            elif cpu_usage > 70:
                health_score -= 10
            
            if memory_usage > 90:
                health_score -= 20
            elif memory_usage > 70:
                health_score -= 10
            
            if disk_usage > 90:
                health_score -= 15
            elif disk_usage > 80:
                health_score -= 5
        
        # Deduct points for active alerts
        health_score -= alerts_by_severity.get("critical", 0) * 25
        health_score -= alerts_by_severity.get("error", 0) * 15
        health_score -= alerts_by_severity.get("warning", 0) * 5
        
        # Deduct points for unhealthy services
        unhealthy_services = len([s for s in service_statuses.values() if s["status"] != "healthy"])
        health_score -= unhealthy_services * 10
        
        health_score = max(0, health_score)  # Ensure it doesn't go below 0
        
        return {
            "overall_health_score": health_score,
            "status": "healthy" if health_score >= 80 else "degraded" if health_score >= 60 else "unhealthy",
            "latest_metrics": latest_metrics,
            "active_alerts": len(active_alerts),
            "alerts_by_severity": alerts_by_severity,
            "services": service_statuses,
            "generated_at": datetime.now().isoformat()
        }
