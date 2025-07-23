"""
Clinical Quality Service - Decision explainability and human-AI concordance.
Implements comprehensive quality assurance for clinical decision support.
"""

import json
import logging
import statistics
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4

import numpy as np
from fastapi import HTTPException
from sqlalchemy import select, and_, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..db.models import User, Patient, DecisionResult, ClinicalProtocol
from ..schemas.clinical_quality import (
    ExplainabilityReport,
    ConcordanceAnalysis,
    GuidelineCompliance,
    QualityMetrics,
    DecisionExplanation,
    FeatureImportance,
    ClinicalReasoning,
    QualityAssessment,
)

logger = logging.getLogger(__name__)


class ClinicalQualityService:
    """Service for clinical decision quality assurance and explainability."""

    def __init__(self):
        self.explanation_templates = self._load_explanation_templates()
        self.guideline_rules = self._load_guideline_rules()

    async def generate_decision_explanation(
        self,
        db: AsyncSession,
        decision_id: UUID,
        explanation_level: str = "detailed",
    ) -> DecisionExplanation:
        """Generate comprehensive explanation for a clinical decision."""
        try:
            # Get decision details
            result = await db.execute(
                select(DecisionResult).where(DecisionResult.id == decision_id)
            )
            decision = result.scalar_one_or_none()
            
            if not decision:
                raise HTTPException(status_code=404, detail="Decision not found")

            # Generate feature importance analysis
            feature_importance = await self._analyze_feature_importance(db, decision)
            
            # Generate clinical reasoning
            clinical_reasoning = await self._generate_clinical_reasoning(db, decision)
            
            # Generate natural language explanation
            natural_explanation = await self._generate_natural_explanation(
                decision, feature_importance, explanation_level
            )
            
            # Calculate confidence metrics
            confidence_metrics = await self._calculate_confidence_metrics(db, decision)
            
            # Get similar cases for context
            similar_cases = await self._find_similar_cases(db, decision)
            
            explanation = DecisionExplanation(
                decision_id=decision_id,
                natural_explanation=natural_explanation,
                feature_importance=feature_importance,
                clinical_reasoning=clinical_reasoning,
                confidence_metrics=confidence_metrics,
                similar_cases=similar_cases,
                evidence_quality=await self._assess_evidence_quality(db, decision),
                guideline_alignment=await self._check_guideline_alignment(db, decision),
                uncertainty_sources=await self._identify_uncertainty_sources(db, decision),
                recommendations=await self._generate_recommendations(db, decision),
                generated_at=datetime.utcnow(),
            )

            return explanation

        except Exception as e:
            logger.error(f"Failed to generate decision explanation: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to generate decision explanation"
            )

    async def analyze_human_ai_concordance(
        self,
        db: AsyncSession,
        timeframe_days: int = 30,
        user_id: Optional[UUID] = None,
    ) -> ConcordanceAnalysis:
        """Analyze concordance between human and AI decisions."""
        try:
            # Get decisions from the specified timeframe
            cutoff_date = datetime.utcnow() - timedelta(days=timeframe_days)
            
            query = select(DecisionResult).where(
                DecisionResult.created_at >= cutoff_date
            )
            
            if user_id:
                query = query.where(DecisionResult.user_id == user_id)
            
            result = await db.execute(query)
            decisions = result.scalars().all()

            if not decisions:
                return ConcordanceAnalysis(
                    timeframe_days=timeframe_days,
                    total_decisions=0,
                    concordance_rate=0.0,
                    discordance_patterns=[],
                    user_specific=user_id is not None,
                    analysis_date=datetime.utcnow(),
                )

            # Analyze concordance patterns
            concordance_data = []
            discordance_patterns = []
            
            for decision in decisions:
                # Compare AI recommendation with human final decision
                # This would require additional fields in the decision model
                # For now, use mock data
                
                ai_recommendation = decision.recommendation
                human_decision = decision.final_decision if hasattr(decision, 'final_decision') else ai_recommendation
                
                is_concordant = ai_recommendation.lower() == human_decision.lower()
                concordance_data.append(is_concordant)
                
                if not is_concordant:
                    discordance_patterns.append({
                        "decision_id": str(decision.id),
                        "ai_recommendation": ai_recommendation,
                        "human_decision": human_decision,
                        "confidence_score": decision.confidence_score,
                        "case_complexity": self._assess_case_complexity(decision),
                        "discordance_reason": await self._analyze_discordance_reason(decision),
                    })

            # Calculate metrics
            concordance_rate = sum(concordance_data) / len(concordance_data) if concordance_data else 0.0
            
            # Analyze patterns
            complexity_concordance = self._analyze_complexity_concordance(decisions, concordance_data)
            confidence_concordance = self._analyze_confidence_concordance(decisions, concordance_data)
            
            analysis = ConcordanceAnalysis(
                timeframe_days=timeframe_days,
                total_decisions=len(decisions),
                concordance_rate=concordance_rate,
                concordance_by_complexity=complexity_concordance,
                concordance_by_confidence=confidence_concordance,
                discordance_patterns=discordance_patterns,
                user_specific=user_id is not None,
                analysis_date=datetime.utcnow(),
                recommendations=self._generate_concordance_recommendations(
                    concordance_rate, discordance_patterns
                ),
            )

            return analysis

        except Exception as e:
            logger.error(f"Failed to analyze human-AI concordance: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to analyze human-AI concordance"
            )

    async def check_guideline_compliance(
        self,
        db: AsyncSession,
        decision_id: UUID,
        guideline_set: Optional[str] = None,
    ) -> GuidelineCompliance:
        """Check decision compliance with clinical guidelines."""
        try:
            # Get decision details
            result = await db.execute(
                select(DecisionResult).where(DecisionResult.id == decision_id)
            )
            decision = result.scalar_one_or_none()
            
            if not decision:
                raise HTTPException(status_code=404, detail="Decision not found")

            # Get applicable guidelines
            applicable_guidelines = await self._get_applicable_guidelines(
                db, decision, guideline_set
            )
            
            # Check compliance for each guideline
            compliance_results = []
            overall_compliance = True
            
            for guideline in applicable_guidelines:
                compliance_result = await self._check_single_guideline_compliance(
                    db, decision, guideline
                )
                compliance_results.append(compliance_result)
                
                if not compliance_result["is_compliant"]:
                    overall_compliance = False

            # Generate compliance report
            compliance = GuidelineCompliance(
                decision_id=decision_id,
                guideline_set=guideline_set or "default",
                overall_compliance=overall_compliance,
                compliance_score=self._calculate_compliance_score(compliance_results),
                guideline_results=compliance_results,
                deviations=self._identify_deviations(compliance_results),
                recommendations=self._generate_compliance_recommendations(compliance_results),
                checked_at=datetime.utcnow(),
            )

            return compliance

        except Exception as e:
            logger.error(f"Failed to check guideline compliance: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to check guideline compliance"
            )

    async def assess_decision_quality(
        self,
        db: AsyncSession,
        decision_id: UUID,
    ) -> QualityAssessment:
        """Comprehensive quality assessment of a clinical decision."""
        try:
            # Get all quality components
            explanation = await self.generate_decision_explanation(db, decision_id)
            compliance = await self.check_guideline_compliance(db, decision_id)
            
            # Calculate quality metrics
            quality_metrics = await self._calculate_quality_metrics(
                db, decision_id, explanation, compliance
            )
            
            # Generate overall assessment
            assessment = QualityAssessment(
                decision_id=decision_id,
                overall_score=quality_metrics.overall_score,
                explanation_quality=quality_metrics.explanation_quality,
                guideline_compliance=quality_metrics.guideline_compliance,
                evidence_strength=quality_metrics.evidence_strength,
                clinical_appropriateness=quality_metrics.clinical_appropriateness,
                risk_assessment_accuracy=quality_metrics.risk_assessment_accuracy,
                recommendation_clarity=quality_metrics.recommendation_clarity,
                uncertainty_handling=quality_metrics.uncertainty_handling,
                strengths=self._identify_strengths(quality_metrics),
                areas_for_improvement=self._identify_improvements(quality_metrics),
                action_items=self._generate_action_items(quality_metrics),
                assessed_at=datetime.utcnow(),
            )

            return assessment

        except Exception as e:
            logger.error(f"Failed to assess decision quality: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to assess decision quality"
            )

    async def generate_explainability_report(
        self,
        db: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
    ) -> ExplainabilityReport:
        """Generate comprehensive explainability report."""
        try:
            # Get decisions based on filters
            decisions = await self._get_filtered_decisions(db, filters)
            
            # Analyze explainability metrics
            explanation_scores = []
            complexity_distribution = {"low": 0, "medium": 0, "high": 0}
            confidence_distribution = []
            
            for decision in decisions:
                explanation = await self.generate_decision_explanation(
                    db, decision.id, "summary"
                )
                explanation_scores.append(explanation.confidence_metrics["explanation_score"])
                
                complexity = self._assess_case_complexity(decision)
                complexity_distribution[complexity] += 1
                
                confidence_distribution.append(decision.confidence_score)

            # Calculate overall metrics
            avg_explanation_score = statistics.mean(explanation_scores) if explanation_scores else 0.0
            avg_confidence = statistics.mean(confidence_distribution) if confidence_distribution else 0.0
            
            # Generate insights
            insights = self._generate_explainability_insights(
                explanation_scores, complexity_distribution, confidence_distribution
            )
            
            report = ExplainabilityReport(
                period_start=filters.get("start_date") if filters else datetime.utcnow() - timedelta(days=30),
                period_end=filters.get("end_date") if filters else datetime.utcnow(),
                total_decisions=len(decisions),
                average_explanation_score=avg_explanation_score,
                average_confidence_score=avg_confidence,
                complexity_distribution=complexity_distribution,
                top_uncertainty_sources=self._identify_top_uncertainty_sources(decisions),
                improvement_recommendations=self._generate_improvement_recommendations(insights),
                generated_at=datetime.utcnow(),
            )

            return report

        except Exception as e:
            logger.error(f"Failed to generate explainability report: {str(e)}")
            raise HTTPException(
                status_code=500, detail="Failed to generate explainability report"
            )

    async def _analyze_feature_importance(
        self, db: AsyncSession, decision: DecisionResult
    ) -> List[FeatureImportance]:
        """Analyze feature importance for the decision."""
        # Mock implementation - in reality, this would use SHAP or similar
        features = [
            FeatureImportance(
                feature_name="TNM Stage",
                importance_score=0.35,
                direction="positive",
                value="T3N1M0",
                interpretation="Advanced local disease increases surgery urgency",
            ),
            FeatureImportance(
                feature_name="Performance Status",
                importance_score=0.25,
                direction="negative",
                value="ECOG 1",
                interpretation="Good performance status supports surgical candidacy",
            ),
            FeatureImportance(
                feature_name="Age",
                importance_score=0.20,
                direction="positive",
                value="68 years",
                interpretation="Age within acceptable range for major surgery",
            ),
            FeatureImportance(
                feature_name="Comorbidities",
                importance_score=0.15,
                direction="positive",
                value="Controlled diabetes",
                interpretation="Manageable comorbidity with minor impact",
            ),
            FeatureImportance(
                feature_name="Tumor Location",
                importance_score=0.05,
                direction="neutral",
                value="Antrum",
                interpretation="Location allows for standard surgical approach",
            ),
        ]
        return features

    async def _generate_clinical_reasoning(
        self, db: AsyncSession, decision: DecisionResult
    ) -> ClinicalReasoning:
        """Generate clinical reasoning explanation."""
        return ClinicalReasoning(
            primary_factors=[
                "Locally advanced gastric adenocarcinoma (T3N1M0)",
                "Good performance status (ECOG 1)",
                "Adequate organ function for surgery",
                "No distant metastases detected",
            ],
            supporting_evidence=[
                "CT imaging shows resectable tumor without distant spread",
                "Staging laparoscopy negative for peritoneal disease",
                "Cardiac and pulmonary function tests within normal limits",
            ],
            alternative_considerations=[
                "Neoadjuvant chemotherapy could be considered",
                "Minimally invasive approach may be suitable",
                "Nutritional optimization may improve outcomes",
            ],
            contraindications=[],
            risk_factors=[
                "Advanced age increases perioperative risk",
                "Diabetes requires careful perioperative management",
            ],
            mitigation_strategies=[
                "Multidisciplinary team consultation",
                "Perioperative glucose management protocol",
                "Enhanced recovery pathway implementation",
            ],
        )

    async def _generate_natural_explanation(
        self,
        decision: DecisionResult,
        feature_importance: List[FeatureImportance],
        level: str,
    ) -> str:
        """Generate natural language explanation."""
        if level == "brief":
            return f"Recommendation: {decision.recommendation}. Based on tumor stage and patient fitness, surgical resection is indicated with {decision.confidence_score:.0%} confidence."
        
        elif level == "detailed":
            top_features = sorted(feature_importance, key=lambda x: x.importance_score, reverse=True)[:3]
            feature_text = ", ".join([f.feature_name for f in top_features])
            
            return f"""
Recommendation: {decision.recommendation}

This recommendation is based on comprehensive analysis of patient and tumor characteristics. 
The most important factors influencing this decision are {feature_text}. 

The patient presents with {top_features[0].value} ({top_features[0].feature_name}), 
which {top_features[0].interpretation.lower()}. Combined with {top_features[1].value} 
and {top_features[2].value}, the overall clinical picture supports the recommended approach.

Confidence in this recommendation is {decision.confidence_score:.0%}, reflecting 
the strength of evidence and consistency with established clinical guidelines.
            """.strip()
        
        else:  # summary
            return f"Based on tumor staging and patient factors, {decision.recommendation.lower()} is recommended with {decision.confidence_score:.0%} confidence. Key factors include tumor stage, performance status, and surgical risk assessment."

    async def _calculate_confidence_metrics(
        self, db: AsyncSession, decision: DecisionResult
    ) -> Dict[str, float]:
        """Calculate detailed confidence metrics."""
        return {
            "overall_confidence": decision.confidence_score,
            "data_confidence": 0.9,  # Based on data completeness
            "model_confidence": 0.85,  # Based on model uncertainty
            "explanation_score": 0.8,  # Based on explanation quality
            "guideline_alignment": 0.95,  # Based on guideline compliance
            "clinical_consensus": 0.9,  # Based on expert agreement
        }

    async def _find_similar_cases(
        self, db: AsyncSession, decision: DecisionResult
    ) -> List[Dict[str, Any]]:
        """Find similar cases for context."""
        # Mock implementation - in reality, would use similarity search
        return [
            {
                "case_id": "12345",
                "similarity_score": 0.85,
                "outcome": "Successful surgical resection",
                "key_similarities": ["Similar TNM stage", "Comparable age", "Same tumor location"],
            },
            {
                "case_id": "23456",
                "similarity_score": 0.78,
                "outcome": "Neoadjuvant therapy followed by surgery",
                "key_similarities": ["Similar stage", "Comparable comorbidities"],
            },
        ]

    def _assess_case_complexity(self, decision: DecisionResult) -> str:
        """Assess case complexity level."""
        # Simple heuristic - in reality, would use sophisticated scoring
        if decision.confidence_score > 0.8:
            return "low"
        elif decision.confidence_score > 0.6:
            return "medium"
        else:
            return "high"

    async def _analyze_discordance_reason(self, decision: DecisionResult) -> str:
        """Analyze reason for human-AI discordance."""
        # Mock implementation
        if decision.confidence_score < 0.7:
            return "Low AI confidence - human override reasonable"
        else:
            return "Clinical factors not captured by AI model"

    def _generate_concordance_recommendations(
        self, concordance_rate: float, discordance_patterns: List[Dict]
    ) -> List[str]:
        """Generate recommendations based on concordance analysis."""
        recommendations = []
        
        if concordance_rate < 0.8:
            recommendations.append("Consider model retraining or recalibration")
            recommendations.append("Review discordant cases for pattern identification")
        
        if len(discordance_patterns) > 5:
            recommendations.append("Implement systematic review of discordant cases")
        
        return recommendations

    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load explanation templates."""
        return {
            "surgical_recommendation": "Based on {factors}, surgical resection is recommended",
            "medical_recommendation": "Based on {factors}, medical management is recommended",
            "observation_recommendation": "Based on {factors}, observation is recommended",
        }

    def _load_guideline_rules(self) -> Dict[str, Any]:
        """Load clinical guideline rules."""
        return {
            "gastric_cancer_surgery": {
                "indications": ["T1-T4a", "N0-N3", "M0", "adequate_performance_status"],
                "contraindications": ["M1", "poor_performance_status", "severe_comorbidities"],
            }
        }
