"""
Search API - Surgify Platform
Provides unified search across cases, patients, procedures, and protocols
"""

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/search", tags=["Search"])

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "data" / "database" / "surgify.db"


class SearchRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20


class SearchResult(BaseModel):
    type: str  # 'case', 'patient', 'procedure', 'protocol'
    id: str
    title: str
    description: str
    url: str
    metadata: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    results: List[SearchResult]
    total: int
    query: str


def get_db_connection():
    """Get database connection"""
    return sqlite3.connect(str(DB_PATH))


def search_cases(query: str, limit: int = 10) -> List[SearchResult]:
    """Search in cases"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT c.id, c.case_number, c.diagnosis, c.procedure_type, c.status,
                   p.first_name, p.last_name, p.patient_id
            FROM cases c
            JOIN patients p ON c.patient_id = p.id
            WHERE c.case_number LIKE ? OR c.diagnosis LIKE ? OR c.procedure_type LIKE ?
               OR p.first_name LIKE ? OR p.last_name LIKE ? OR p.patient_id LIKE ?
            ORDER BY c.created_at DESC
            LIMIT ?
        """,
            (
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                f"%{query}%",
                limit,
            ),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                SearchResult(
                    type="case",
                    id=str(row[0]),
                    title=f"Case {row[1]}",
                    description=f"{row[2]} - {row[3]} ({row[4]})",
                    url=f"/cases/{row[0]}",
                    metadata={
                        "patient_name": f"{row[5]} {row[6]}",
                        "patient_id": row[7],
                        "status": row[4],
                    },
                )
            )

        conn.close()
        return results
    except Exception as e:
        print(f"Error searching cases: {e}")
        return []


def search_patients(query: str, limit: int = 10) -> List[SearchResult]:
    """Search in patients"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, patient_id, first_name, last_name, date_of_birth, phone
            FROM patients
            WHERE patient_id LIKE ? OR first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?
            ORDER BY last_name, first_name
            LIMIT ?
        """,
            (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                SearchResult(
                    type="patient",
                    id=str(row[0]),
                    title=f"{row[2]} {row[3]}",
                    description=f"Patient ID: {row[1]} | DOB: {row[4]}",
                    url=f"/patients/{row[0]}",
                    metadata={"patient_id": row[1], "phone": row[5]},
                )
            )

        conn.close()
        return results
    except Exception as e:
        print(f"Error searching patients: {e}")
        return []


def search_procedures() -> List[SearchResult]:
    """Search in available procedures"""
    procedures = [
        {
            "id": "gastric_resection",
            "name": "Gastric Resection",
            "description": "Surgical removal of part or all of the stomach",
        },
        {
            "id": "laparoscopic_surgery",
            "name": "Laparoscopic Surgery",
            "description": "Minimally invasive surgical technique",
        },
        {
            "id": "bariatric_surgery",
            "name": "Bariatric Surgery",
            "description": "Weight loss surgery procedures",
        },
        {
            "id": "endoscopic_procedures",
            "name": "Endoscopic Procedures",
            "description": "Non-invasive diagnostic and therapeutic procedures",
        },
        {
            "id": "emergency_surgery",
            "name": "Emergency Surgery",
            "description": "Urgent surgical interventions",
        },
    ]

    return [
        SearchResult(
            type="procedure",
            id=proc["id"],
            title=proc["name"],
            description=proc["description"],
            url=f"/procedures/{proc['id']}",
            metadata={"category": "surgical_procedure"},
        )
        for proc in procedures
    ]


@router.post("/", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Unified search endpoint
    """
    if not request.query or len(request.query.strip()) < 2:
        raise HTTPException(
            status_code=400, detail="Query must be at least 2 characters long"
        )

    query = request.query.strip()

    # Search across different types
    case_results = search_cases(query, request.limit // 3)
    patient_results = search_patients(query, request.limit // 3)

    # For procedures, only include if query matches
    procedure_results = []
    if any(
        query.lower() in proc.title.lower() or query.lower() in proc.description.lower()
        for proc in search_procedures()
    ):
        procedure_results = [
            proc
            for proc in search_procedures()
            if query.lower() in proc.title.lower()
            or query.lower() in proc.description.lower()
        ]

    # Combine all results
    all_results = case_results + patient_results + procedure_results

    # Limit total results
    all_results = all_results[: request.limit]

    return SearchResponse(results=all_results, total=len(all_results), query=query)


@router.get("/suggestions/{query}")
async def get_search_suggestions(query: str):
    """
    Get search suggestions for auto-complete
    """
    if len(query) < 2:
        return {"suggestions": []}

    suggestions = []

    # Add some common search terms
    common_terms = [
        "gastric cancer",
        "emergency surgery",
        "laparoscopic",
        "bariatric",
        "endoscopic",
        "diagnosis",
        "high risk",
        "completed cases",
    ]

    matching_terms = [term for term in common_terms if query.lower() in term.lower()]
    suggestions.extend(matching_terms[:5])

    return {"suggestions": suggestions}


@router.get("/recent")
async def get_recent_searches():
    """
    Get recent search terms (mock implementation)
    """
    return {
        "recent": [
            "gastric resection",
            "patient Smith",
            "emergency cases",
            "high risk procedures",
        ]
    }
