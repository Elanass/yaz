"""
Dashboard API - Surgify Platform
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["Dashboard"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database" / "surgify.db"

def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))

@router.get("/stats")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get active cases count
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status IN ('planned', 'in_progress')")
        active_cases = cursor.fetchone()[0]
        
        # Get completed cases today
        cursor.execute("""
            SELECT COUNT(*) FROM cases 
            WHERE status = 'completed' 
            AND date(actual_end) = date('now')
        """)
        completed_today = cursor.fetchone()[0]
        
        # Get total patients
        cursor.execute("SELECT COUNT(*) FROM patients")
        total_patients = cursor.fetchone()[0]
        
        # Get surgeons count
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'surgeon'")
        total_surgeons = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "activeCases": active_cases,
            "completedToday": completed_today,
            "totalPatients": total_patients,
            "totalSurgeons": total_surgeons
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/recent-cases")
async def get_recent_cases():
    """Get recent cases for dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.case_number, p.patient_id, c.procedure_type, 
                   c.status, c.scheduled_date
            FROM cases c
            JOIN patients p ON c.patient_id = p.id
            ORDER BY c.created_at DESC
            LIMIT 5
        """)
        
        cases = []
        for row in cursor.fetchall():
            cases.append({
                "case_number": row[0],
                "patient_id": row[1],
                "procedure_type": row[2],
                "status": row[3],
                "scheduled_date": row[4]
            })
        
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
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status IN ('planned', 'in_progress')")
        active_cases = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        # Calculate completion rate
        cursor.execute("SELECT COUNT(*) FROM cases WHERE status = 'completed'")
        completed_cases = cursor.fetchone()[0] if cursor.fetchone() else 0
        
        completion_rate = (completed_cases / total_cases * 100) if total_cases > 0 else 0
        
        conn.close()
        
        return {
            "total_cases": total_cases,
            "active_cases": active_cases,
            "completion_rate": round(completion_rate, 2)
        }
        
    except Exception as e:
        # Return default values if database doesn't exist yet
        return {
            "total_cases": 0,
            "active_cases": 0,
            "completion_rate": 0.0
        }
