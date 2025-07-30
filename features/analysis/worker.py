"""
Worker module for asynchronous processing of analysis jobs
Handles computationally intensive tasks for the Impact Analyzer and ADCI Engine
"""

import asyncio
import json
import os
import signal
import sys
import time
from typing import Dict, Any, List, Optional

import redis
from pydantic import BaseModel

from core.config.platform_config import config
from core.services.logger import get_logger
from features.analysis.impact_metrics import ImpactMetricsCalculator
from features.decisions.adci_engine import ADCIEngine
from features.protocols.flot_analyzer import FLOTAnalyzer

# Configure logging
logger = get_logger("analysis_worker")

# Initialize components
impact_calculator = ImpactMetricsCalculator()
adci_engine = ADCIEngine()
flot_analyzer = FLOTAnalyzer()

# Connect to Redis
redis_client = redis.Redis.from_url(config.redis_url)
pubsub = redis_client.pubsub()

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


async def process_impact_analysis(job: AnalysisJob) -> Dict[str, Any]:
    """Process impact analysis job"""
    logger.info(f"Processing impact analysis job {job.job_id}")
    
    patient_data = job.data.get("patient_data", {})
    procedure_type = job.data.get("procedure_type", "unknown")
    
    # Calculate impact metrics
    try:
        results = impact_calculator.calculate_impact_metrics(patient_data, procedure_type)
        return {
            "job_id": job.job_id,
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error processing impact analysis job {job.job_id}: {str(e)}")
        return {
            "job_id": job.job_id,
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


async def process_adci_prediction(job: AnalysisJob) -> Dict[str, Any]:
    """Process ADCI prediction job"""
    logger.info(f"Processing ADCI prediction job {job.job_id}")
    
    patient_data = job.data.get("patient_data", {})
    collaboration_context = job.data.get("collaboration_context")
    
    # Generate ADCI prediction
    try:
        results = await adci_engine.predict(patient_data, collaboration_context)
        return {
            "job_id": job.job_id,
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error processing ADCI prediction job {job.job_id}: {str(e)}")
        return {
            "job_id": job.job_id,
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


async def process_flot_analysis(job: AnalysisJob) -> Dict[str, Any]:
    """Process FLOT analysis job"""
    logger.info(f"Processing FLOT analysis job {job.job_id}")
    
    patient_data = job.data.get("patient_data", {})
    research_context = job.data.get("research_context")
    
    # Generate FLOT analysis
    try:
        results = await flot_analyzer.analyze_gastric_surgery_case(patient_data, research_context)
        return {
            "job_id": job.job_id,
            "status": "completed",
            "results": results,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error processing FLOT analysis job {job.job_id}: {str(e)}")
        return {
            "job_id": job.job_id,
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }


async def process_job(job_data: str) -> None:
    """Process a job from the queue"""
    try:
        # Parse job data
        job_dict = json.loads(job_data)
        job = AnalysisJob(**job_dict)
        
        logger.info(f"Processing job {job.job_id} of type {job.job_type}")
        
        # Process based on job type
        if job.job_type == "impact_analysis":
            result = await process_impact_analysis(job)
        elif job.job_type == "adci_prediction":
            result = await process_adci_prediction(job)
        elif job.job_type == "flot_analysis":
            result = await process_flot_analysis(job)
        else:
            logger.error(f"Unknown job type: {job.job_type}")
            result = {
                "job_id": job.job_id,
                "status": "error",
                "error": f"Unknown job type: {job.job_type}",
                "timestamp": time.time()
            }
        
        # Publish result
        redis_client.publish(ANALYSIS_RESULTS_CHANNEL, json.dumps(result))
        logger.info(f"Published result for job {job.job_id}")
        
    except Exception as e:
        logger.error(f"Error processing job: {str(e)}")


async def listen_for_jobs() -> None:
    """Listen for jobs from Redis"""
    logger.info(f"Subscribing to channel {ANALYSIS_JOBS_CHANNEL}")
    pubsub.subscribe(ANALYSIS_JOBS_CHANNEL)
    
    # Process messages
    for message in pubsub.listen():
        if message["type"] == "message":
            job_data = message["data"].decode("utf-8")
            asyncio.create_task(process_job(job_data))


async def main() -> None:
    """Main worker function"""
    logger.info("Starting analysis worker")
    
    # Setup signal handlers
    def handle_exit(sig, frame):
        logger.info("Shutting down worker...")
        pubsub.unsubscribe()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Start listening for jobs
    try:
        await listen_for_jobs()
    except Exception as e:
        logger.error(f"Error in worker: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    logger.info("Starting analysis worker process")
    asyncio.run(main())
