"""
Enhanced Results API - Real-time Analytics and Processing
Supports WebSocket connections for live updates and comprehensive data export
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    Query,
)
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ...core.database import get_db
from ...core.models.database_models import CohortData, AnalysisResult, ProcessingLog
from ...core.services.logger import get_logger
from ...core.websocket_manager import ConnectionManager

logger = get_logger(__name__)
router = APIRouter()

# WebSocket connection manager
manager = ConnectionManager()


# Pydantic models
class StatisticsSummary(BaseModel):
    totalCases: int
    processingRate: float
    avgRiskScore: float
    highRiskCount: int
    riskDistribution: Dict[str, int]
    stageDistribution: Dict[str, int]
    domainDistribution: Dict[str, int]
    recentActivity: List[Dict[str, Any]]


class ProcessingUpdate(BaseModel):
    type: str  # new_case, processing_complete, statistics_update
    payload: Dict[str, Any]
    timestamp: datetime


class ExportRequest(BaseModel):
    format: str  # csv, json, excel
    includeStatistics: bool = True
    includeCharts: bool = False
    dateRange: Optional[Dict[str, str]] = None
    domain: Optional[str] = None


@router.get("/summary", response_model=StatisticsSummary)
async def get_results_summary(
    domain: Optional[str] = Query(None),
    hours: int = Query(24, description="Hours to look back for recent activity"),
    db: Session = Depends(get_db),
):
    """
    Get comprehensive results summary with real-time statistics
    """
    try:
        # Base query filters
        base_query = db.query(CohortData)
        if domain:
            base_query = base_query.filter(CohortData.domain == domain)

        # Total cases
        total_cases = base_query.count()

        # Processing rate (cases per minute in last hour)
        last_hour = datetime.utcnow() - timedelta(hours=1)
        recent_cases = base_query.filter(CohortData.created_at >= last_hour).count()
        processing_rate = round(recent_cases / 60.0, 2)

        # Risk score analysis (mock calculation for demo)
        risk_scores = []
        stage_risk_mapping = {"IA": 1.5, "IB": 2.0, "II": 2.5, "III": 3.5, "IV": 4.5}

        for record in base_query.all():
            risk_score = stage_risk_mapping.get(record.stage, 2.5)
            # Add some variation based on age
            if record.age:
                age_factor = 1 + (record.age - 65) * 0.01  # Adjust based on age
                risk_score *= max(0.5, min(2.0, age_factor))
            risk_scores.append(risk_score)

        avg_risk_score = (
            round(sum(risk_scores) / len(risk_scores), 2) if risk_scores else 0
        )
        high_risk_count = len([score for score in risk_scores if score >= 3.5])

        # Risk distribution
        risk_distribution = {
            "low": len([score for score in risk_scores if score < 2.5]),
            "medium": len([score for score in risk_scores if 2.5 <= score < 3.5]),
            "high": len([score for score in risk_scores if score >= 3.5]),
        }

        # Stage distribution
        stage_counts = db.query(CohortData.stage, func.count(CohortData.id)).group_by(
            CohortData.stage
        )

        if domain:
            stage_counts = stage_counts.filter(CohortData.domain == domain)

        stage_distribution = {stage: count for stage, count in stage_counts.all()}

        # Domain distribution
        domain_counts = (
            db.query(CohortData.domain, func.count(CohortData.id))
            .group_by(CohortData.domain)
            .all()
        )

        domain_distribution = {domain: count for domain, count in domain_counts}

        # Recent activity
        recent_cutoff = datetime.utcnow() - timedelta(hours=hours)
        recent_activity_query = (
            base_query.filter(CohortData.created_at >= recent_cutoff)
            .order_by(CohortData.created_at.desc())
            .limit(10)
        )

        recent_activity = []
        for record in recent_activity_query.all():
            recent_activity.append(
                {
                    "patient_id": record.patient_id,
                    "stage": record.stage,
                    "domain": record.domain,
                    "created_at": record.created_at.isoformat(),
                    "risk_score": stage_risk_mapping.get(record.stage, 2.5),
                }
            )

        return StatisticsSummary(
            totalCases=total_cases,
            processingRate=processing_rate,
            avgRiskScore=avg_risk_score,
            highRiskCount=high_risk_count,
            riskDistribution=risk_distribution,
            stageDistribution=stage_distribution,
            domainDistribution=domain_distribution,
            recentActivity=recent_activity,
        )

    except Exception as e:
        logger.error(f"Failed to get results summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve results summary"
        )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time results updates
    """
    await manager.connect(websocket)
    try:
        # Send initial data
        await websocket.send_json(
            {
                "type": "connection_established",
                "message": "Real-time updates connected",
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for client messages (heartbeat, subscriptions, etc.)
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "heartbeat":
                    await websocket.send_json(
                        {
                            "type": "heartbeat_response",
                            "timestamp": datetime.utcnow().isoformat(),
                        }
                    )
                elif message.get("type") == "subscribe":
                    # Handle subscription to specific data types
                    await handle_subscription(websocket, message.get("payload", {}))

            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                await websocket.send_json(
                    {
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)


async def handle_subscription(websocket: WebSocket, payload: Dict):
    """
    Handle client subscription requests
    """
    subscription_type = payload.get("subscription_type")

    if subscription_type == "statistics":
        # Send periodic statistics updates
        asyncio.create_task(send_periodic_statistics(websocket))
    elif subscription_type == "processing_log":
        # Send processing log updates
        asyncio.create_task(send_processing_updates(websocket))


async def send_periodic_statistics(websocket: WebSocket):
    """
    Send periodic statistics updates to WebSocket client
    """
    try:
        while True:
            # This would normally fetch from database
            # For demo, we'll send mock periodic updates
            await asyncio.sleep(10)  # Update every 10 seconds

            update = {
                "type": "statistics_update",
                "payload": {
                    "totalCases": 156 + int(datetime.utcnow().timestamp() % 100),
                    "processingRate": round(
                        12 + (datetime.utcnow().timestamp() % 10), 2
                    ),
                    "avgRiskScore": round(
                        3.4 + (datetime.utcnow().timestamp() % 5) * 0.1, 2
                    ),
                },
                "timestamp": datetime.utcnow().isoformat(),
            }

            await websocket.send_json(update)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Error sending periodic statistics: {str(e)}")


async def send_processing_updates(websocket: WebSocket):
    """
    Send real-time processing log updates
    """
    try:
        while True:
            await asyncio.sleep(5)  # Check for updates every 5 seconds

            # Mock processing update
            update = {
                "type": "processing_update",
                "payload": {
                    "message": f"Processed case {uuid.uuid4().hex[:8]} - Stage III",
                    "timestamp": datetime.utcnow().isoformat(),
                    "severity": "info",
                },
            }

            await websocket.send_json(update)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        logger.error(f"Error sending processing updates: {str(e)}")


@router.post("/export")
async def export_results(request: ExportRequest, db: Session = Depends(get_db)):
    """
    Export results data in various formats
    """
    try:
        # Query data based on filters
        query = db.query(CohortData)

        if request.domain:
            query = query.filter(CohortData.domain == request.domain)

        if request.dateRange:
            start_date = datetime.fromisoformat(request.dateRange["start"])
            end_date = datetime.fromisoformat(request.dateRange["end"])
            query = query.filter(
                and_(
                    CohortData.created_at >= start_date,
                    CohortData.created_at <= end_date,
                )
            )

        results = query.all()

        # Generate export based on format
        if request.format == "csv":
            return await export_as_csv(results, request.includeStatistics)
        elif request.format == "json":
            return await export_as_json(results, request.includeStatistics)
        elif request.format == "excel":
            return await export_as_excel(results, request.includeStatistics)
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


async def export_as_csv(results: List, include_statistics: bool) -> StreamingResponse:
    """
    Export results as CSV format
    """
    import csv
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    headers = [
        "patient_id",
        "age",
        "stage",
        "gender",
        "histology",
        "location",
        "domain",
        "created_at",
    ]
    writer.writerow(headers)

    # Write data rows
    for result in results:
        writer.writerow(
            [
                result.patient_id,
                result.age,
                result.stage,
                result.gender or "",
                result.histology or "",
                result.location or "",
                result.domain,
                result.created_at.isoformat() if result.created_at else "",
            ]
        )

    # Add statistics if requested
    if include_statistics:
        writer.writerow([])  # Empty row
        writer.writerow(["STATISTICS"])
        writer.writerow(["Total Records", len(results)])

        # Stage distribution
        stage_counts = defaultdict(int)
        for result in results:
            stage_counts[result.stage] += 1

        writer.writerow(["Stage Distribution"])
        for stage, count in stage_counts.items():
            writer.writerow([stage, count])

    output.seek(0)

    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        },
    )


async def export_as_json(results: List, include_statistics: bool) -> Dict:
    """
    Export results as JSON format
    """
    data = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "total_records": len(results),
        "data": [],
    }

    for result in results:
        data["data"].append(
            {
                "patient_id": result.patient_id,
                "age": result.age,
                "stage": result.stage,
                "gender": result.gender,
                "histology": result.histology,
                "location": result.location,
                "domain": result.domain,
                "created_at": result.created_at.isoformat()
                if result.created_at
                else None,
            }
        )

    if include_statistics:
        # Calculate statistics
        stage_counts = defaultdict(int)
        domain_counts = defaultdict(int)
        age_groups = defaultdict(int)

        for result in results:
            stage_counts[result.stage] += 1
            domain_counts[result.domain] += 1

            if result.age:
                if result.age < 50:
                    age_groups["<50"] += 1
                elif result.age < 70:
                    age_groups["50-70"] += 1
                else:
                    age_groups[">70"] += 1

        data["statistics"] = {
            "stage_distribution": dict(stage_counts),
            "domain_distribution": dict(domain_counts),
            "age_distribution": dict(age_groups),
        }

    return data


