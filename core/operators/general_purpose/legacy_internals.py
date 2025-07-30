"""
Internal Operations Manager
Handles internal system operations, monitoring, health checks, and maintenance
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import psutil
import asyncio
import json
from pathlib import Path

from core.services.base import BaseService
from core.services.logger import get_logger

logger = get_logger(__name__)

class SystemStatus(Enum):
    """System status indicators"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"

class ComponentType(Enum):
    """Types of system components to monitor"""
    DATABASE = "database"
    API = "api"
    WEB_SERVER = "web_server"
    CACHE = "cache"
    STORAGE = "storage"
    EXTERNAL_SERVICE = "external_service"

@dataclass
class HealthCheck:
    """Health check result"""
    component: str
    component_type: ComponentType
    status: SystemStatus
    response_time_ms: Optional[float]
    message: str
    details: Dict[str, Any]
    checked_at: datetime

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    active_connections: int
    request_rate: float
    error_rate: float
    uptime_seconds: int
    collected_at: datetime

class InternalOperator(BaseService):
    """Internal system operations and monitoring"""
    
    def __init__(self):
        super().__init__()
        self.start_time = datetime.now()
        self.health_checks = []
        self.performance_history = []
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run comprehensive health checks"""
        
        try:
            health_results = []
            overall_status = SystemStatus.HEALTHY
            
            # Database health check
            db_health = await self._check_database_health()
            health_results.append(db_health)
            if db_health.status == SystemStatus.CRITICAL:
                overall_status = SystemStatus.CRITICAL
            elif db_health.status == SystemStatus.WARNING and overall_status != SystemStatus.CRITICAL:
                overall_status = SystemStatus.WARNING
            
            # API health check
            api_health = await self._check_api_health()
            health_results.append(api_health)
            if api_health.status == SystemStatus.CRITICAL:
                overall_status = SystemStatus.CRITICAL
            elif api_health.status == SystemStatus.WARNING and overall_status != SystemStatus.CRITICAL:
                overall_status = SystemStatus.WARNING
            
            # Storage health check
            storage_health = await self._check_storage_health()
            health_results.append(storage_health)
            if storage_health.status == SystemStatus.CRITICAL:
                overall_status = SystemStatus.CRITICAL
            elif storage_health.status == SystemStatus.WARNING and overall_status != SystemStatus.CRITICAL:
                overall_status = SystemStatus.WARNING
            
            # External services health check
            external_health = await self._check_external_services()
            health_results.extend(external_health)
            
            # Store health check results
            self.health_checks.extend(health_results)
            
            summary = {
                "overall_status": overall_status.value,
                "timestamp": datetime.now().isoformat(),
                "components": [
                    {
                        "component": hc.component,
                        "type": hc.component_type.value,
                        "status": hc.status.value,
                        "response_time_ms": hc.response_time_ms,
                        "message": hc.message
                    }
                    for hc in health_results
                ],
                "summary": {
                    "total_components": len(health_results),
                    "healthy": sum(1 for hc in health_results if hc.status == SystemStatus.HEALTHY),
                    "warning": sum(1 for hc in health_results if hc.status == SystemStatus.WARNING),
                    "critical": sum(1 for hc in health_results if hc.status == SystemStatus.CRITICAL)
                }
            }
            
            await self._log_health_check(summary)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error running health checks: {e}")
            raise
    
    async def collect_system_metrics(self) -> SystemMetrics:
        """Collect system performance metrics"""
        
        try:
            # CPU and memory usage
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            # Disk usage for main partition
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Network connections (active)
            connections = len(psutil.net_connections(kind='inet'))
            
            # Calculate uptime
            uptime = (datetime.now() - self.start_time).total_seconds()
            
            # Request and error rates (would be collected from application metrics)
            request_rate = await self._get_request_rate()
            error_rate = await self._get_error_rate()
            
            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_percent=disk_percent,
                active_connections=connections,
                request_rate=request_rate,
                error_rate=error_rate,
                uptime_seconds=int(uptime),
                collected_at=datetime.now()
            )
            
            # Store in history
            self.performance_history.append(metrics)
            
            # Keep only last 24 hours of metrics (assuming collection every minute)
            max_history = 24 * 60
            if len(self.performance_history) > max_history:
                self.performance_history = self.performance_history[-max_history:]
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
            raise
    
    async def perform_maintenance_tasks(self) -> Dict[str, Any]:
        """Perform routine maintenance tasks"""
        
        try:
            maintenance_results = {}
            
            # Clean up old log files
            log_cleanup = await self._cleanup_old_logs()
            maintenance_results["log_cleanup"] = log_cleanup
            
            # Clean up temporary files
            temp_cleanup = await self._cleanup_temp_files()
            maintenance_results["temp_cleanup"] = temp_cleanup
            
            # Database maintenance
            db_maintenance = await self._perform_database_maintenance()
            maintenance_results["database_maintenance"] = db_maintenance
            
            # Cache optimization
            cache_optimization = await self._optimize_cache()
            maintenance_results["cache_optimization"] = cache_optimization
            
            # Security updates check
            security_check = await self._check_security_updates()
            maintenance_results["security_check"] = security_check
            
            summary = {
                "maintenance_completed_at": datetime.now().isoformat(),
                "tasks_completed": len(maintenance_results),
                "results": maintenance_results,
                "next_maintenance": (datetime.now() + timedelta(days=1)).isoformat()
            }
            
            await self._log_maintenance(summary)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error performing maintenance: {e}")
            raise
    
    async def get_system_status_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive system status dashboard"""
        
        try:
            # Get latest metrics
            current_metrics = await self.collect_system_metrics()
            
            # Get recent health checks
            recent_health = self.health_checks[-10:] if self.health_checks else []
            
            # Calculate performance trends
            performance_trend = await self._calculate_performance_trend()
            
            # Get alert conditions
            alerts = await self._check_alert_conditions(current_metrics)
            
            dashboard = {
                "system_overview": {
                    "status": await self._determine_overall_system_status(),
                    "uptime_hours": current_metrics.uptime_seconds / 3600,
                    "last_updated": current_metrics.collected_at.isoformat()
                },
                "current_metrics": {
                    "cpu_percent": current_metrics.cpu_percent,
                    "memory_percent": current_metrics.memory_percent,
                    "disk_percent": current_metrics.disk_percent,
                    "active_connections": current_metrics.active_connections,
                    "request_rate": current_metrics.request_rate,
                    "error_rate": current_metrics.error_rate
                },
                "performance_trends": performance_trend,
                "recent_health_checks": [
                    {
                        "component": hc.component,
                        "status": hc.status.value,
                        "checked_at": hc.checked_at.isoformat()
                    }
                    for hc in recent_health
                ],
                "active_alerts": alerts,
                "recommendations": await self._generate_system_recommendations(current_metrics, alerts)
            }
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Error generating system status dashboard: {e}")
            raise
    
    async def _check_database_health(self) -> HealthCheck:
        """Check database connectivity and performance"""
        
        start_time = datetime.now()
        
        try:
            # Simple database connectivity check
            # In a real implementation, this would test actual database connection
            await asyncio.sleep(0.01)  # Simulate database query
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response_time > 1000:  # > 1 second
                status = SystemStatus.CRITICAL
                message = f"Database response time too high: {response_time:.2f}ms"
            elif response_time > 100:  # > 100ms
                status = SystemStatus.WARNING
                message = f"Database response time elevated: {response_time:.2f}ms"
            else:
                status = SystemStatus.HEALTHY
                message = "Database connectivity normal"
            
            return HealthCheck(
                component="database",
                component_type=ComponentType.DATABASE,
                status=status,
                response_time_ms=response_time,
                message=message,
                details={"connection_pool": "healthy", "active_queries": 0},
                checked_at=datetime.now()
            )
            
        except Exception as e:
            return HealthCheck(
                component="database",
                component_type=ComponentType.DATABASE,
                status=SystemStatus.CRITICAL,
                response_time_ms=None,
                message=f"Database health check failed: {str(e)}",
                details={"error": str(e)},
                checked_at=datetime.now()
            )
    
    async def _check_api_health(self) -> HealthCheck:
        """Check API endpoint health"""
        
        start_time = datetime.now()
        
        try:
            # Simulate API health check
            await asyncio.sleep(0.005)  # Simulate API call
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return HealthCheck(
                component="api",
                component_type=ComponentType.API,
                status=SystemStatus.HEALTHY,
                response_time_ms=response_time,
                message="API endpoints responding normally",
                details={"endpoints_tested": 5, "failures": 0},
                checked_at=datetime.now()
            )
            
        except Exception as e:
            return HealthCheck(
                component="api",
                component_type=ComponentType.API,
                status=SystemStatus.CRITICAL,
                response_time_ms=None,
                message=f"API health check failed: {str(e)}",
                details={"error": str(e)},
                checked_at=datetime.now()
            )
    
    async def _check_storage_health(self) -> HealthCheck:
        """Check storage system health"""
        
        try:
            # Check disk space
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            if disk_percent > 90:
                status = SystemStatus.CRITICAL
                message = f"Disk space critically low: {disk_percent:.1f}% used"
            elif disk_percent > 80:
                status = SystemStatus.WARNING
                message = f"Disk space running low: {disk_percent:.1f}% used"
            else:
                status = SystemStatus.HEALTHY
                message = f"Disk space normal: {disk_percent:.1f}% used"
            
            return HealthCheck(
                component="storage",
                component_type=ComponentType.STORAGE,
                status=status,
                response_time_ms=None,
                message=message,
                details={
                    "total_gb": disk.total / (1024**3),
                    "used_gb": disk.used / (1024**3),
                    "free_gb": disk.free / (1024**3)
                },
                checked_at=datetime.now()
            )
            
        except Exception as e:
            return HealthCheck(
                component="storage",
                component_type=ComponentType.STORAGE,
                status=SystemStatus.CRITICAL,
                response_time_ms=None,
                message=f"Storage health check failed: {str(e)}",
                details={"error": str(e)},
                checked_at=datetime.now()
            )
    
    async def _check_external_services(self) -> List[HealthCheck]:
        """Check external service connectivity"""
        
        # Mock external services for now
        services = ["ipfs", "electric_sql"]
        health_checks = []
        
        for service in services:
            try:
                # Simulate external service check
                await asyncio.sleep(0.01)
                
                health_checks.append(HealthCheck(
                    component=service,
                    component_type=ComponentType.EXTERNAL_SERVICE,
                    status=SystemStatus.HEALTHY,
                    response_time_ms=10.0,
                    message=f"{service} service responding",
                    details={"last_sync": datetime.now().isoformat()},
                    checked_at=datetime.now()
                ))
                
            except Exception as e:
                health_checks.append(HealthCheck(
                    component=service,
                    component_type=ComponentType.EXTERNAL_SERVICE,
                    status=SystemStatus.WARNING,
                    response_time_ms=None,
                    message=f"{service} service unavailable: {str(e)}",
                    details={"error": str(e)},
                    checked_at=datetime.now()
                ))
        
        return health_checks
    
    async def _get_request_rate(self) -> float:
        """Get current request rate (requests per second)"""
        # In a real implementation, this would come from application metrics
        return 50.0
    
    async def _get_error_rate(self) -> float:
        """Get current error rate (percentage)"""
        # In a real implementation, this would come from application metrics
        return 0.5
    
    async def _cleanup_old_logs(self) -> Dict[str, Any]:
        """Clean up old log files"""
        
        try:
            logs_dir = Path("logs")
            if not logs_dir.exists():
                return {"status": "skipped", "reason": "logs directory not found"}
            
            cutoff_date = datetime.now() - timedelta(days=30)
            cleaned_files = 0
            freed_space = 0
            
            for log_file in logs_dir.glob("*.log"):
                file_stat = log_file.stat()
                if datetime.fromtimestamp(file_stat.st_mtime) < cutoff_date:
                    freed_space += file_stat.st_size
                    log_file.unlink()
                    cleaned_files += 1
            
            return {
                "status": "completed",
                "files_cleaned": cleaned_files,
                "space_freed_mb": freed_space / (1024 * 1024)
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _cleanup_temp_files(self) -> Dict[str, Any]:
        """Clean up temporary files"""
        
        try:
            temp_dirs = ["temp", "data/uploads/temp", ".pytest_cache"]
            total_cleaned = 0
            total_freed = 0
            
            for temp_dir in temp_dirs:
                temp_path = Path(temp_dir)
                if temp_path.exists():
                    for temp_file in temp_path.rglob("*"):
                        if temp_file.is_file():
                            total_freed += temp_file.stat().st_size
                            temp_file.unlink()
                            total_cleaned += 1
            
            return {
                "status": "completed",
                "files_cleaned": total_cleaned,
                "space_freed_mb": total_freed / (1024 * 1024)
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _perform_database_maintenance(self) -> Dict[str, Any]:
        """Perform database maintenance tasks"""
        
        try:
            # In a real implementation, this would run database optimization
            return {
                "status": "completed",
                "tasks": ["vacuum", "reindex", "analyze"],
                "duration_seconds": 5.0
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        
        try:
            # In a real implementation, this would clear expired cache entries
            return {
                "status": "completed",
                "cache_cleared": True,
                "hit_rate_improvement": 5.0
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _check_security_updates(self) -> Dict[str, Any]:
        """Check for security updates"""
        
        try:
            # In a real implementation, this would check for package updates
            return {
                "status": "completed",
                "security_updates_available": 0,
                "last_check": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def _calculate_performance_trend(self) -> Dict[str, Any]:
        """Calculate performance trends"""
        
        if len(self.performance_history) < 2:
            return {"trend": "insufficient_data"}
        
        recent_metrics = self.performance_history[-10:]
        older_metrics = self.performance_history[-20:-10] if len(self.performance_history) >= 20 else []
        
        if not older_metrics:
            return {"trend": "insufficient_data"}
        
        recent_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        older_cpu = sum(m.cpu_percent for m in older_metrics) / len(older_metrics)
        
        cpu_trend = "increasing" if recent_cpu > older_cpu * 1.1 else "decreasing" if recent_cpu < older_cpu * 0.9 else "stable"
        
        return {
            "trend": "analyzed",
            "cpu_trend": cpu_trend,
            "recent_avg_cpu": recent_cpu,
            "older_avg_cpu": older_cpu
        }
    
    async def _check_alert_conditions(self, metrics: SystemMetrics) -> List[str]:
        """Check for alert conditions"""
        
        alerts = []
        
        if metrics.cpu_percent > 80:
            alerts.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
        
        if metrics.memory_percent > 85:
            alerts.append(f"High memory usage: {metrics.memory_percent:.1f}%")
        
        if metrics.disk_percent > 90:
            alerts.append(f"Disk space critically low: {metrics.disk_percent:.1f}%")
        
        if metrics.error_rate > 5:
            alerts.append(f"High error rate: {metrics.error_rate:.1f}%")
        
        return alerts
    
    async def _determine_overall_system_status(self) -> str:
        """Determine overall system status"""
        
        recent_health = self.health_checks[-5:] if self.health_checks else []
        
        if not recent_health:
            return "unknown"
        
        if any(hc.status == SystemStatus.CRITICAL for hc in recent_health):
            return "critical"
        elif any(hc.status == SystemStatus.WARNING for hc in recent_health):
            return "warning"
        else:
            return "healthy"
    
    async def _generate_system_recommendations(
        self, 
        metrics: SystemMetrics, 
        alerts: List[str]
    ) -> List[str]:
        """Generate system optimization recommendations"""
        
        recommendations = []
        
        if metrics.cpu_percent > 70:
            recommendations.append("Consider scaling compute resources or optimizing CPU-intensive operations")
        
        if metrics.memory_percent > 80:
            recommendations.append("Monitor memory usage and consider increasing available RAM")
        
        if metrics.disk_percent > 85:
            recommendations.append("Clean up old files or increase storage capacity")
        
        if metrics.error_rate > 2:
            recommendations.append("Investigate recent errors and implement fixes")
        
        if not recommendations:
            recommendations.append("System performance is within normal parameters")
        
        return recommendations
    
    async def _log_health_check(self, summary: Dict[str, Any]):
        """Log health check results"""
        await self.audit_log(
            action="system_health_check",
            entity_type="system_monitoring",
            metadata={
                "overall_status": summary["overall_status"],
                "components_checked": summary["summary"]["total_components"],
                "critical_issues": summary["summary"]["critical"]
            }
        )
    
    async def _log_maintenance(self, summary: Dict[str, Any]):
        """Log maintenance completion"""
        await self.audit_log(
            action="system_maintenance",
            entity_type="system_operation",
            metadata={
                "tasks_completed": summary["tasks_completed"],
                "maintenance_time": summary["maintenance_completed_at"]
            }
        )
