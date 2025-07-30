"""
Job submission utilities for analysis tasks

This module provides functions for submitting analysis jobs to the worker
and retrieving results asynchronously.
"""

import json
import time
import uuid
import asyncio
from typing import Dict, Any, Optional, List, Union

import redis
from pydantic import BaseModel

from core.config.platform_config import config
from core.services.logger import get_logger

# Configure logging
logger = get_logger("job_manager")

# Connect to Redis
redis_client = redis.Redis.from_url(config.redis_url)

# Job channels
ANALYSIS_JOBS_CHANNEL = "analysis_jobs"
ANALYSIS_RESULTS_CHANNEL = "analysis_results"


class AnalysisJob(BaseModel):
    """Model for analysis job data"""
    job_id: str
    job_type: str  # One of: "impact_analysis", "adci_prediction", "flot_analysis"
    data: Dict[str, Any]
    timestamp: float
    priority: int = 1  # Higher numbers = higher priority


class JobResult(BaseModel):
    """Model for job result data"""
    job_id: str
    status: str
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float


async def submit_impact_analysis_job(
    patient_data: Dict[str, Any], 
    procedure_type: str,
    priority: int = 1
) -> str:
    """
    Submit an impact analysis job
    
    Args:
        patient_data: Patient data dictionary
        procedure_type: Type of surgical procedure
        priority: Job priority (higher = more important)
        
    Returns:
        job_id: Unique ID for tracking the job
    """
    job_id = str(uuid.uuid4())
    
    job = AnalysisJob(
        job_id=job_id,
        job_type="impact_analysis",
        data={
            "patient_data": patient_data,
            "procedure_type": procedure_type
        },
        timestamp=time.time(),
        priority=priority
    )
    
    # Publish job to Redis
    redis_client.publish(ANALYSIS_JOBS_CHANNEL, job.json())
    logger.info(f"Submitted impact analysis job {job_id}")
    
    # Also store in a Redis set for tracking
    redis_client.set(f"job:{job_id}", job.json(), ex=86400)  # expire after 24 hours
    
    return job_id


async def submit_adci_prediction_job(
    patient_data: Dict[str, Any], 
    collaboration_context: Optional[Dict[str, Any]] = None,
    priority: int = 1
) -> str:
    """
    Submit an ADCI prediction job
    
    Args:
        patient_data: Patient data dictionary
        collaboration_context: Optional collaboration context
        priority: Job priority (higher = more important)
        
    Returns:
        job_id: Unique ID for tracking the job
    """
    job_id = str(uuid.uuid4())
    
    job = AnalysisJob(
        job_id=job_id,
        job_type="adci_prediction",
        data={
            "patient_data": patient_data,
            "collaboration_context": collaboration_context
        },
        timestamp=time.time(),
        priority=priority
    )
    
    # Publish job to Redis
    redis_client.publish(ANALYSIS_JOBS_CHANNEL, job.json())
    logger.info(f"Submitted ADCI prediction job {job_id}")
    
    # Also store in a Redis set for tracking
    redis_client.set(f"job:{job_id}", job.json(), ex=86400)  # expire after 24 hours
    
    return job_id


async def submit_flot_analysis_job(
    patient_data: Dict[str, Any], 
    research_context: Optional[Dict[str, Any]] = None,
    priority: int = 1
) -> str:
    """
    Submit a FLOT analysis job
    
    Args:
        patient_data: Patient data dictionary
        research_context: Optional research context
        priority: Job priority (higher = more important)
        
    Returns:
        job_id: Unique ID for tracking the job
    """
    job_id = str(uuid.uuid4())
    
    job = AnalysisJob(
        job_id=job_id,
        job_type="flot_analysis",
        data={
            "patient_data": patient_data,
            "research_context": research_context
        },
        timestamp=time.time(),
        priority=priority
    )
    
    # Publish job to Redis
    redis_client.publish(ANALYSIS_JOBS_CHANNEL, job.json())
    logger.info(f"Submitted FLOT analysis job {job_id}")
    
    # Also store in a Redis set for tracking
    redis_client.set(f"job:{job_id}", job.json(), ex=86400)  # expire after 24 hours
    
    return job_id


async def get_job_status(job_id: str) -> Dict[str, Any]:
    """
    Get the status of a job
    
    Args:
        job_id: Job ID to check
        
    Returns:
        Job status dictionary
    """
    # Check if result exists
    result_json = redis_client.get(f"result:{job_id}")
    if result_json:
        result = json.loads(result_json)
        return result
    
    # Check if job exists
    job_json = redis_client.get(f"job:{job_id}")
    if job_json:
        return {"job_id": job_id, "status": "pending"}
    
    # Job not found
    return {"job_id": job_id, "status": "not_found"}


async def wait_for_job_result(job_id: str, timeout: int = 30) -> Optional[Dict[str, Any]]:
    """
    Wait for a job result with timeout
    
    Args:
        job_id: Job ID to wait for
        timeout: Maximum seconds to wait
        
    Returns:
        Job result or None if timeout
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        status = await get_job_status(job_id)
        
        if status["status"] == "completed":
            return status["results"]
        elif status["status"] == "error":
            raise ValueError(f"Job failed: {status.get('error', 'Unknown error')}")
        elif status["status"] == "not_found":
            raise ValueError(f"Job not found: {job_id}")
        
        # Wait a bit before checking again
        await asyncio.sleep(0.5)
    
    # Timeout
    return None
