"""Health check and monitoring endpoints."""

import os
import time
from datetime import datetime
from typing import Any

import psutil
import redis
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from shared.config import get_shared_config
from apps.surge.core.database import get_db


router = APIRouter()

config = get_shared_config()


@router.get("/health")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": config.environment,
    }


@router.get("/health/detailed")
async def detailed_health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Detailed health check with dependency status."""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": config.environment,
        "checks": {},
    }

    overall_healthy = True

    # Database check
    try:
        start_time = time.time()
        db.execute(text("SELECT 1")).fetchone()
        db_latency = (time.time() - start_time) * 1000

        health_status["checks"]["database"] = {
            "status": "healthy",
            "latency_ms": round(db_latency, 2),
            "connection_pool": {
                "size": db.bind.pool.size(),
                "checked_in": db.bind.pool.checkedin(),
                "checked_out": db.bind.pool.checkedout(),
            },
        }
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    # Redis check
    try:
        r = redis.from_url(config.redis_url)
        start_time = time.time()
        r.ping()
        redis_latency = (time.time() - start_time) * 1000

        info = r.info()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "latency_ms": round(redis_latency, 2),
            "memory_usage": info.get("used_memory_human", "unknown"),
            "connected_clients": info.get("connected_clients", 0),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        overall_healthy = False

    # System resources
    try:
        health_status["checks"]["system"] = {
            "status": "healthy",
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage_percent": psutil.disk_usage("/").percent,
            "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
        }
    except Exception as e:
        health_status["checks"]["system"] = {"status": "degraded", "error": str(e)}

    # P2P Network check (if enabled)
    if config.feature_p2p:
        try:
            # Mock P2P health check
            health_status["checks"]["p2p_network"] = {
                "status": "healthy",
                "relay_connected": True,
                "peer_count": 5,  # Mock data
                "network_key": config.p2p_network_key[:8] + "...",
            }
        except Exception as e:
            health_status["checks"]["p2p_network"] = {
                "status": "unhealthy",
                "error": str(e),
            }

    # Set overall status
    if not overall_healthy:
        health_status["status"] = "unhealthy"
    elif any(
        check.get("status") == "degraded" for check in health_status["checks"].values()
    ):
        health_status["status"] = "degraded"

    # Return appropriate HTTP status
    if health_status["status"] == "unhealthy":
        return JSONResponse(status_code=503, content=health_status)
    if health_status["status"] == "degraded":
        return JSONResponse(status_code=200, content=health_status)

    return health_status


@router.get("/metrics")
async def metrics_endpoint() -> str:
    """Prometheus metrics endpoint."""
    metrics = []

    # Application metrics
    metrics.append(
        f'surgify_app_info{{version="2.0.0",environment="{config.environment}"}} 1'
    )
    metrics.append(f"surgify_uptime_seconds {time.time() - get_app_start_time()}")

    # Database metrics
    try:
        # Mock metrics for now
        metrics.extend(
            [
                "surgify_db_connections_active 5",
                "surgify_db_connections_total 20",
                'surgify_db_query_duration_seconds{quantile="0.5"} 0.001',
                'surgify_db_query_duration_seconds{quantile="0.95"} 0.005',
                'surgify_db_query_duration_seconds{quantile="0.99"} 0.010',
            ]
        )
    except Exception:
        pass

    # Cache metrics
    try:
        r = redis.from_url(config.redis_url)
        info = r.info()
        cache_hits = info.get("keyspace_hits", 0)
        cache_misses = info.get("keyspace_misses", 0)
        cache_total = cache_hits + cache_misses

        if cache_total > 0:
            hit_ratio = cache_hits / cache_total
            metrics.append(f"surgify_cache_hit_ratio {hit_ratio:.3f}")
            metrics.append(f"surgify_cache_hits_total {cache_hits}")
            metrics.append(f"surgify_cache_misses_total {cache_misses}")

        metrics.append(f"surgify_cache_memory_usage_bytes {info.get('used_memory', 0)}")
    except Exception:
        pass

    # Domain plugin metrics
    metrics.extend(
        [
            'surgify_domains_loaded{domain="surgery"} 1',
            'surgify_domains_loaded{domain="logistics"} 1',
            'surgify_domains_loaded{domain="insurance"} 1',
            'surgify_domains_loaded{domain="radiology"} 1',
            'surgify_domains_loaded{domain="oncology"} 1',
        ]
    )

    # API endpoint metrics (mock for now)
    metrics.extend(
        [
            'surgify_http_requests_total{method="GET",endpoint="/health"} 150',
            'surgify_http_requests_total{method="POST",endpoint="/api/v1/analyze"} 25',
            'surgify_http_request_duration_seconds{method="GET",endpoint="/health",quantile="0.5"} 0.001',
            'surgify_http_request_duration_seconds{method="POST",endpoint="/api/v1/analyze",quantile="0.95"} 2.5',
        ]
    )

    return "\n".join(metrics)


def get_app_start_time() -> float:
    """Get application start time."""
    # This would be set when the app starts
    return getattr(get_app_start_time, "_start_time", time.time())


# Set start time
get_app_start_time._start_time = time.time()


@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Kubernetes readiness probe."""
    try:
        # Check if we can connect to database
        db.execute(text("SELECT 1"))

        # Check if we can connect to Redis
        r = redis.from_url(config.redis_url)
        r.ping()

        return {"status": "ready", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


@router.get("/liveness")
async def liveness_check() -> dict[str, Any]:
    """Kubernetes liveness probe."""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "pid": os.getpid(),
    }
