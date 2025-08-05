"""
Unified Case Service for Surgify Platform
Handles all case-related business logic with caching, persistence, and advanced analytics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from uuid import uuid4
import pandas as pd

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, desc, asc, select, func
from pydantic import BaseModel

from ..database import get_db
from ..models.database_models import CaseModel, User
from ...data.models.orm import Case
from ..cache import invalidate_cache, cache_response
from .base import BaseService
from .logger import get_logger

logger = get_logger(__name__)

class CaseCreateRequest(BaseModel):
    """Request model for creating a case"""
    patient_id: str
    procedure_type: str
    diagnosis: Optional[str] = None
    status: str = "planned"
    priority: str = "medium"
    surgeon_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None

class CaseUpdateRequest(BaseModel):
    """Request model for updating a case"""
    patient_id: Optional[str] = None
    procedure_type: Optional[str] = None
    diagnosis: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    surgeon_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    notes: Optional[str] = None

class CaseResponse(BaseModel):
    """Response model for case data"""
    id: int
    case_number: str
    patient_id: str
    procedure_type: str
    diagnosis: Optional[str] = None
    status: str
    priority: str
    surgeon_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    risk_score: Optional[float] = None
    recommendations: List[str] = []
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class CaseListFilters(BaseModel):
    """Filters for case listing"""
    status: Optional[str] = None
    procedure_type: Optional[str] = None
    surgeon_id: Optional[str] = None
    priority: Optional[str] = None
    patient_id: Optional[str] = None
    search: Optional[str] = None

class CaseService(BaseService):
    """
    Enhanced case processing service with database persistence and caching
    """
    
    def __init__(self, db: Session = None):
        super().__init__()
        self.db = db
    
    def _get_db(self) -> Session:
        """Get database session"""
        if self.db:
            return self.db
        return next(get_db())
    
    async def create_case(self, request: CaseCreateRequest, user_id: Optional[str] = None) -> CaseResponse:
        """Create a new surgical case"""
        db = self._get_db()
        
        try:
            # Generate unique case number
            case_number = f"CASE-{uuid4().hex[:8].upper()}"
            
            # Create case model
            case_data = CaseModel(
                case_number=case_number,
                patient_id=request.patient_id,
                procedure_type=request.procedure_type,
                diagnosis=request.diagnosis,
                status=request.status,
                priority=request.priority,
                surgeon_id=request.surgeon_id,
                scheduled_date=request.scheduled_date,
                notes=request.notes,
                created_by=user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(case_data)
            db.commit()
            db.refresh(case_data)
            
            # Invalidate cache
            await invalidate_cache("cases")
            
            # Calculate initial risk score (placeholder logic)
            risk_score = await self._calculate_risk_score(case_data)
            recommendations = await self._generate_recommendations(case_data)
            
            logger.info(f"Created case {case_number} for patient {request.patient_id}")
            
            return CaseResponse(
                id=case_data.id,
                case_number=case_data.case_number,
                patient_id=case_data.patient_id,
                procedure_type=case_data.procedure_type,
                diagnosis=case_data.diagnosis,
                status=case_data.status,
                priority=case_data.priority,
                surgeon_id=case_data.surgeon_id,
                scheduled_date=case_data.scheduled_date,
                created_at=case_data.created_at,
                updated_at=case_data.updated_at,
                risk_score=risk_score,
                recommendations=recommendations,
                notes=case_data.notes
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating case: {e}")
            raise
        finally:
            if not self.db:  # Only close if we created the session
                db.close()
    
    async def list_cases(
        self,
        filters: CaseListFilters = None,
        page: int = 1,
        limit: int = 50,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> List[CaseResponse]:
        """List cases with filtering, pagination, and sorting"""
        db = self._get_db()
        
        try:
            query = db.query(CaseModel)
            
            # Apply filters
            if filters:
                if filters.status:
                    query = query.filter(CaseModel.status == filters.status)
                if filters.procedure_type:
                    query = query.filter(CaseModel.procedure_type == filters.procedure_type)
                if filters.surgeon_id:
                    query = query.filter(CaseModel.surgeon_id == filters.surgeon_id)
                if filters.priority:
                    query = query.filter(CaseModel.priority == filters.priority)
                if filters.patient_id:
                    query = query.filter(CaseModel.patient_id == filters.patient_id)
                if filters.search:
                    search_term = f"%{filters.search}%"
                    query = query.filter(
                        or_(
                            CaseModel.case_number.ilike(search_term),
                            CaseModel.patient_id.ilike(search_term),
                            CaseModel.diagnosis.ilike(search_term),
                            CaseModel.procedure_type.ilike(search_term)
                        )
                    )
            
            # Apply sorting
            if sort_order.lower() == "desc":
                query = query.order_by(desc(getattr(CaseModel, sort_by, CaseModel.created_at)))
            else:
                query = query.order_by(asc(getattr(CaseModel, sort_by, CaseModel.created_at)))
            
            # Apply pagination
            offset = (page - 1) * limit
            cases = query.offset(offset).limit(limit).all()
            
            # Convert to response models
            case_responses = []
            for case in cases:
                risk_score = await self._calculate_risk_score(case)
                recommendations = await self._generate_recommendations(case)
                
                case_responses.append(CaseResponse(
                    id=case.id,
                    case_number=case.case_number,
                    patient_id=case.patient_id,
                    procedure_type=case.procedure_type,
                    diagnosis=case.diagnosis,
                    status=case.status,
                    priority=case.priority,
                    surgeon_id=case.surgeon_id,
                    scheduled_date=case.scheduled_date,
                    created_at=case.created_at,
                    updated_at=case.updated_at,
                    risk_score=risk_score,
                    recommendations=recommendations,
                    notes=case.notes
                ))
            
            return case_responses
            
        except Exception as e:
            logger.error(f"Error listing cases: {e}")
            raise
        finally:
            if not self.db:
                db.close()
    
    async def get_case(self, case_id: int) -> Optional[CaseResponse]:
        """Get a specific case by ID"""
        db = self._get_db()
        
        try:
            case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
            
            if not case:
                return None
            
            risk_score = await self._calculate_risk_score(case)
            recommendations = await self._generate_recommendations(case)
            
            return CaseResponse(
                id=case.id,
                case_number=case.case_number,
                patient_id=case.patient_id,
                procedure_type=case.procedure_type,
                diagnosis=case.diagnosis,
                status=case.status,
                priority=case.priority,
                surgeon_id=case.surgeon_id,
                scheduled_date=case.scheduled_date,
                created_at=case.created_at,
                updated_at=case.updated_at,
                risk_score=risk_score,
                recommendations=recommendations,
                notes=case.notes
            )
            
        except Exception as e:
            logger.error(f"Error getting case {case_id}: {e}")
            raise
        finally:
            if not self.db:
                db.close()
    
    async def update_case(self, case_id: int, request: CaseUpdateRequest, user_id: Optional[str] = None) -> Optional[CaseResponse]:
        """Update an existing case"""
        db = self._get_db()
        
        try:
            case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
            
            if not case:
                return None
            
            # Update fields
            update_data = request.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(case, field, value)
            
            case.updated_at = datetime.utcnow()
            case.updated_by = user_id
            
            db.commit()
            db.refresh(case)
            
            # Invalidate cache
            await invalidate_cache("cases")
            await invalidate_cache("cases", id=case_id)
            
            risk_score = await self._calculate_risk_score(case)
            recommendations = await self._generate_recommendations(case)
            
            logger.info(f"Updated case {case.case_number}")
            
            return CaseResponse(
                id=case.id,
                case_number=case.case_number,
                patient_id=case.patient_id,
                procedure_type=case.procedure_type,
                diagnosis=case.diagnosis,
                status=case.status,
                priority=case.priority,
                surgeon_id=case.surgeon_id,
                scheduled_date=case.scheduled_date,
                created_at=case.created_at,
                updated_at=case.updated_at,
                risk_score=risk_score,
                recommendations=recommendations,
                notes=case.notes
            )
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating case {case_id}: {e}")
            raise
        finally:
            if not self.db:
                db.close()
    
    async def delete_case(self, case_id: int) -> bool:
        """Delete a case"""
        db = self._get_db()
        
        try:
            case = db.query(CaseModel).filter(CaseModel.id == case_id).first()
            
            if not case:
                return False
            
            db.delete(case)
            db.commit()
            
            # Invalidate cache
            await invalidate_cache("cases")
            await invalidate_cache("cases", id=case_id)
            
            logger.info(f"Deleted case {case.case_number}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error deleting case {case_id}: {e}")
            raise
        finally:
            if not self.db:
                db.close()
    
    async def _calculate_risk_score(self, case: CaseModel) -> float:
        """Calculate risk score for a case (placeholder implementation)"""
        # This would integrate with actual risk assessment algorithms
        base_score = 0.3
        
        # Adjust based on procedure type
        high_risk_procedures = ["cardiac", "neurosurgery", "transplant"]
        if any(proc in case.procedure_type.lower() for proc in high_risk_procedures):
            base_score += 0.3
        
        # Adjust based on priority
        if case.priority == "high":
            base_score += 0.2
        elif case.priority == "low":
            base_score -= 0.1
        
        return min(max(base_score, 0.0), 1.0)
    
    async def _generate_recommendations(self, case: CaseModel) -> List[str]:
        """Generate recommendations for a case (placeholder implementation)"""
        recommendations = ["Standard pre-operative assessment"]
        
        # Add specific recommendations based on procedure type
        if "cardiac" in case.procedure_type.lower():
            recommendations.extend([
                "Cardiac clearance required",
                "Monitor for arrhythmias",
                "Consider anticoagulation protocol"
            ])
        elif "orthopedic" in case.procedure_type.lower():
            recommendations.extend([
                "DVT prophylaxis",
                "Physical therapy consultation"
            ])
        
        # Add priority-based recommendations
        if case.priority == "high":
            recommendations.append("Expedited scheduling recommended")
        
        return recommendations