async def export_as_excel(results: List, include_statistics: bool) -> StreamingResponse:
    """
    Export results as Excel format (placeholder - would require openpyxl)
    """
    # For now, fall back to CSV format
    # In production, implement proper Excel export with openpyxl
    return await export_as_csv(results, include_statistics)


@router.post("/report")
async def generate_report(
    includeCharts: bool = True,
    includeStatistics: bool = True,
    format: str = "pdf",
    db: Session = Depends(get_db),
):
    """
    Generate comprehensive analysis report
    """
    try:
        # This would generate a comprehensive PDF report
        # For now, return a placeholder response

        report_data = {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.utcnow().isoformat(),
            "format": format,
            "status": "generated",
            "download_url": f"/api/v1/results/download-report/{uuid.uuid4()}",
        }

        logger.info(f"Generated report: {report_data['report_id']}")

        return report_data

    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Report generation failed: {str(e)}"
        )


@router.get("/processing-log")
async def get_processing_log(
    limit: int = Query(50, description="Number of log entries to retrieve"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    db: Session = Depends(get_db),
):
    """
    Get recent processing log entries
    """
    try:
        # Mock processing log for demo
        log_entries = []

        for i in range(limit):
            timestamp = datetime.utcnow() - timedelta(minutes=i * 2)
            entry = {
                "timestamp": timestamp.isoformat(),
                "message": f"Processed case {uuid.uuid4().hex[:8]} - Stage {['IA', 'IB', 'II', 'III', 'IV'][i % 5]}",
                "severity": ["info", "warning", "error"][i % 3]
                if not severity
                else severity,
                "processing_time": round(0.5 + (i % 10) * 0.1, 2),
            }
            log_entries.append(entry)

        return {
            "entries": log_entries,
            "total": limit,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get processing log: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve processing log")


# Background task to broadcast updates to connected WebSocket clients
async def broadcast_update(update: ProcessingUpdate):
    """
    Broadcast update to all connected WebSocket clients
    """
    if manager.active_connections:
        await manager.broadcast(update.dict())


# Utility function to trigger real-time updates (called from other parts of the system)
async def trigger_results_update(update_type: str, payload: Dict[str, Any]):
    """
    Trigger a real-time update to be broadcast to clients
    """
    update = ProcessingUpdate(
        type=update_type, payload=payload, timestamp=datetime.utcnow()
    )

    await broadcast_update(update)
