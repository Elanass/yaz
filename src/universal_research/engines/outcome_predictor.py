"""
Outcome Predictor - Enhances existing decision support with research-based predictions
Integrates with existing recommendation system to provide evidence-based insights
"""

import math
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from ....modules.universal_research.adapters.surgify_adapter import \
    SurgifyAdapter


class OutcomePredictor:
    """
    Enhances existing Surgify decision support with research-based outcome prediction
    Integrates seamlessly with current recommendation system
    """

    def __init__(self, surgify_adapter: SurgifyAdapter):
        self.surgify_adapter = surgify_adapter
        self.prediction_models = self._initialize_prediction_models()

    def predict_case_outcome(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predicts outcome for a specific case using historical data
        Enhances existing risk assessment with evidence-based predictions
        """
        # Get similar historical cases for comparison
        similar_cases = self._find_similar_cases(case_data)

        if not similar_cases:
            return self._default_prediction(case_data)

        prediction_result = {
            "primary_prediction": self._calculate_primary_outcome_probability(
                case_data, similar_cases
            ),
            "risk_stratified_prediction": self._calculate_risk_stratified_prediction(
                case_data, similar_cases
            ),
            "complication_predictions": self._predict_complications(
                case_data, similar_cases
            ),
            "timeline_predictions": self._predict_timeline(case_data, similar_cases),
            "resource_predictions": self._predict_resource_requirements(
                case_data, similar_cases
            ),
            "evidence_metrics": self._calculate_evidence_metrics(similar_cases),
            "confidence_intervals": self._calculate_confidence_intervals(
                case_data, similar_cases
            ),
            "contributing_factors": self._identify_contributing_factors(
                case_data, similar_cases
            ),
        }

        return prediction_result

    def enhance_existing_recommendations(
        self, case_data: Dict[str, Any], existing_recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enhances existing Surgify recommendations with research-based insights
        Preserves original recommendations while adding evidence-based enhancements
        """
        enhanced_recommendations = existing_recommendations.copy()

        # Get outcome predictions
        outcome_prediction = self.predict_case_outcome(case_data)

        # Add research-based enhancements
        enhanced_recommendations["evidence_based_insights"] = {
            "outcome_probability": outcome_prediction["primary_prediction"],
            "evidence_strength": outcome_prediction["evidence_metrics"][
                "evidence_level"
            ],
            "similar_cases_analyzed": outcome_prediction["evidence_metrics"][
                "sample_size"
            ],
            "prediction_confidence": outcome_prediction["evidence_metrics"][
                "confidence_level"
            ],
        }

        enhanced_recommendations[
            "risk_mitigation_strategies"
        ] = self._generate_risk_mitigation_strategies(case_data, outcome_prediction)

        enhanced_recommendations[
            "optimization_suggestions"
        ] = self._generate_optimization_suggestions(case_data, outcome_prediction)

        enhanced_recommendations[
            "monitoring_recommendations"
        ] = self._generate_monitoring_recommendations(case_data, outcome_prediction)

        return enhanced_recommendations

    def predict_cohort_outcomes(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Predicts outcomes for an entire cohort
        Useful for research planning and resource allocation
        """
        cohort_predictions = []

        for case in cohort_data:
            case_prediction = self.predict_case_outcome(case)
            cohort_predictions.append(
                {
                    "case_id": case.get("case_id"),
                    "prediction": case_prediction["primary_prediction"],
                    "risk_level": self._categorize_risk_level(
                        case_prediction["primary_prediction"]
                    ),
                }
            )

        return {
            "individual_predictions": cohort_predictions,
            "cohort_summary": self._summarize_cohort_predictions(cohort_predictions),
            "risk_distribution": self._calculate_cohort_risk_distribution(
                cohort_predictions
            ),
            "resource_projections": self._project_cohort_resources(
                cohort_data, cohort_predictions
            ),
        }

    def compare_prediction_accuracy(
        self, historical_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validates prediction accuracy against historical outcomes
        Provides model performance metrics
        """
        accuracy_metrics = {
            "total_cases_evaluated": len(historical_cases),
            "prediction_accuracy": 0.0,
            "sensitivity": 0.0,
            "specificity": 0.0,
            "positive_predictive_value": 0.0,
            "negative_predictive_value": 0.0,
            "area_under_curve": 0.0,
        }

        if not historical_cases:
            return accuracy_metrics

        predictions = []
        actual_outcomes = []

        for case in historical_cases:
            # Make prediction using historical data (excluding outcome)
            case_for_prediction = case.copy()
            case_for_prediction.pop("research_metadata", None)  # Remove outcome info

            prediction = self.predict_case_outcome(case_for_prediction)
            predictions.append(prediction["primary_prediction"]["success_probability"])

            # Get actual outcome
            actual_outcome = case.get("research_metadata", {}).get("outcome_category")
            actual_outcomes.append(
                1.0 if actual_outcome in ["excellent", "good"] else 0.0
            )

        # Calculate accuracy metrics
        accuracy_metrics.update(
            self._calculate_prediction_metrics(predictions, actual_outcomes)
        )

        return accuracy_metrics

    def _find_similar_cases(self, case_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find historically similar cases for comparison"""
        # Define similarity criteria based on case characteristics
        similarity_criteria = {
            "procedure_type": case_data.get("procedure_type"),
            "date_range": (
                datetime.now() - timedelta(days=365 * 2),  # Look back 2 years
                datetime.now(),
            ),
        }

        # Get potential similar cases
        candidate_cases = self.surgify_adapter.get_research_cohort(similarity_criteria)

        # Score similarity and return top matches
        similar_cases = []
        for candidate in candidate_cases:
            similarity_score = self._calculate_similarity_score(case_data, candidate)
            if similarity_score > 0.7:  # Threshold for similarity
                candidate["similarity_score"] = similarity_score
                similar_cases.append(candidate)

        # Sort by similarity score and return top matches
        similar_cases.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similar_cases[:50]  # Limit to top 50 similar cases

    def _calculate_similarity_score(
        self, case_a: Dict[str, Any], case_b: Dict[str, Any]
    ) -> float:
        """Calculate similarity score between two cases"""
        score = 0.0
        max_score = 0.0

        # Procedure type similarity (weight: 0.3)
        if case_a.get("procedure_type") == case_b.get("procedure_type"):
            score += 0.3
        max_score += 0.3

        # Patient demographics similarity (weight: 0.2)
        demo_a = case_a.get("patient_demographics", {})
        demo_b = case_b.get("patient_demographics", {})

        # Age similarity
        age_a = demo_a.get("age")
        age_b = demo_b.get("age")
        if age_a and age_b:
            age_diff = abs(age_a - age_b)
            age_similarity = max(0, 1 - (age_diff / 50))  # Normalize by 50 years
            score += age_similarity * 0.1
        max_score += 0.1

        # Gender similarity
        if demo_a.get("gender") == demo_b.get("gender"):
            score += 0.05
        max_score += 0.05

        # BMI similarity
        bmi_a = demo_a.get("bmi")
        bmi_b = demo_b.get("bmi")
        if bmi_a and bmi_b:
            bmi_diff = abs(bmi_a - bmi_b)
            bmi_similarity = max(0, 1 - (bmi_diff / 20))  # Normalize by 20 BMI units
            score += bmi_similarity * 0.05
        max_score += 0.05

        # Risk score similarity (weight: 0.2)
        risk_a = case_a.get("risk_score")
        risk_b = case_b.get("risk_score")
        if risk_a and risk_b:
            risk_diff = abs(risk_a - risk_b)
            risk_similarity = max(0, 1 - risk_diff)  # Risk scores are 0-1
            score += risk_similarity * 0.2
        max_score += 0.2

        # Complexity similarity (weight: 0.2)
        complex_a = case_a.get("research_metadata", {}).get("complexity_score", 1.0)
        complex_b = case_b.get("research_metadata", {}).get("complexity_score", 1.0)
        complex_diff = abs(complex_a - complex_b)
        complex_similarity = max(
            0, 1 - (complex_diff / 5)
        )  # Normalize by max complexity
        score += complex_similarity * 0.2
        max_score += 0.2

        # Medical history similarity (weight: 0.1)
        history_a = demo_a.get("medical_history", "").lower()
        history_b = demo_b.get("medical_history", "").lower()
        if history_a and history_b:
            # Simple keyword matching for medical history
            keywords_a = set(history_a.split())
            keywords_b = set(history_b.split())
            if keywords_a and keywords_b:
                intersection = len(keywords_a.intersection(keywords_b))
                union = len(keywords_a.union(keywords_b))
                history_similarity = intersection / union if union > 0 else 0
                score += history_similarity * 0.1
        max_score += 0.1

        return score / max_score if max_score > 0 else 0.0

    def _calculate_primary_outcome_probability(
        self, case_data: Dict[str, Any], similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate primary outcome probability based on similar cases"""
        if not similar_cases:
            return self._default_prediction(case_data)["primary_prediction"]

        # Analyze outcomes of similar cases
        successful_outcomes = 0
        total_outcomes = 0
        weighted_success = 0.0
        total_weight = 0.0

        for case in similar_cases:
            outcome = case.get("research_metadata", {}).get("outcome_category")
            weight = case.get("similarity_score", 1.0)

            if outcome:
                total_outcomes += 1
                total_weight += weight

                if outcome in ["excellent", "good"]:
                    successful_outcomes += 1
                    weighted_success += weight

        if total_outcomes == 0:
            return self._default_prediction(case_data)["primary_prediction"]

        # Calculate probability
        raw_probability = successful_outcomes / total_outcomes
        weighted_probability = (
            weighted_success / total_weight if total_weight > 0 else raw_probability
        )

        # Adjust for case-specific factors
        adjusted_probability = self._adjust_probability_for_case_factors(
            weighted_probability, case_data
        )

        return {
            "success_probability": adjusted_probability,
            "raw_probability": raw_probability,
            "weighted_probability": weighted_probability,
            "confidence_level": self._calculate_confidence_level(total_outcomes),
            "sample_size": len(similar_cases),
        }

    def _calculate_risk_stratified_prediction(
        self, case_data: Dict[str, Any], similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate predictions stratified by risk level"""
        case_risk_score = case_data.get("risk_score", 0.5)

        # Stratify similar cases by risk level
        low_risk_cases = [c for c in similar_cases if c.get("risk_score", 0.5) < 0.3]
        moderate_risk_cases = [
            c for c in similar_cases if 0.3 <= c.get("risk_score", 0.5) < 0.7
        ]
        high_risk_cases = [c for c in similar_cases if c.get("risk_score", 0.5) >= 0.7]

        # Determine which stratum the current case belongs to
        if case_risk_score < 0.3:
            primary_stratum = "low_risk"
            primary_cases = low_risk_cases
        elif case_risk_score < 0.7:
            primary_stratum = "moderate_risk"
            primary_cases = moderate_risk_cases
        else:
            primary_stratum = "high_risk"
            primary_cases = high_risk_cases

        return {
            "primary_stratum": primary_stratum,
            "stratum_prediction": self._calculate_stratum_prediction(primary_cases),
            "risk_stratified_outcomes": {
                "low_risk": self._calculate_stratum_prediction(low_risk_cases),
                "moderate_risk": self._calculate_stratum_prediction(
                    moderate_risk_cases
                ),
                "high_risk": self._calculate_stratum_prediction(high_risk_cases),
            },
        }

    def _predict_complications(
        self, case_data: Dict[str, Any], similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict potential complications based on similar cases"""
        risk_factors = case_data.get("research_insights", {}).get("risk_factors", [])

        # Analyze complications in similar cases (would need complication data)
        complication_risk = {
            "overall_complication_risk": self._calculate_complication_risk(
                case_data, similar_cases
            ),
            "specific_risk_factors": self._analyze_specific_risk_factors(risk_factors),
            "mitigation_strategies": self._suggest_complication_mitigation(
                risk_factors
            ),
            "monitoring_priorities": self._prioritize_monitoring(risk_factors),
        }

        return complication_risk

    def _predict_timeline(
        self, case_data: Dict[str, Any], similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict timeline based on similar cases"""
        # Extract duration data from similar cases
        durations = []
        for case in similar_cases:
            start = case.get("actual_start")
            end = case.get("actual_end")
            if start and end:
                duration = (end - start).total_seconds() / 3600  # Hours
                durations.append(duration)

        if not durations:
            return {"message": "Insufficient timeline data for prediction"}

        # Calculate timeline statistics
        avg_duration = sum(durations) / len(durations)
        min_duration = min(durations)
        max_duration = max(durations)

        # Adjust for case complexity
        complexity_factor = case_data.get("research_metadata", {}).get(
            "complexity_score", 1.0
        )
        adjusted_duration = avg_duration * (
            complexity_factor / 2.0
        )  # Normalize by average complexity

        return {
            "predicted_duration_hours": adjusted_duration,
            "duration_range": {
                "minimum": min_duration,
                "maximum": max_duration,
                "average": avg_duration,
            },
            "complexity_adjustment": complexity_factor,
            "confidence_interval": self._calculate_duration_confidence_interval(
                durations
            ),
        }

    def _predict_resource_requirements(
        self, case_data: Dict[str, Any], similar_cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Predict resource requirements based on similar cases"""
        complexity_score = case_data.get("research_metadata", {}).get(
            "complexity_score", 1.0
        )

        # Base resource requirements on complexity and similar cases
        base_resources = {
            "estimated_or_time_hours": self._estimate_or_time(complexity_score),
            "staff_requirements": self._estimate_staff_requirements(complexity_score),
            "equipment_needs": self._estimate_equipment_needs(
                case_data.get("procedure_type")
            ),
            "post_op_monitoring_level": self._estimate_monitoring_level(
                complexity_score
            ),
        }

        return base_resources

    def _initialize_prediction_models(self) -> Dict[str, Any]:
        """Initialize prediction models (placeholder for future ML models)"""
        return {
            "outcome_model": "logistic_regression",  # Placeholder
            "timeline_model": "linear_regression",  # Placeholder
            "risk_model": "random_forest",  # Placeholder
        }

    def _default_prediction(self, case_data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide default prediction when no similar cases are available"""
        risk_score = case_data.get("risk_score", 0.5)
        base_probability = max(0.1, min(0.95, 1.0 - risk_score))

        return {
            "primary_prediction": {
                "success_probability": base_probability,
                "confidence_level": "low",
                "sample_size": 0,
                "message": "Prediction based on risk score only - limited historical data",
            }
        }

    # Additional helper methods would be implemented here...
    def _adjust_probability_for_case_factors(
        self, base_probability: float, case_data: Dict[str, Any]
    ) -> float:
        """Adjust probability based on specific case factors"""
        adjusted = base_probability

        # Adjust for risk factors
        risk_factors = case_data.get("research_insights", {}).get("risk_factors", [])
        risk_adjustment = len(risk_factors) * 0.05  # 5% reduction per risk factor
        adjusted = max(0.1, adjusted - risk_adjustment)

        # Adjust for complexity
        complexity = case_data.get("research_metadata", {}).get("complexity_score", 1.0)
        if complexity > 3.0:
            adjusted = max(0.1, adjusted - 0.1)  # 10% reduction for high complexity

        return min(0.95, adjusted)

    def _calculate_confidence_level(self, sample_size: int) -> str:
        """Calculate confidence level based on sample size"""
        if sample_size >= 100:
            return "high"
        elif sample_size >= 30:
            return "moderate"
        elif sample_size >= 10:
            return "low"
        else:
            return "very_low"
