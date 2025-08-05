"""
Legacy Bridge - Bridges existing APIs with new research APIs
Ensures backward compatibility while adding research capabilities
"""

from typing import Dict, List, Any, Optional
from fastapi import HTTPException

from surgify.core.services.case_service import CaseService
from surgify.api.v1.cases import list_cases, get_case
from .surgify_adapter import SurgifyAdapter


class LegacyBridge:
    """
    Bridges existing Surgify APIs with new research capabilities
    Maintains 100% backward compatibility while adding research features
    """

    def __init__(self, case_service: CaseService, surgify_adapter: SurgifyAdapter):
        self.case_service = case_service
        self.surgify_adapter = surgify_adapter

    def enhance_case_response(
        self, case_data: Dict[str, Any], include_research: bool = False
    ) -> Dict[str, Any]:
        """
        Enhances existing case response with optional research data
        Preserves original structure, adds research insights if requested
        """
        if not include_research:
            return case_data  # Return unchanged for backward compatibility

        # Add research enhancements to existing case data
        enhanced_data = case_data.copy()

        try:
            research_data = self.surgify_adapter.enhance_existing_case_data(
                case_data.get("case_number")
            )
            if research_data:
                enhanced_data["research_insights"] = research_data.get(
                    "research_insights", {}
                )
                enhanced_data["research_metadata"] = research_data.get(
                    "research_metadata", {}
                )
        except Exception as e:
            # Fail gracefully - return original data if research enhancement fails
            enhanced_data[
                "research_error"
            ] = f"Research enhancement unavailable: {str(e)}"

        return enhanced_data

    def enhance_cases_list_response(
        self, cases_data: List[Dict[str, Any]], include_research: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Enhances existing cases list with optional research data
        Preserves original list structure, adds research insights if requested
        """
        if not include_research:
            return cases_data  # Return unchanged for backward compatibility

        enhanced_cases = []
        for case_data in cases_data:
            enhanced_case = self.enhance_case_response(case_data, include_research=True)
            enhanced_cases.append(enhanced_case)

        return enhanced_cases

    def enhance_dashboard_response(
        self, dashboard_data: Dict[str, Any], include_research: bool = False
    ) -> Dict[str, Any]:
        """
        Enhances existing dashboard response with optional research metrics
        Preserves original dashboard structure, adds research metrics if requested
        """
        if not include_research:
            return dashboard_data  # Return unchanged for backward compatibility

        enhanced_data = dashboard_data.copy()

        try:
            # Add research metrics to existing dashboard
            research_metrics = self._calculate_research_metrics()
            enhanced_data["research_metrics"] = research_metrics
        except Exception as e:
            # Fail gracefully
            enhanced_data[
                "research_metrics_error"
            ] = f"Research metrics unavailable: {str(e)}"

        return enhanced_data

    def enhance_recommendations_response(
        self, recommendations_data: Dict[str, Any], include_research: bool = False
    ) -> Dict[str, Any]:
        """
        Enhances existing recommendations with optional research-based insights
        Preserves original recommendations, adds research-backed suggestions if requested
        """
        if not include_research:
            return recommendations_data  # Return unchanged for backward compatibility

        enhanced_data = recommendations_data.copy()

        try:
            # Add research-based recommendations to existing ones
            case_id = recommendations_data.get("case_id")
            if case_id:
                research_recommendations = self._generate_research_recommendations(
                    case_id
                )
                enhanced_data["research_recommendations"] = research_recommendations
        except Exception as e:
            # Fail gracefully
            enhanced_data[
                "research_recommendations_error"
            ] = f"Research recommendations unavailable: {str(e)}"

        return enhanced_data

    def bridge_existing_endpoint(
        self, endpoint_name: str, original_response: Any, request_params: Dict[str, Any]
    ) -> Any:
        """
        Generic bridge for any existing endpoint
        Adds research enhancements while preserving original behavior
        """
        # Check if research enhancements are requested
        include_research = request_params.get("include_research", False)

        if not include_research:
            return original_response  # Return unchanged

        # Apply appropriate enhancement based on endpoint
        if endpoint_name == "get_case":
            return self.enhance_case_response(original_response, include_research=True)
        elif endpoint_name == "list_cases":
            return self.enhance_cases_list_response(
                original_response, include_research=True
            )
        elif endpoint_name == "get_dashboard":
            return self.enhance_dashboard_response(
                original_response, include_research=True
            )
        elif endpoint_name == "get_recommendations":
            return self.enhance_recommendations_response(
                original_response, include_research=True
            )
        else:
            # For unrecognized endpoints, just return original response
            return original_response

    def validate_backward_compatibility(
        self, endpoint_name: str, original_response: Any, enhanced_response: Any
    ) -> bool:
        """
        Validates that enhanced response maintains backward compatibility
        Ensures all original fields are preserved
        """
        try:
            if isinstance(original_response, dict) and isinstance(
                enhanced_response, dict
            ):
                # Check that all original keys are preserved
                for key in original_response.keys():
                    if key not in enhanced_response:
                        return False

                    # Check that original values are unchanged (for non-research fields)
                    if key not in [
                        "research_insights",
                        "research_metadata",
                        "research_metrics",
                        "research_recommendations",
                    ]:
                        if original_response[key] != enhanced_response[key]:
                            return False

                return True

            elif isinstance(original_response, list) and isinstance(
                enhanced_response, list
            ):
                # Check list length is preserved
                if len(original_response) != len(enhanced_response):
                    return False

                # Check each item maintains compatibility
                for orig_item, enh_item in zip(original_response, enhanced_response):
                    if not self.validate_backward_compatibility(
                        endpoint_name, orig_item, enh_item
                    ):
                        return False

                return True

            else:
                # For other types, they should be identical if no research enhancement
                return original_response == enhanced_response

        except Exception:
            return False

    def _calculate_research_metrics(self) -> Dict[str, Any]:
        """Calculate research metrics for dashboard enhancement"""
        try:
            # Get research cohort statistics
            total_cases = self.case_service.get_total_cases_count()
            research_eligible_criteria = {"status": "completed"}  # Example criteria
            research_cohort = self.surgify_adapter.get_research_cohort(
                research_eligible_criteria
            )

            return {
                "total_research_eligible_cases": len(research_cohort),
                "research_coverage_percentage": (
                    len(research_cohort) / total_cases * 100
                )
                if total_cases > 0
                else 0,
                "unique_procedure_types": len(
                    set(
                        case.get("procedure_type")
                        for case in research_cohort
                        if case.get("procedure_type")
                    )
                ),
                "average_complexity_score": self._calculate_average_complexity(
                    research_cohort
                ),
                "risk_distribution": self._calculate_risk_distribution(research_cohort),
            }
        except Exception as e:
            return {"error": f"Failed to calculate research metrics: {str(e)}"}

    def _generate_research_recommendations(self, case_id: str) -> Dict[str, Any]:
        """Generate research-based recommendations for a specific case"""
        try:
            enhanced_case_data = self.surgify_adapter.enhance_existing_case_data(
                case_id
            )
            if not enhanced_case_data:
                return {"error": "Case not found for research analysis"}

            research_insights = enhanced_case_data.get("research_insights", {})

            recommendations = {
                "evidence_based_suggestions": [],
                "similar_cases_insights": {},
                "risk_mitigation_strategies": [],
                "outcome_optimization_tips": [],
            }

            # Generate recommendations based on research insights
            if research_insights.get("similar_cases_count", 0) > 10:
                recommendations["evidence_based_suggestions"].append(
                    f"Based on {research_insights['similar_cases_count']} similar cases, "
                    f"expected success probability is {research_insights.get('outcome_probability', 0.75):.1%}"
                )

            risk_factors = research_insights.get("risk_factors", [])
            if risk_factors:
                recommendations["risk_mitigation_strategies"] = [
                    f"Consider additional monitoring for {factor.replace('_', ' ')}"
                    for factor in risk_factors
                ]

            evidence_level = research_insights.get("evidence_level")
            if evidence_level == "high":
                recommendations["evidence_based_suggestions"].append(
                    "High evidence base available - consider following established protocols"
                )
            elif evidence_level == "low":
                recommendations["evidence_based_suggestions"].append(
                    "Limited evidence base - consider contributing case data to research"
                )

            return recommendations

        except Exception as e:
            return {"error": f"Failed to generate research recommendations: {str(e)}"}

    def _calculate_average_complexity(
        self, research_cohort: List[Dict[str, Any]]
    ) -> float:
        """Calculate average complexity score for research cohort"""
        complexity_scores = [
            case.get("research_metadata", {}).get("complexity_score", 1.0)
            for case in research_cohort
        ]

        if complexity_scores:
            return sum(complexity_scores) / len(complexity_scores)

        return 1.0

    def _calculate_risk_distribution(
        self, research_cohort: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate risk level distribution for research cohort"""
        risk_distribution = {"low": 0, "moderate": 0, "high": 0}

        for case in research_cohort:
            risk_score = case.get("risk_score", 0.5)
            if risk_score < 0.3:
                risk_distribution["low"] += 1
            elif risk_score < 0.7:
                risk_distribution["moderate"] += 1
            else:
                risk_distribution["high"] += 1

        return risk_distribution
