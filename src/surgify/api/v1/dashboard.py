"""
Dashboard API - Surgify Platform
Enhanced with optional Universal Research metrics
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query

from surgify.modules.analytics.analytics_engine import AnalyticsEngine

# Universal Research Integration (Optional Enhancement)
try:
    from surgify.core.database import get_db
    from surgify.core.services.case_service import CaseService
    from surgify.modules.universal_research.adapters.legacy_bridge import LegacyBridge
    from surgify.modules.universal_research.adapters.surgify_adapter import (
        SurgifyAdapter,
    )

    RESEARCH_AVAILABLE = True
    LegacyBridge = LegacyBridge  # Make available for type hints
except ImportError:
    RESEARCH_AVAILABLE = False
    LegacyBridge = None  # Provide None fallback

router = APIRouter(tags=["Dashboard"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database" / "surgify.db"

# Dependencies
analytics_engine = AnalyticsEngine()


# Research enhancement dependencies (optional)
def get_legacy_bridge() -> Optional[Any]:
    """Get legacy bridge for research enhancements (optional)"""
    if not RESEARCH_AVAILABLE or LegacyBridge is None:
        return None
    try:
        from sqlalchemy.orm import Session

        db_session = next(get_db())
        surgify_adapter = SurgifyAdapter(db_session)
        case_service = CaseService(db_session)
        return LegacyBridge(case_service, surgify_adapter)
    except Exception:
        return None


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))


@router.get("/stats")
async def get_dashboard_stats(
    include_research: bool = Query(
        False, description="Include research metrics (optional)"
    ),
    legacy_bridge: Optional[Any] = Depends(get_legacy_bridge),
):
    """
    Get dashboard statistics
    ENHANCED: Now supports optional research metrics via ?include_research=true
    BACKWARD COMPATIBLE: Works exactly as before when include_research=false (default)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get active cases count (unchanged)
        cursor.execute(
            "SELECT COUNT(*) FROM cases WHERE status IN ('planned', 'in_progress')"
        )
        active_cases = cursor.fetchone()[0]

        # Get completed cases today (unchanged)
        cursor.execute(
            """
            SELECT COUNT(*) FROM cases 
            WHERE status = 'completed' 
            AND date(actual_end) = date('now')
        """
        )
        completed_today = cursor.fetchone()[0]

        # Get total patients (unchanged)
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]

        # Get surgeons count (unchanged)
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'surgeon'")
        total_surgeons = cursor.fetchone()[0]

        # Original dashboard stats (unchanged)
        stats = {
            "active_cases": active_cases,
            "completed_today": completed_today,
            "total_patients": total_patients,
            "total_surgeons": total_surgeons,
        }

        conn.close()

        # RESEARCH ENHANCEMENT (Optional - maintains backward compatibility)
        if include_research and legacy_bridge and RESEARCH_AVAILABLE:
            try:
                enhanced_stats = legacy_bridge.enhance_dashboard_response(
                    stats, include_research=True
                )
                return enhanced_stats
            except Exception:
                # Fallback to original stats if research enhancement fails
                pass

        # Original behavior (unchanged)
        return stats

    except Exception as e:
        # Return basic stats if database doesn't exist or has errors
        return {
            "active_cases": 0,
            "completed_today": 0,
            "total_patients": 0,
            "total_surgeons": 0,
        }


@router.get("/recent-cases")
async def get_recent_cases():
    """Get recent cases for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT c.case_number, p.patient_id, c.procedure_type, 
                   c.status, c.scheduled_date
            FROM cases c
            JOIN patients p ON c.patient_id = p.id
            ORDER BY c.created_at DESC
            LIMIT 5
        """
        )

        cases = []
        for row in cursor.fetchall():
            cases.append(
                {
                    "case_number": row[0],
                    "patient_id": row[1],
                    "procedure_type": row[2],
                    "status": row[3],
                    "scheduled_date": row[4],
                }
            )

        conn.close()
        return {"recent_cases": cases}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/metrics")
async def get_dashboard_metrics():
    """Get dashboard metrics for overview"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get total cases
        cursor.execute("SELECT COUNT(*) FROM cases")
        total_cases = cursor.fetchone()[0] if cursor.fetchone() else 0

        # Get active cases count
        cursor.execute(
            "SELECT COUNT(*) FROM cases WHERE status IN ('planned', 'in_progress')"
        )
        active_cases = cursor.fetchone()[0] if cursor.fetchone() else 0

        # Calculate completion rate
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'completed'")
        completed_cases = cursor.fetchone()[0] if cursor.fetchone() else 0

        completion_rate = (
            (completed_cases / total_cases * 100) if total_cases > 0 else 0
        )

        conn.close()

        return {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "completion_rate": round(completion_rate, 2),
        }

    except Exception as e:
        # Return default values if database doesn't exist yet
        return {"total_cases": 0, "active_cases": 0, "completion_rate": 0.0}


@router.get("/dashboard/metrics", response_model=Dict[str, float])
def get_metrics():
    try:
        metrics = analytics_engine.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/trends", response_model=Dict[str, List[float]])
def get_trends():
    try:
        trends = analytics_engine.get_trends()
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard/export")
def export_report():
    try:
        report_path = analytics_engine.export_report()
        return {"report_path": report_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
