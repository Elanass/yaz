"""
Extended Impact Analyzer for detailed outcome and economic analysis
"""

from typing import Any, Dict, List
from lifelines import KaplanMeierFitter

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

    def generate_cost_effectiveness_analysis(self, resource_data: Dict[str, Any]) -> Dict[str, Any]:
        """Economic impact analysis of treatments"""
        cost = resource_data.get('cost', 0.0)
        benefit = resource_data.get('benefit', 0.0)
        ratio = (cost / benefit) if benefit > 0 else None
        return {
            'cost': cost,
            'benefit': benefit,
            'cost_effectiveness_ratio': round(ratio, 3) if ratio is not None else None
        }
