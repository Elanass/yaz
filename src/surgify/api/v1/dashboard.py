"""
Dashboard API - Surgify Platform
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

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
