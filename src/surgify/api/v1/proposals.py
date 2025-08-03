"""
Surgical Proposals API - Collaborative Surgery Platform
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
from surgify.core.database import DATABASE_DIR

router = APIRouter()

# Response Models
class ProposalResponse(BaseModel):
    id: int
    case_id: int
    title: str
    description: str
    technique: Optional[str]
    proposed_by: int
    status: str
    regulatory_status: str
    study_reference: Optional[str]
    success_rate: Optional[float]
    created_at: datetime

class ConsentResponse(BaseModel):
    id: int
    proposal_id: int
    surgeon_id: int
    consent_type: str
    comments: Optional[str]
    confidence_score: Optional[float]
    created_at: datetime

@router.get("/proposals", response_model=List[ProposalResponse])
async def get_proposals():
    """Get all surgical proposals"""
    conn = sqlite3.connect(f"{DATABASE_DIR}/surgify.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT p.*, u.full_name as proposer_name
            FROM surgical_proposals p
            LEFT JOIN users u ON p.proposed_by = u.id
            ORDER BY p.created_at DESC
        """)
        
        proposals = []
        for row in cursor.fetchall():
            if row:
                proposals.append(ProposalResponse(
                    id=row[0],
                    case_id=row[1],
                    title=row[3],
                    description=row[4],
                    technique=row[5],
                    proposed_by=row[2],
                    status=row[9],
                    regulatory_status=row[10],
                    study_reference=row[7],
                    success_rate=row[8],
                    created_at=datetime.fromisoformat(row[12]) if row[12] else datetime.now()
                ))
        
        conn.close()
        return proposals
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/proposals/{proposal_id}", response_model=ProposalResponse)
async def get_proposal(proposal_id: int):
    """Get specific surgical proposal"""
    conn = sqlite3.connect(f"{DATABASE_DIR}/surgify.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM surgical_proposals WHERE id = ?
        """, (proposal_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        proposal = ProposalResponse(
            id=row[0],
            case_id=row[1],
            title=row[3],
            description=row[4],
            technique=row[5],
            proposed_by=row[2],
            status=row[9],
            regulatory_status=row[10],
            study_reference=row[7],
            success_rate=row[8],
            created_at=datetime.fromisoformat(row[12]) if row[12] else datetime.now()
        )
        
        conn.close()
        return proposal
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/proposals/{proposal_id}/consents", response_model=List[ConsentResponse])
async def get_proposal_consents(proposal_id: int):
    """Get consents for a specific proposal"""
    conn = sqlite3.connect(f"{DATABASE_DIR}/surgify.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT c.*, u.full_name as surgeon_name
            FROM surgeon_consents c
            LEFT JOIN users u ON c.surgeon_id = u.id
            WHERE c.proposal_id = ?
            ORDER BY c.created_at DESC
        """, (proposal_id,))
        
        consents = []
        for row in cursor.fetchall():
            if row:
                consents.append(ConsentResponse(
                    id=row[0],
                    proposal_id=row[1],
                    surgeon_id=row[2],
                    consent_type=row[3],
                    comments=row[4],
                    confidence_score=row[5],
                    created_at=datetime.fromisoformat(row[6]) if row[6] else datetime.now()
                ))
        
        conn.close()
        return consents
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/studies")
async def get_study_results():
    """Get study results and validation data"""
    conn = sqlite3.connect(f"{DATABASE_DIR}/surgify.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT * FROM study_results
            ORDER BY created_at DESC
        """)
        
        studies = []
        for row in cursor.fetchall():
            if row:
                studies.append({
                    "id": row[0],
                    "study_name": row[1],
                    "study_type": row[2],
                    "participants": row[3],
                    "success_rate": row[6],
                    "published": bool(row[9]),
                    "created_at": row[11]
                })
        
        conn.close()
        return studies
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.get("/collaborations")
async def get_collaborations():
    """Get case collaboration sessions"""
    conn = sqlite3.connect(f"{DATABASE_DIR}/surgify.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT cc.*, c.case_number, u.full_name as primary_surgeon_name
            FROM case_collaborations cc
            LEFT JOIN cases c ON cc.case_id = c.id
            LEFT JOIN users u ON cc.primary_surgeon = u.id
            ORDER BY cc.scheduled_at DESC
        """)
        
        collaborations = []
        for row in cursor.fetchall():
            if row:
                collaborations.append({
                    "id": row[0],
                    "case_id": row[1],
                    "session_name": row[2],
                    "primary_surgeon": row[3],
                    "status": row[6],
                    "scheduled_at": row[5],
                    "case_number": row[8],
                    "primary_surgeon_name": row[9]
                })
        
        conn.close()
        return collaborations
        
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
