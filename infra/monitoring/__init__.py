"""Monitoring and Metrics Module for YAZ Healthcare Platform
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List


logger = logging.getLogger("yaz-monitoring")


@dataclass
class Metric:
    """Data class for storing metrics"""

    name: str
    value: float
    timestamp: datetime
    tags: dict[str, str] = None


class MetricsCollector:
    """Collects and stores platform metrics"""

    def __init__(self):
        self.metrics: list[Metric] = []
        self.counters: dict[str, int] = {}
        self.gauges: dict[str, float] = {}
        self.timers: dict[str, list[float]] = {}

    def counter(self, name: str, value: int = 1, tags: dict[str, str] = None):
        """Increment a counter metric"""
        if name not in self.counters:
            self.counters[name] = 0
        self.counters[name] += value

        metric = Metric(
            name=name, value=self.counters[name], timestamp=datetime.now(), tags=tags
        )
        self.metrics.append(metric)

    def gauge(self, name: str, value: float, tags: dict[str, str] = None):
        """Set a gauge metric"""
        self.gauges[name] = value

        metric = Metric(name=name, value=value, timestamp=datetime.now(), tags=tags)
        self.metrics.append(metric)

    def timer(self, name: str, value: float, tags: dict[str, str] = None):
        """Record a timing metric"""
        if name not in self.timers:
            self.timers[name] = []
        self.timers[name].append(value)

        metric = Metric(name=name, value=value, timestamp=datetime.now(), tags=tags)
        self.metrics.append(metric)

    def get_metrics(self, since: datetime = None) -> list[Metric]:
        """Get metrics since a specific time"""
        if since is None:
            return self.metrics

        return [m for m in self.metrics if m.timestamp >= since]

    def get_summary(self) -> dict:
        """Get a summary of all metrics"""
        now = datetime.now()
        last_hour = now - timedelta(hours=1)

        recent_metrics = self.get_metrics(since=last_hour)

        return {
            "total_metrics": len(self.metrics),
            "recent_metrics": len(recent_metrics),
            "counters": self.counters,
            "gauges": self.gauges,
            "timer_averages": {
                name: sum(values) / len(values) if values else 0
                for name, values in self.timers.items()
            },
            "timestamp": now.isoformat(),
        }


class HealthChecker:
    """Health checking for platform components"""

    def __init__(self):
        self.checks: dict[str, callable] = {}
        self.status: dict[str, dict] = {}

    def register_check(self, name: str, check_func: callable):
        """Register a health check function"""
        self.checks[name] = check_func

    async def run_checks(self) -> dict[str, dict]:
        """Run all health checks"""
        results = {}

        for name, check_func in self.checks.items():
            try:
                start_time = time.time()

                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                duration = time.time() - start_time

                results[name] = {
                    "status": "healthy" if result else "unhealthy",
                    "duration_ms": round(duration * 1000, 2),
                    "timestamp": datetime.now().isoformat(),
                    "details": result if isinstance(result, dict) else {},
                }

            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        self.status = results
        return results

    def get_overall_status(self) -> str:
        """Get overall platform health status"""
        if not self.status:
            return "unknown"

        statuses = [check["status"] for check in self.status.values()]

        if "error" in statuses or "unhealthy" in statuses:
            return "degraded"
        return "healthy"


# Global instances
metrics = MetricsCollector()
health_checker = HealthChecker()


def time_function(name: str):
    """Decorator to time function execution"""

    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.timer(f"{name}_duration", duration)
                metrics.counter(f"{name}_success")
                return result
            except Exception:
                duration = time.time() - start_time
                metrics.timer(f"{name}_duration", duration)
                metrics.counter(f"{name}_error")
                raise

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.timer(f"{name}_duration", duration)
                metrics.counter(f"{name}_success")
                return result
            except Exception:
                duration = time.time() - start_time
                metrics.timer(f"{name}_duration", duration)
                metrics.counter(f"{name}_error")
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
