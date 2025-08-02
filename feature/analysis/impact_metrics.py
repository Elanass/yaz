"""
Impact Metrics Analyzer for Decision Precision in Surgery

This module provides advanced outcome metrics calculation and analysis
for gastric surgery with FLOT protocol impact assessment, supporting
the Precision Decision Engine with evidence-based outcome predictions.
"""

from typing import Any, Dict, List
from lifelines import KaplanMeierFitter

class ImpactMetricsCalculator:
    """Calculates impact metrics for surgical and medical interventions"""
    
    def calculate_impact_metrics(self, patient_data: Dict[str, Any], procedure_type: str) -> Dict[str, Any]:
        """Calculate comprehensive impact metrics for the given procedure"""
        analyzer = ImpactMetricsAnalyzer()
        
        # Generate core surgical outcomes
        surgical_outcomes = analyzer.analyze_surgical_outcomes(patient_data, procedure_type)
        
        # Calculate quality of life impact if data available
        qol_impact = {}
        if 'surveys' in patient_data:
            qol_impact = analyzer.analyze_quality_of_life_impact(patient_data.get('surveys', []))
        
        # Calculate economic impact if data available
        economic_impact = {}
        if 'cost_data' in patient_data:
            economic_impact = self._calculate_economic_impact(patient_data.get('cost_data', {}))
            
        return {
            'surgical_outcomes': surgical_outcomes,
            'quality_of_life': qol_impact,
            'economic_impact': economic_impact,
            'confidence_interval': self._calculate_confidence_interval(surgical_outcomes),
            'procedure_type': procedure_type
        }
    
    def _calculate_economic_impact(self, cost_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate economic impact metrics"""
        # Basic implementation for MVP
        return {
            'estimated_cost': cost_data.get('estimated_cost', 0),
            'cost_effectiveness': cost_data.get('cost_effectiveness', 'unknown'),
            'resource_utilization': cost_data.get('resource_utilization', {})
        }
    
    def _calculate_confidence_interval(self, outcomes: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence intervals for outcomes"""
        # Basic implementation for MVP
        return {
            'lower_bound': 0.8,
            'upper_bound': 0.95,
            'confidence_level': 0.9
        }

class ImpactMetricsAnalyzer:
    """Analyzes surgical and treatment impact metrics"""

    def analyze_surgical_outcomes(self, patient_data: Dict[str, Any], procedure_type: str) -> Dict[str, Any]:
        """Analyze surgical outcomes including survival and effectiveness"""
        # Generate survival curves for the cohort if provided
        cohort = patient_data.get('cohort', [])
        survival = self.generate_survival_curves(cohort) if cohort else {}
        # Calculate treatment effectiveness from pre/post data
        pre_post = patient_data.get('pre_post_data', [])
        effectiveness = self.calculate_treatment_effectiveness(pre_post)
        return {
            'procedure_type': procedure_type,
            'survival_curve': survival,
            'effectiveness': effectiveness
        }

    def generate_survival_curves(self, cohort_data: List[Dict[str, Any]]) -> Any:
        """Generate Kaplan-Meier survival analysis"""
        # Expect each record to have 'time_to_event' and optional 'event' (1 or 0)
        durations = [rec.get('time_to_event', 0) for rec in cohort_data]
        events = [rec.get('event', 1) for rec in cohort_data]
        kmf = KaplanMeierFitter()
        kmf.fit(durations, events)
        sf = kmf.survival_function_
        return {
            'timeline': sf.index.tolist(),
            'survival_probabilities': sf['KM_estimate'].tolist()
        }

    def calculate_treatment_effectiveness(self, pre_post_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate treatment response rates and effectiveness metrics"""
        total = len(pre_post_data)
        responders = sum(1 for rec in pre_post_data if rec.get('response', False))
        rate = (responders / total) if total > 0 else 0.0
        return {
            'response_rate': round(rate, 3),
            'responders': responders,
            'total': total
        }

    def analyze_quality_of_life_impact(self, patient_surveys: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze QoL scores and functional outcomes"""
        # Compute average quality of life score
        scores = [s.get('score', 0) for s in patient_surveys]
        count = len(scores)
        avg_score = (sum(scores) / count) if count > 0 else 0.0
        return {
            'average_qol_score': round(avg_score, 3),
            'count': count
        }


class PrecisionEngine:
    """
    Decision Precision in Surgery Engine for gastric cancer treatment planning
    with FLOT protocol impact assessment for surgical outcomes.
    
    This engine provides evidence-based analysis and recommendations for
    gastric surgery cases, integrating both retrospective analysis and 
    predictive modeling.
    """
    
    def __init__(self):
        """Initialize the Precision Engine"""
        self.version = "3.0-Precision"
    
    def analyze(self, patient_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze patient records and generate insights
        
        Args:
            patient_records: List of patient data dictionaries
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        for record in patient_records:
            # Generate basic insights for MVP
            patient_insight = {
                'patient_id': record.get('patient_id', 'unknown'),
                'risk_factors': self._extract_risk_factors(record),
                'treatment_recommendations': self._generate_recommendations(record),
                'confidence_score': self._calculate_confidence(record),
                'evidence_sources': self._get_evidence_sources(record)
            }
            
            insights.append(patient_insight)
            
        return insights
    
    def _extract_risk_factors(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract risk factors from patient data"""
        risk_factors = {}
        
        # Basic risk factor extraction for MVP
        if patient_data.get('age', 0) > 65:
            risk_factors['age'] = 'elevated'
        
        comorbidities = patient_data.get('comorbidities', [])
        if comorbidities:
            risk_factors['comorbidities'] = comorbidities
            
        if patient_data.get('bmi', 0) > 30:
            risk_factors['bmi'] = 'elevated'
            
        return risk_factors
    
    def _generate_recommendations(self, patient_data: Dict[str, Any]) -> List[str]:
        """Generate treatment recommendations based on patient data"""
        recommendations = []
        
        # Very basic recommendations for MVP
        if 'gastric_cancer' in patient_data.get('diagnosis', []):
            recommendations.append("Consider FLOT protocol assessment")
        
        risk_factors = self._extract_risk_factors(patient_data)
        if risk_factors.get('age') == 'elevated':
            recommendations.append("Consider geriatric assessment")
        
        return recommendations
    
    def _calculate_confidence(self, patient_data: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis"""
        # Simplified confidence calculation for MVP
        # Data completeness affects confidence
        completeness = sum(1 for k in ['age', 'gender', 'comorbidities', 'diagnosis'] if k in patient_data) / 4
        return round(completeness * 0.9, 2)  # Max 0.9 for MVP
    
    def _get_evidence_sources(self, patient_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Get evidence sources for the analysis"""
        # Placeholder evidence sources for MVP
        return [
            {
                'title': 'FLOT vs. ECF/ECX for perioperative treatment of gastric cancer',
                'journal': 'The Lancet Oncology',
                'year': '2019',
                'url': 'https://example.com/evidence1'
            }
        ]
