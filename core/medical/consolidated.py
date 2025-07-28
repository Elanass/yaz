"""
Core Medical Modules - Consolidated Structure
Healthcare-grade PWA for gastric oncology decision support

This module consolidates the four core medical functionalities:
1. EMR (Electronic Medical Records)
2. Precision Decision Engine 
3. Gastric ADCI Surgery Flow
4. Impact Analyzer
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import logging

from core.config.platform_config import config
from core.dependencies import DatabaseSession, EncryptionService
from data.models import Patient, Case, Decision, ClinicalOutcome
from features.decisions.service import ADCIEngine, GastrectomyEngine
from core.decision_engine.precision_engine import PrecisionEngine


class CoreMedicalModule:
    """
    Consolidated core medical functionality following DRY principles
    Integrates EMR, Decision Engine, Surgery Flow, and Impact Analysis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.adci_engine = ADCIEngine()
        self.gastrectomy_engine = GastrectomyEngine()
        self.precision_engine = PrecisionEngine()
    
    # ========================================
    # EMR (Electronic Medical Records) Core
    # ========================================
    
    async def create_patient_record(
        self, 
        patient_data: Dict[str, Any],
        session: DatabaseSession,
        encryption: EncryptionService
    ) -> Patient:
        """Create new patient record with HIPAA compliance"""
        
        # Encrypt sensitive data
        encrypted_data = {}
        sensitive_fields = ['ssn', 'medical_record_number', 'notes']
        
        for field in sensitive_fields:
            if field in patient_data:
                encrypted_data[f'encrypted_{field}'] = encryption.encrypt_data(
                    str(patient_data[field])
                )
        
        patient = Patient(
            **{k: v for k, v in patient_data.items() if k not in sensitive_fields},
            **encrypted_data,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        session.add(patient)
        await session.commit()
        await session.refresh(patient)
        
        self.logger.info(f"Created patient record: {patient.id}")
        return patient
    
    async def get_patient_history(
        self,
        patient_id: str,
        session: DatabaseSession,
        include_encrypted: bool = False
    ) -> Dict[str, Any]:
        """Get comprehensive patient history"""
        
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        # Get patient with related data
        result = await session.execute(
            select(Patient)
            .options(
                selectinload(Patient.cases),
                selectinload(Patient.decisions),
                selectinload(Patient.outcomes)
            )
            .where(Patient.id == patient_id)
        )
        
        patient = result.scalar_one_or_none()
        if not patient:
            raise ValueError(f"Patient {patient_id} not found")
        
        return {
            'patient': patient,
            'cases': patient.cases,
            'decisions': patient.decisions,
            'outcomes': patient.outcomes,
            'total_cases': len(patient.cases),
            'last_visit': max([case.created_at for case in patient.cases]) if patient.cases else None
        }
    
    # ========================================
    # Precision Decision Engine Core
    # ========================================
    
    async def generate_clinical_decision(
        self,
        patient_data: Dict[str, Any],
        clinical_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate evidence-based clinical decision with confidence scoring"""
        
        # Run ADCI analysis
        adci_result = await self.adci_engine.analyze(
            patient_data, clinical_data, context
        )
        
        # Run surgery-specific analysis if applicable
        surgery_result = None
        if clinical_data.get('tumor_data'):
            surgery_result = await self.gastrectomy_engine.analyze(
                patient_data, clinical_data['tumor_data'], context
            )
        
        # Run precision medicine analysis
        precision_result = await self.precision_engine.analyze(
            patient_data, clinical_data, context
        )
        
        # Consolidate results
        consolidated_decision = {
            'decision_id': f"decision_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'patient_id': patient_data.get('id'),
            'adci_analysis': adci_result,
            'surgery_analysis': surgery_result,
            'precision_analysis': precision_result,
            'consolidated_recommendation': self._consolidate_recommendations(
                adci_result, surgery_result, precision_result
            ),
            'confidence_score': self._calculate_overall_confidence(
                adci_result, surgery_result, precision_result
            )
        }
        
        self.logger.info(f"Generated clinical decision: {consolidated_decision['decision_id']}")
        return consolidated_decision
    
    # ========================================
    # Gastric ADCI Surgery Flow Core
    # ========================================
    
    async def manage_surgery_workflow(
        self,
        case_id: str,
        workflow_stage: str,
        session: DatabaseSession,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Manage gastric surgery workflow stages"""
        
        workflow_stages = [
            'pre_operative_assessment',
            'surgical_planning',
            'intraoperative_monitoring',
            'post_operative_care',
            'follow_up_care'
        ]
        
        if workflow_stage not in workflow_stages:
            raise ValueError(f"Invalid workflow stage: {workflow_stage}")
        
        # Get case
        from sqlalchemy import select
        result = await session.execute(
            select(Case).where(Case.id == case_id)
        )
        case = result.scalar_one_or_none()
        
        if not case:
            raise ValueError(f"Case {case_id} not found")
        
        # Update workflow stage
        case.workflow_stage = workflow_stage
        case.updated_at = datetime.utcnow()
        
        # Process stage-specific data
        workflow_data = await self._process_workflow_stage(
            workflow_stage, case, data
        )
        
        await session.commit()
        
        return {
            'case_id': case_id,
            'workflow_stage': workflow_stage,
            'stage_data': workflow_data,
            'next_stage': self._get_next_workflow_stage(workflow_stage),
            'completion_percentage': self._calculate_workflow_completion(workflow_stage)
        }
    
    # ========================================
    # Impact Analyzer Core
    # ========================================
    
    async def analyze_clinical_impact(
        self,
        intervention_data: Dict[str, Any],
        patient_cohort: List[str],
        session: DatabaseSession,
        timeframe_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze impact of clinical interventions"""
        
        from sqlalchemy import select, and_
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
        
        # Get outcomes for the cohort
        result = await session.execute(
            select(ClinicalOutcome)
            .where(and_(
                ClinicalOutcome.patient_id.in_(patient_cohort),
                ClinicalOutcome.created_at >= cutoff_date
            ))
        )
        
        outcomes = result.scalars().all()
        
        # Calculate impact metrics
        impact_analysis = {
            'intervention': intervention_data.get('type', 'unknown'),
            'cohort_size': len(patient_cohort),
            'timeframe_days': timeframe_days,
            'outcomes_analyzed': len(outcomes),
            'metrics': self._calculate_impact_metrics(outcomes, intervention_data),
            'statistical_significance': self._assess_statistical_significance(outcomes),
            'clinical_significance': self._assess_clinical_significance(outcomes),
            'recommendations': self._generate_impact_recommendations(outcomes)
        }
        
        return impact_analysis
    
    # ========================================
    # Private Helper Methods (DRY)
    # ========================================
    
    def _consolidate_recommendations(
        self, 
        adci_result: Dict[str, Any], 
        surgery_result: Optional[Dict[str, Any]], 
        precision_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Consolidate recommendations from all engines"""
        
        recommendations = {
            'primary': adci_result.get('recommendation', 'Further evaluation needed'),
            'confidence': adci_result.get('confidence_score', 0.5),
            'supporting_evidence': []
        }
        
        if surgery_result:
            recommendations['surgical_approach'] = surgery_result.get('recommendation')
            recommendations['surgical_confidence'] = surgery_result.get('confidence_score')
        
        recommendations['precision_factors'] = precision_result.get('risk_factors', [])
        
        return recommendations
    
    def _calculate_overall_confidence(
        self, 
        adci_result: Dict[str, Any], 
        surgery_result: Optional[Dict[str, Any]], 
        precision_result: Dict[str, Any]
    ) -> float:
        """Calculate overall confidence score"""
        
        scores = [adci_result.get('confidence_score', 0.5)]
        
        if surgery_result:
            scores.append(surgery_result.get('confidence_score', 0.5))
        
        scores.append(precision_result.get('confidence_score', 0.5))
        
        return sum(scores) / len(scores)
    
    async def _process_workflow_stage(
        self, 
        stage: str, 
        case: Case, 
        data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Process stage-specific workflow data"""
        
        stage_processors = {
            'pre_operative_assessment': self._process_pre_op_assessment,
            'surgical_planning': self._process_surgical_planning,
            'intraoperative_monitoring': self._process_intraop_monitoring,
            'post_operative_care': self._process_post_op_care,
            'follow_up_care': self._process_follow_up_care
        }
        
        processor = stage_processors.get(stage)
        if processor:
            return await processor(case, data)
        
        return {'stage': stage, 'processed': False}
    
    def _get_next_workflow_stage(self, current_stage: str) -> Optional[str]:
        """Get next workflow stage"""
        
        stage_sequence = [
            'pre_operative_assessment',
            'surgical_planning', 
            'intraoperative_monitoring',
            'post_operative_care',
            'follow_up_care'
        ]
        
        try:
            current_index = stage_sequence.index(current_stage)
            if current_index < len(stage_sequence) - 1:
                return stage_sequence[current_index + 1]
        except ValueError:
            pass
        
        return None
    
    def _calculate_workflow_completion(self, current_stage: str) -> int:
        """Calculate workflow completion percentage"""
        
        stage_percentages = {
            'pre_operative_assessment': 20,
            'surgical_planning': 40,
            'intraoperative_monitoring': 60,
            'post_operative_care': 80,
            'follow_up_care': 100
        }
        
        return stage_percentages.get(current_stage, 0)
    
    def _calculate_impact_metrics(
        self, 
        outcomes: List[ClinicalOutcome], 
        intervention: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate clinical impact metrics"""
        
        if not outcomes:
            return {'error': 'No outcomes to analyze'}
        
        # Basic metrics
        total_outcomes = len(outcomes)
        positive_outcomes = len([o for o in outcomes if o.outcome_value > 0])
        
        return {
            'total_cases': total_outcomes,
            'positive_outcomes': positive_outcomes,
            'success_rate': positive_outcomes / total_outcomes if total_outcomes > 0 else 0,
            'average_outcome_score': sum([o.outcome_value for o in outcomes]) / total_outcomes,
            'intervention_type': intervention.get('type', 'unknown')
        }
    
    def _assess_statistical_significance(self, outcomes: List[ClinicalOutcome]) -> Dict[str, Any]:
        """Assess statistical significance of outcomes"""
        
        # Simplified statistical assessment
        return {
            'sample_size': len(outcomes),
            'significance_level': 'preliminary' if len(outcomes) < 30 else 'adequate',
            'confidence_interval': '95%' if len(outcomes) >= 30 else 'insufficient_data'
        }
    
    def _assess_clinical_significance(self, outcomes: List[ClinicalOutcome]) -> Dict[str, Any]:
        """Assess clinical significance of outcomes"""
        
        return {
            'clinical_relevance': 'high' if len(outcomes) >= 10 else 'moderate',
            'practice_changing_potential': 'requires_validation',
            'guideline_impact': 'under_review'
        }
    
    def _generate_impact_recommendations(self, outcomes: List[ClinicalOutcome]) -> List[str]:
        """Generate recommendations based on impact analysis"""
        
        recommendations = []
        
        if len(outcomes) < 10:
            recommendations.append("Increase sample size for more robust analysis")
        
        success_rate = len([o for o in outcomes if o.outcome_value > 0]) / len(outcomes)
        
        if success_rate > 0.8:
            recommendations.append("Consider expanding intervention to broader patient population")
        elif success_rate < 0.5:
            recommendations.append("Review intervention protocol and patient selection criteria")
        else:
            recommendations.append("Continue monitoring with current protocol")
        
        return recommendations
    
    # Stage-specific processors (simplified implementations)
    async def _process_pre_op_assessment(self, case: Case, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'stage': 'pre_operative_assessment', 'completed': True}
    
    async def _process_surgical_planning(self, case: Case, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'stage': 'surgical_planning', 'completed': True}
    
    async def _process_intraop_monitoring(self, case: Case, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'stage': 'intraoperative_monitoring', 'completed': True}
    
    async def _process_post_op_care(self, case: Case, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'stage': 'post_operative_care', 'completed': True}
    
    async def _process_follow_up_care(self, case: Case, data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        return {'stage': 'follow_up_care', 'completed': True}


# Singleton instance for global use
core_medical = CoreMedicalModule()
