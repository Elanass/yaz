"""
Cohort Analyzer - Analyzes surgical cohorts from existing cases
Leverages existing Surgify data for research cohort analysis
"""

import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ....modules.universal_research.adapters.domain_mapper import ConceptMapper
from ....modules.universal_research.adapters.surgify_adapter import \
    SurgifyAdapter


class CohortAnalyzer:
    """
    Analyzes surgical cohorts using existing Surgify case data
    Provides research-grade analysis while preserving clinical workflow
    """

    def __init__(
        self, surgify_adapter: SurgifyAdapter, concept_mapper: ConceptMapper = None
    ):
        self.surgify_adapter = surgify_adapter
        self.concept_mapper = concept_mapper or ConceptMapper()

    def analyze_cohort(self, cohort_criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive cohort analysis using existing Surgify data
        Returns research-grade statistical analysis
        """
        # Get cohort data from existing cases
        cohort_data = self.surgify_adapter.get_research_cohort(cohort_criteria)

        if not cohort_data:
            return self._empty_cohort_result()

        analysis_result = {
            "cohort_summary": self._analyze_cohort_summary(cohort_data),
            "demographic_analysis": self._analyze_demographics(cohort_data),
            "procedure_analysis": self._analyze_procedures(cohort_data),
            "outcome_analysis": self._analyze_outcomes(cohort_data),
            "risk_factor_analysis": self._analyze_risk_factors(cohort_data),
            "temporal_analysis": self._analyze_temporal_patterns(cohort_data),
            "comparative_analysis": self._perform_comparative_analysis(cohort_data),
            "statistical_summary": self._generate_statistical_summary(cohort_data),
            "research_quality_metrics": self._assess_research_quality(cohort_data),
        }

        return analysis_result

    def stratify_cohort(
        self, cohort_data: List[Dict[str, Any]], stratification_factors: List[str]
    ) -> Dict[str, Any]:
        """
        Stratifies cohort by specified factors for subgroup analysis
        """
        stratified_groups = defaultdict(list)

        for case in cohort_data:
            strata_key = self._generate_strata_key(case, stratification_factors)
            stratified_groups[strata_key].append(case)

        stratification_result = {}
        for strata_key, group_cases in stratified_groups.items():
            stratification_result[strata_key] = {
                "count": len(group_cases),
                "percentage": (len(group_cases) / len(cohort_data)) * 100,
                "summary_statistics": self._calculate_group_statistics(group_cases),
                "outcome_distribution": self._analyze_group_outcomes(group_cases),
            }

        return {
            "stratification_factors": stratification_factors,
            "total_cohort_size": len(cohort_data),
            "stratified_groups": stratification_result,
            "stratification_quality": self._assess_stratification_quality(
                stratified_groups
            ),
        }

    def compare_cohorts(
        self, cohort_a_criteria: Dict[str, Any], cohort_b_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compares two cohorts for research analysis
        """
        cohort_a = self.surgify_adapter.get_research_cohort(cohort_a_criteria)
        cohort_b = self.surgify_adapter.get_research_cohort(cohort_b_criteria)

        return {
            "cohort_a_summary": self._analyze_cohort_summary(cohort_a),
            "cohort_b_summary": self._analyze_cohort_summary(cohort_b),
            "comparative_statistics": self._compare_cohort_statistics(
                cohort_a, cohort_b
            ),
            "outcome_comparison": self._compare_outcomes(cohort_a, cohort_b),
            "demographic_comparison": self._compare_demographics(cohort_a, cohort_b),
            "statistical_significance": self._assess_statistical_significance(
                cohort_a, cohort_b
            ),
        }

    def identify_research_opportunities(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Identifies research opportunities from cohort analysis
        """
        return {
            "sample_size_adequacy": self._assess_sample_size_adequacy(cohort_data),
            "data_completeness": self._assess_data_completeness(cohort_data),
            "research_questions": self._suggest_research_questions(cohort_data),
            "publication_potential": self._assess_publication_potential(cohort_data),
            "collaboration_opportunities": self._identify_collaboration_opportunities(
                cohort_data
            ),
            "follow_up_recommendations": self._suggest_follow_up_studies(cohort_data),
        }

    def _analyze_cohort_summary(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate cohort summary statistics"""
        if not cohort_data:
            return {"total_cases": 0}

        return {
            "total_cases": len(cohort_data),
            "date_range": self._calculate_date_range(cohort_data),
            "unique_patients": len(
                set(
                    case.get("patient_id")
                    for case in cohort_data
                    if case.get("patient_id")
                )
            ),
            "unique_procedures": len(
                set(
                    case.get("procedure_type")
                    for case in cohort_data
                    if case.get("procedure_type")
                )
            ),
            "unique_surgeons": len(
                set(
                    case.get("provider_info", {}).get("surgeon_id")
                    for case in cohort_data
                )
            ),
            "completion_rate": self._calculate_completion_rate(cohort_data),
            "data_quality_score": self._calculate_data_quality_score(cohort_data),
        }

    def _analyze_demographics(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze demographic characteristics"""
        ages = [
            case.get("patient_demographics", {}).get("age")
            for case in cohort_data
            if case.get("patient_demographics", {}).get("age")
        ]
        genders = [
            case.get("patient_demographics", {}).get("gender")
            for case in cohort_data
            if case.get("patient_demographics", {}).get("gender")
        ]
        bmis = [
            case.get("patient_demographics", {}).get("bmi")
            for case in cohort_data
            if case.get("patient_demographics", {}).get("bmi")
        ]

        return {
            "age_statistics": self._calculate_numeric_statistics(ages)
            if ages
            else None,
            "gender_distribution": self._calculate_categorical_distribution(genders)
            if genders
            else None,
            "bmi_statistics": self._calculate_numeric_statistics(bmis)
            if bmis
            else None,
            "age_groups": self._categorize_age_groups(ages) if ages else None,
        }

    def _analyze_procedures(self, cohort_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze procedure characteristics"""
        procedures = [
            case.get("procedure_type")
            for case in cohort_data
            if case.get("procedure_type")
        ]
        complexities = [
            case.get("research_metadata", {}).get("complexity_score")
            for case in cohort_data
        ]

        return {
            "procedure_distribution": self._calculate_categorical_distribution(
                procedures
            ),
            "complexity_statistics": self._calculate_numeric_statistics(
                [c for c in complexities if c is not None]
            ),
            "specialty_distribution": self._analyze_specialty_distribution(cohort_data),
            "approach_distribution": self._analyze_approach_distribution(cohort_data),
        }

    def _analyze_outcomes(self, cohort_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze outcome characteristics"""
        outcomes = [
            case.get("research_metadata", {}).get("outcome_category")
            for case in cohort_data
        ]
        risk_scores = [
            case.get("risk_score")
            for case in cohort_data
            if case.get("risk_score") is not None
        ]
        outcome_probabilities = [
            case.get("research_insights", {}).get("outcome_probability")
            for case in cohort_data
        ]

        return {
            "outcome_distribution": self._calculate_categorical_distribution(outcomes),
            "risk_score_statistics": self._calculate_numeric_statistics(risk_scores)
            if risk_scores
            else None,
            "success_rate": self._calculate_success_rate(outcomes),
            "outcome_probability_statistics": self._calculate_numeric_statistics(
                [p for p in outcome_probabilities if p is not None]
            ),
        }

    def _analyze_risk_factors(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze risk factor patterns"""
        all_risk_factors = []
        for case in cohort_data:
            risk_factors = case.get("research_insights", {}).get("risk_factors", [])
            all_risk_factors.extend(risk_factors)

        risk_factor_counts = defaultdict(int)
        for factor in all_risk_factors:
            risk_factor_counts[factor] += 1

        return {
            "risk_factor_prevalence": dict(risk_factor_counts),
            "risk_factor_distribution": {
                factor: (count / len(cohort_data)) * 100
                for factor, count in risk_factor_counts.items()
            },
            "average_risk_factors_per_case": len(all_risk_factors) / len(cohort_data)
            if cohort_data
            else 0,
            "high_risk_cases": len(
                [case for case in cohort_data if case.get("risk_score", 0) > 0.7]
            ),
        }

    def _analyze_temporal_patterns(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze temporal patterns in the cohort"""
        scheduled_dates = [
            case.get("scheduled_date")
            for case in cohort_data
            if case.get("scheduled_date")
        ]
        durations = []

        for case in cohort_data:
            start = case.get("actual_start")
            end = case.get("actual_end")
            if start and end:
                duration = (end - start).total_seconds() / 3600  # Hours
                durations.append(duration)

        return {
            "temporal_distribution": self._analyze_temporal_distribution(
                scheduled_dates
            ),
            "duration_statistics": self._calculate_numeric_statistics(durations)
            if durations
            else None,
            "seasonal_patterns": self._analyze_seasonal_patterns(scheduled_dates),
            "scheduling_patterns": self._analyze_scheduling_patterns(scheduled_dates),
        }

    def _perform_comparative_analysis(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comparative analysis within the cohort"""
        # Compare by procedure complexity
        low_complexity = [
            case
            for case in cohort_data
            if case.get("research_metadata", {}).get("complexity_score", 1.0) < 2.0
        ]
        high_complexity = [
            case
            for case in cohort_data
            if case.get("research_metadata", {}).get("complexity_score", 1.0) >= 3.0
        ]

        return {
            "complexity_comparison": {
                "low_complexity_outcomes": self._analyze_group_outcomes(low_complexity),
                "high_complexity_outcomes": self._analyze_group_outcomes(
                    high_complexity
                ),
                "complexity_impact": self._assess_complexity_impact(
                    low_complexity, high_complexity
                ),
            },
            "risk_stratified_comparison": self._compare_risk_stratified_groups(
                cohort_data
            ),
            "procedure_type_comparison": self._compare_procedure_types(cohort_data),
        }

    def _generate_statistical_summary(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate comprehensive statistical summary"""
        return {
            "descriptive_statistics": self._calculate_descriptive_statistics(
                cohort_data
            ),
            "correlation_analysis": self._perform_correlation_analysis(cohort_data),
            "confidence_intervals": self._calculate_confidence_intervals(cohort_data),
            "effect_sizes": self._calculate_effect_sizes(cohort_data),
        }

    def _assess_research_quality(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Assess quality of cohort for research purposes"""
        return {
            "sample_size": len(cohort_data),
            "power_analysis": self._perform_power_analysis(cohort_data),
            "data_completeness_score": self._calculate_data_completeness_score(
                cohort_data
            ),
            "bias_assessment": self._assess_potential_biases(cohort_data),
            "generalizability_score": self._assess_generalizability(cohort_data),
            "publication_readiness": self._assess_publication_readiness(cohort_data),
        }

    def _empty_cohort_result(self) -> Dict[str, Any]:
        """Return empty result structure for no data scenarios"""
        return {
            "cohort_summary": {"total_cases": 0},
            "message": "No cases found matching the specified criteria",
            "suggestions": [
                "Broaden the inclusion criteria",
                "Extend the date range",
                "Consider different procedure types",
            ],
        }

    # Helper methods for statistical calculations
    def _calculate_numeric_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calculate statistics for numeric values"""
        if not values:
            return {}

        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "q1": statistics.quantiles(values, n=4)[0] if len(values) >= 4 else None,
            "q3": statistics.quantiles(values, n=4)[2] if len(values) >= 4 else None,
        }

    def _calculate_categorical_distribution(self, values: List[str]) -> Dict[str, Any]:
        """Calculate distribution for categorical values"""
        if not values:
            return {}

        counts = defaultdict(int)
        for value in values:
            if value:
                counts[value] += 1

        total = len(values)
        return {
            "counts": dict(counts),
            "percentages": {k: (v / total) * 100 for k, v in counts.items()},
            "most_common": max(counts.items(), key=lambda x: x[1])[0]
            if counts
            else None,
        }

    def _generate_strata_key(self, case: Dict[str, Any], factors: List[str]) -> str:
        """Generate stratification key for a case"""
        key_parts = []
        for factor in factors:
            if factor == "age_group":
                age = case.get("patient_demographics", {}).get("age")
                key_parts.append(self._categorize_age(age) if age else "unknown_age")
            elif factor == "risk_level":
                risk_score = case.get("risk_score", 0.5)
                key_parts.append(self._categorize_risk(risk_score))
            elif factor == "procedure_type":
                key_parts.append(case.get("procedure_type", "unknown_procedure"))
            elif factor == "complexity_level":
                complexity = case.get("research_metadata", {}).get(
                    "complexity_score", 1.0
                )
                key_parts.append(self._categorize_complexity(complexity))
            else:
                key_parts.append("unknown")

        return "_".join(key_parts)

    def _categorize_age(self, age: int) -> str:
        """Categorize age into groups"""
        if age < 18:
            return "pediatric"
        elif age < 65:
            return "adult"
        else:
            return "elderly"

    def _categorize_risk(self, risk_score: float) -> str:
        """Categorize risk score"""
        if risk_score < 0.3:
            return "low_risk"
        elif risk_score < 0.7:
            return "moderate_risk"
        else:
            return "high_risk"

    def _categorize_complexity(self, complexity_score: float) -> str:
        """Categorize complexity score"""
        if complexity_score < 2.0:
            return "low_complexity"
        elif complexity_score < 3.5:
            return "moderate_complexity"
        else:
            return "high_complexity"

    def _calculate_completion_rate(self, cohort_data: List[Dict[str, Any]]) -> float:
        """Calculate completion rate"""
        completed = len(
            [case for case in cohort_data if case.get("status") == "completed"]
        )
        return (completed / len(cohort_data)) * 100 if cohort_data else 0

    def _calculate_success_rate(self, outcomes: List[str]) -> float:
        """Calculate success rate from outcomes"""
        if not outcomes:
            return 0

        successful_outcomes = ["excellent", "good"]
        successful = len(
            [outcome for outcome in outcomes if outcome in successful_outcomes]
        )
        return (successful / len(outcomes)) * 100

    def _calculate_date_range(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Calculate date range of the cohort"""
        dates = []
        for case in cohort_data:
            if case.get("scheduled_date"):
                dates.append(case["scheduled_date"])
            elif case.get("actual_start"):
                dates.append(case["actual_start"])

        if not dates:
            return {"message": "No date information available"}

        return {
            "earliest": min(dates),
            "latest": max(dates),
            "span_days": (max(dates) - min(dates)).days,
        }

    # Additional helper methods would be implemented here...
