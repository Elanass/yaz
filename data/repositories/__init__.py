"""
Clinical Data Repositories
Specialized repositories for gastric oncology data management
"""

from datetime import datetime, date
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from data.repositories.base import BaseRepository
from data.models.orm import (
    PatientORM, ComorbidityORM, TumorCharacteristicsORM, 
    PerformanceStatusORM, LaboratoryResultsORM, TreatmentPlanORM,
    ADCIDecisionORM, ClinicalOutcomeORM, AuditLogORM
)
from data.models import (
    Patient, PatientCreateRequest, PatientUpdateRequest,
    TreatmentPlan, TreatmentPlanRequest, ADCIDecision, ADCIDecisionRequest,
    GenderType, TreatmentProtocol, DecisionStatus
)
from core.models.base import PaginationParams, PaginationMeta


class PatientRepository(BaseRepository[PatientORM]):
    """Repository for patient data management"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(PatientORM, session)
    
    async def get_by_mrn(self, medical_record_number: str, user_id: str = None) -> Optional[PatientORM]:
        """Get patient by medical record number"""
        try:
            query = select(PatientORM).where(
                PatientORM.medical_record_number == medical_record_number
            ).options(
                selectinload(PatientORM.comorbidities),
                selectinload(PatientORM.tumor_characteristics),
                selectinload(PatientORM.performance_status),
                selectinload(PatientORM.laboratory_results),
                selectinload(PatientORM.treatment_plans),
                selectinload(PatientORM.adci_decisions)
            )
            
            result = await self.session.execute(query)
            patient = result.scalar_one_or_none()
            
            if patient:
                await self._log_audit_event(
                    action="read_by_mrn",
                    entity_id=patient.id,
                    user_id=user_id,
                    new_values={"medical_record_number": medical_record_number}
                )
            
            return patient
            
        except Exception as e:
            self.logger.error(f"Error getting patient by MRN {medical_record_number}: {e}")
            raise
    
    async def search_patients(
        self,
        search_criteria: Dict[str, any],
        pagination: PaginationParams = None,
        user_id: str = None
    ) -> Tuple[List[PatientORM], PaginationMeta]:
        """Advanced patient search with multiple criteria"""
        try:
            query = select(PatientORM).options(
                selectinload(PatientORM.tumor_characteristics),
                selectinload(PatientORM.performance_status)
            )
            
            conditions = []
            
            # Name or MRN search
            if search_criteria.get('search_term'):
                term = search_criteria['search_term']
                conditions.append(
                    or_(
                        PatientORM.medical_record_number.ilike(f"%{term}%"),
                        PatientORM.external_id.ilike(f"%{term}%")
                    )
                )
            
            # Age range
            if search_criteria.get('min_age'):
                conditions.append(PatientORM.age >= search_criteria['min_age'])
            if search_criteria.get('max_age'):
                conditions.append(PatientORM.age <= search_criteria['max_age'])
            
            # Gender
            if search_criteria.get('gender'):
                conditions.append(PatientORM.gender == search_criteria['gender'])
            
            # Tumor characteristics (requires join)
            if search_criteria.get('tumor_stage') or search_criteria.get('tumor_histology'):
                query = query.join(TumorCharacteristicsORM, isouter=True)
                
                if search_criteria.get('tumor_stage'):
                    conditions.append(TumorCharacteristicsORM.t_stage == search_criteria['tumor_stage'])
                
                if search_criteria.get('tumor_histology'):
                    conditions.append(TumorCharacteristicsORM.histology == search_criteria['tumor_histology'])
            
            # Apply conditions
            if conditions:
                query = query.where(and_(*conditions))
            
            # Count total
            count_query = select(func.count(PatientORM.id))
            if conditions:
                if search_criteria.get('tumor_stage') or search_criteria.get('tumor_histology'):
                    count_query = count_query.join(TumorCharacteristicsORM, isouter=True)
                count_query = count_query.where(and_(*conditions))
            
            total_result = await self.session.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.size)
                page = pagination.page
                size = pagination.size
            else:
                page = 1
                size = total
            
            # Order by created_at desc by default
            query = query.order_by(PatientORM.created_at.desc())
            
            result = await self.session.execute(query)
            patients = result.scalars().all()
            
            pagination_meta = PaginationMeta.create(page, size, total)
            
            # Log search
            await self._log_audit_event(
                action="advanced_search",
                user_id=user_id,
                new_values={"criteria": search_criteria, "count": len(patients)}
            )
            
            return list(patients), pagination_meta
            
        except Exception as e:
            self.logger.error(f"Error searching patients: {e}")
            raise
    
    async def get_patients_by_protocol(
        self, 
        protocol: TreatmentProtocol,
        user_id: str = None
    ) -> List[PatientORM]:
        """Get all patients on a specific treatment protocol"""
        try:
            query = select(PatientORM).join(TreatmentPlanORM).where(
                TreatmentPlanORM.protocol == protocol
            ).options(
                selectinload(PatientORM.treatment_plans),
                selectinload(PatientORM.tumor_characteristics)
            )
            
            result = await self.session.execute(query)
            patients = result.scalars().all()
            
            await self._log_audit_event(
                action="get_by_protocol",
                user_id=user_id,
                new_values={"protocol": protocol.value, "count": len(patients)}
            )
            
            return list(patients)
            
        except Exception as e:
            self.logger.error(f"Error getting patients by protocol {protocol}: {e}")
            raise
    
    async def get_patient_statistics(self, user_id: str = None) -> Dict[str, any]:
        """Get patient demographics and clinical statistics"""
        try:
            # Total patients
            total_query = select(func.count(PatientORM.id))
            total_result = await self.session.execute(total_query)
            total_patients = total_result.scalar()
            
            # Gender distribution
            gender_query = select(
                PatientORM.gender,
                func.count(PatientORM.id)
            ).group_by(PatientORM.gender)
            gender_result = await self.session.execute(gender_query)
            gender_distribution = {gender.value: count for gender, count in gender_result.all()}
            
            # Age distribution
            age_query = select(
                func.count(PatientORM.id).filter(PatientORM.age < 50).label('under_50'),
                func.count(PatientORM.id).filter(and_(PatientORM.age >= 50, PatientORM.age < 70)).label('50_to_70'),
                func.count(PatientORM.id).filter(PatientORM.age >= 70).label('over_70')
            )
            age_result = await self.session.execute(age_query)
            age_stats = age_result.first()
            
            statistics = {
                "total_patients": total_patients,
                "gender_distribution": gender_distribution,
                "age_distribution": {
                    "under_50": age_stats.under_50,
                    "50_to_70": age_stats.50_to_70,
                    "over_70": age_stats.over_70
                }
            }
            
            await self._log_audit_event(
                action="get_statistics",
                user_id=user_id,
                new_values=statistics
            )
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Error getting patient statistics: {e}")
            raise


class TreatmentPlanRepository(BaseRepository[TreatmentPlanORM]):
    """Repository for treatment plan management"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(TreatmentPlanORM, session)
    
    async def get_by_patient(self, patient_id: UUID, user_id: str = None) -> List[TreatmentPlanORM]:
        """Get all treatment plans for a patient"""
        try:
            query = select(TreatmentPlanORM).where(
                TreatmentPlanORM.patient_id == patient_id
            ).order_by(TreatmentPlanORM.created_at.desc())
            
            result = await self.session.execute(query)
            plans = result.scalars().all()
            
            await self._log_audit_event(
                action="get_by_patient",
                user_id=user_id,
                new_values={"patient_id": str(patient_id), "count": len(plans)}
            )
            
            return list(plans)
            
        except Exception as e:
            self.logger.error(f"Error getting treatment plans for patient {patient_id}: {e}")
            raise
    
    async def get_active_plans(self, user_id: str = None) -> List[TreatmentPlanORM]:
        """Get all active treatment plans"""
        try:
            query = select(TreatmentPlanORM).where(
                TreatmentPlanORM.status == "active"
            ).options(
                joinedload(TreatmentPlanORM.patient)
            ).order_by(TreatmentPlanORM.planned_start_date.asc())
            
            result = await self.session.execute(query)
            plans = result.scalars().all()
            
            await self._log_audit_event(
                action="get_active_plans",
                user_id=user_id,
                new_values={"count": len(plans)}
            )
            
            return list(plans)
            
        except Exception as e:
            self.logger.error(f"Error getting active treatment plans: {e}")
            raise


class ADCIDecisionRepository(BaseRepository[ADCIDecisionORM]):
    """Repository for ADCI decision management"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(ADCIDecisionORM, session)
    
    async def get_by_patient(self, patient_id: UUID, user_id: str = None) -> List[ADCIDecisionORM]:
        """Get all ADCI decisions for a patient"""
        try:
            query = select(ADCIDecisionORM).where(
                ADCIDecisionORM.patient_id == patient_id
            ).order_by(ADCIDecisionORM.decision_timestamp.desc())
            
            result = await self.session.execute(query)
            decisions = result.scalars().all()
            
            await self._log_audit_event(
                action="get_by_patient",
                user_id=user_id,
                new_values={"patient_id": str(patient_id), "count": len(decisions)}
            )
            
            return list(decisions)
            
        except Exception as e:
            self.logger.error(f"Error getting ADCI decisions for patient {patient_id}: {e}")
            raise
    
    async def get_by_decision_maker(
        self, 
        decision_maker: str, 
        pagination: PaginationParams = None,
        user_id: str = None
    ) -> Tuple[List[ADCIDecisionORM], PaginationMeta]:
        """Get decisions by decision maker"""
        try:
            query = select(ADCIDecisionORM).where(
                ADCIDecisionORM.decision_maker == decision_maker
            ).options(
                joinedload(ADCIDecisionORM.patient)
            ).order_by(ADCIDecisionORM.decision_timestamp.desc())
            
            # Count total
            count_query = select(func.count(ADCIDecisionORM.id)).where(
                ADCIDecisionORM.decision_maker == decision_maker
            )
            total_result = await self.session.execute(count_query)
            total = total_result.scalar()
            
            # Apply pagination
            if pagination:
                query = query.offset(pagination.offset).limit(pagination.size)
                page = pagination.page
                size = pagination.size
            else:
                page = 1
                size = total
            
            result = await self.session.execute(query)
            decisions = result.scalars().all()
            
            pagination_meta = PaginationMeta.create(page, size, total)
            
            await self._log_audit_event(
                action="get_by_decision_maker",
                user_id=user_id,
                new_values={"decision_maker": decision_maker, "count": len(decisions)}
            )
            
            return list(decisions), pagination_meta
            
        except Exception as e:
            self.logger.error(f"Error getting decisions by maker {decision_maker}: {e}")
            raise
    
    async def get_decision_analytics(
        self, 
        start_date: datetime = None,
        end_date: datetime = None,
        user_id: str = None
    ) -> Dict[str, any]:
        """Get analytics on ADCI decisions"""
        try:
            query = select(ADCIDecisionORM)
            
            if start_date:
                query = query.where(ADCIDecisionORM.decision_timestamp >= start_date)
            if end_date:
                query = query.where(ADCIDecisionORM.decision_timestamp <= end_date)
            
            # Total decisions
            total_result = await self.session.execute(
                select(func.count(ADCIDecisionORM.id)).select_from(query.subquery())
            )
            total_decisions = total_result.scalar()
            
            # Average score
            avg_score_result = await self.session.execute(
                select(func.avg(ADCIDecisionORM.adci_score)).select_from(query.subquery())
            )
            avg_score = avg_score_result.scalar() or 0
            
            # Confidence level distribution
            confidence_query = select(
                ADCIDecisionORM.confidence_level,
                func.count(ADCIDecisionORM.id)
            ).group_by(ADCIDecisionORM.confidence_level)
            
            if start_date:
                confidence_query = confidence_query.where(ADCIDecisionORM.decision_timestamp >= start_date)
            if end_date:
                confidence_query = confidence_query.where(ADCIDecisionORM.decision_timestamp <= end_date)
            
            confidence_result = await self.session.execute(confidence_query)
            confidence_distribution = {level.value: count for level, count in confidence_result.all()}
            
            # Implementation rate
            implementation_result = await self.session.execute(
                select(func.count(ADCIDecisionORM.id).filter(ADCIDecisionORM.implemented == True)).select_from(query.subquery())
            )
            implemented_count = implementation_result.scalar()
            implementation_rate = (implemented_count / total_decisions * 100) if total_decisions > 0 else 0
            
            analytics = {
                "total_decisions": total_decisions,
                "average_score": round(float(avg_score), 2),
                "confidence_distribution": confidence_distribution,
                "implementation_rate": round(implementation_rate, 2),
                "period": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None
                }
            }
            
            await self._log_audit_event(
                action="get_analytics",
                user_id=user_id,
                new_values=analytics
            )
            
            return analytics
            
        except Exception as e:
            self.logger.error(f"Error getting decision analytics: {e}")
            raise


class ClinicalOutcomeRepository(BaseRepository[ClinicalOutcomeORM]):
    """Repository for clinical outcome tracking"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(ClinicalOutcomeORM, session)
    
    async def get_survival_statistics(
        self,
        protocol: TreatmentProtocol = None,
        user_id: str = None
    ) -> Dict[str, any]:
        """Get survival statistics for outcomes analysis"""
        try:
            query = select(ClinicalOutcomeORM).options(
                joinedload(ClinicalOutcomeORM.patient)
            )
            
            if protocol:
                # Join with treatment plans to filter by protocol
                query = query.join(PatientORM).join(TreatmentPlanORM).where(
                    TreatmentPlanORM.protocol == protocol
                )
            
            result = await self.session.execute(query)
            outcomes = result.scalars().all()
            
            # Calculate statistics
            survival_data = [o.overall_survival_months for o in outcomes if o.overall_survival_months is not None]
            dfs_data = [o.disease_free_survival_months for o in outcomes if o.disease_free_survival_months is not None]
            qol_data = [o.quality_of_life_score for o in outcomes if o.quality_of_life_score is not None]
            
            statistics = {
                "total_outcomes": len(outcomes),
                "overall_survival": {
                    "count": len(survival_data),
                    "mean": sum(survival_data) / len(survival_data) if survival_data else 0,
                    "median": sorted(survival_data)[len(survival_data)//2] if survival_data else 0
                },
                "disease_free_survival": {
                    "count": len(dfs_data),
                    "mean": sum(dfs_data) / len(dfs_data) if dfs_data else 0,
                    "median": sorted(dfs_data)[len(dfs_data)//2] if dfs_data else 0
                },
                "quality_of_life": {
                    "count": len(qol_data),
                    "mean": sum(qol_data) / len(qol_data) if qol_data else 0
                },
                "protocol": protocol.value if protocol else "all"
            }
            
            await self._log_audit_event(
                action="get_survival_statistics",
                user_id=user_id,
                new_values=statistics
            )
            
            return statistics
            
        except Exception as e:
            self.logger.error(f"Error getting survival statistics: {e}")
            raise


# Repository factory for dependency injection

class RepositoryFactory:
    """Factory for creating repository instances"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def patient_repository(self) -> PatientRepository:
        return PatientRepository(self.session)
    
    def treatment_plan_repository(self) -> TreatmentPlanRepository:
        return TreatmentPlanRepository(self.session)
    
    def adci_decision_repository(self) -> ADCIDecisionRepository:
        return ADCIDecisionRepository(self.session)
    
    def clinical_outcome_repository(self) -> ClinicalOutcomeRepository:
        return ClinicalOutcomeRepository(self.session)
