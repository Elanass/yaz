"""
API Enhancer - Adds research endpoints to existing FastAPI application
Preserves all existing functionality while adding research capabilities
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from surgify.core.database import get_db
from surgify.core.models.user import User
from surgify.core.services.auth_service import get_current_user

from ....modules.universal_research.adapters.legacy_bridge import LegacyBridge
from ....modules.universal_research.adapters.surgify_adapter import \
    SurgifyAdapter
from ....modules.universal_research.engines.cohort_analyzer import \
    CohortAnalyzer
from ....modules.universal_research.engines.outcome_predictor import \
    OutcomePredictor
from ....modules.universal_research.engines.research_generator import \
    ResearchGenerator


# Global dependency functions for FastAPI injection
def get_surgify_adapter(db: Session = Depends(get_db)) -> SurgifyAdapter:
    return SurgifyAdapter(db)


def get_cohort_analyzer(
    adapter: SurgifyAdapter = Depends(get_surgify_adapter),
) -> CohortAnalyzer:
    return CohortAnalyzer(adapter)


def get_outcome_predictor(
    adapter: SurgifyAdapter = Depends(get_surgify_adapter),
) -> OutcomePredictor:
    return OutcomePredictor(adapter)


def get_research_generator(
    adapter: SurgifyAdapter = Depends(get_surgify_adapter),
    analyzer: CohortAnalyzer = Depends(get_cohort_analyzer),
    predictor: OutcomePredictor = Depends(get_outcome_predictor),
) -> ResearchGenerator:
    return ResearchGenerator(adapter, analyzer, predictor)


def get_legacy_bridge(
    adapter: SurgifyAdapter = Depends(get_surgify_adapter),
) -> LegacyBridge:
    # This would need the actual case service
    from surgify.core.services.case_service import CaseService

    case_service = CaseService()  # This would be properly injected
    return LegacyBridge(case_service, adapter)


class ResearchAPIEnhancer:
    """
    Enhances existing Surgify FastAPI application with research endpoints
    Maintains complete backward compatibility with existing APIs
    """

    def __init__(self):
        self.router = APIRouter(prefix="/api/v1/research", tags=["research"])
        self._register_research_endpoints()

    def _register_research_endpoints(self):
        """Register all research endpoints"""

        @self.router.get("/cohort/analyze")
        async def analyze_cohort(
            procedure_type: Optional[str] = Query(
                None, description="Filter by procedure type"
            ),
            date_from: Optional[str] = Query(
                None, description="Start date (YYYY-MM-DD)"
            ),
            date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
            status: Optional[str] = Query(None, description="Case status filter"),
            min_cases: int = Query(10, description="Minimum cases required"),
            analyzer: CohortAnalyzer = Depends(get_cohort_analyzer),
            current_user: User = Depends(get_current_user),
        ):
            """
            Analyze surgical cohort for research purposes
            NEW ENDPOINT - Provides research analysis of existing case data
            """
            try:
                # Build cohort criteria from query parameters
                criteria = {}
                if procedure_type:
                    criteria["procedure_type"] = procedure_type
                if status:
                    criteria["status"] = status
                if date_from and date_to:
                    from datetime import datetime

                    criteria["date_range"] = (
                        datetime.fromisoformat(date_from),
                        datetime.fromisoformat(date_to),
                    )

                # Perform cohort analysis
                analysis_result = analyzer.analyze_cohort(criteria)

                # Check minimum cases requirement
                total_cases = analysis_result.get("cohort_summary", {}).get(
                    "total_cases", 0
                )
                if total_cases < min_cases:
                    return {
                        "message": f"Insufficient cases found ({total_cases} < {min_cases} required)",
                        "suggestions": [
                            "Broaden criteria",
                            "Extend date range",
                            "Lower minimum threshold",
                        ],
                    }

                return {
                    "status": "success",
                    "analysis": analysis_result,
                    "metadata": {
                        "analyzed_by": current_user.username,
                        "analysis_date": datetime.now().isoformat(),
                        "criteria_used": criteria,
                    },
                }

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Cohort analysis failed: {str(e)}"
                )

        @self.router.get("/predict/case-outcome")
        async def predict_case_outcome(
            case_id: str = Query(..., description="Case number to analyze"),
            include_confidence: bool = Query(
                True, description="Include confidence intervals"
            ),
            predictor: OutcomePredictor = Depends(get_outcome_predictor),
            adapter: SurgifyAdapter = Depends(get_surgify_adapter),
            current_user: User = Depends(get_current_user),
        ):
            """
            Predict outcome for a specific case using historical data
            NEW ENDPOINT - Enhances existing case management with predictive insights
            """
            try:
                # Get case data for prediction
                case_data = adapter.enhance_existing_case_data(case_id)
                if not case_data:
                    raise HTTPException(status_code=404, detail="Case not found")

                # Generate prediction
                prediction = predictor.predict_case_outcome(case_data)

                return {
                    "status": "success",
                    "case_id": case_id,
                    "prediction": prediction,
                    "metadata": {
                        "predicted_by": current_user.username,
                        "prediction_date": datetime.now().isoformat(),
                        "model_version": "1.0",
                    },
                }

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Prediction failed: {str(e)}"
                )

        @self.router.post("/generate/research-study")
        async def generate_research_study(
            study_request: Dict[str, Any],
            generator: ResearchGenerator = Depends(get_research_generator),
            current_user: User = Depends(get_current_user),
        ):
            """
            Generate complete research study from existing case data
            NEW ENDPOINT - Creates publication-ready research from clinical data
            """
            try:
                # Validate study request
                required_fields = ["study_title", "inclusion_criteria"]
                for field in required_fields:
                    if field not in study_request:
                        raise HTTPException(
                            status_code=400, detail=f"Missing required field: {field}"
                        )

                # Generate research study
                study = generator.generate_research_study(
                    study_request["inclusion_criteria"]
                )

                # Add user metadata
                study["metadata"] = {
                    "generated_by": current_user.username,
                    "generation_date": datetime.now().isoformat(),
                    "study_title": study_request["study_title"],
                    "request_parameters": study_request,
                }

                return {"status": "success", "study": study}

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Research study generation failed: {str(e)}",
                )

        @self.router.post("/generate/case-series")
        async def generate_case_series(
            series_request: Dict[str, Any],
            generator: ResearchGenerator = Depends(get_research_generator),
            current_user: User = Depends(get_current_user),
        ):
            """
            Generate case series report from selected cases
            NEW ENDPOINT - Creates case series publications from clinical cases
            """
            try:
                # Generate case series
                case_series = generator.generate_case_series(
                    series_request.get("selection_criteria", {})
                )

                # Add metadata
                case_series["metadata"] = {
                    "generated_by": current_user.username,
                    "generation_date": datetime.now().isoformat(),
                    "series_title": series_request.get(
                        "series_title", "Generated Case Series"
                    ),
                }

                return {"status": "success", "case_series": case_series}

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Case series generation failed: {str(e)}"
                )

        @self.router.post("/generate/clinical-guidelines")
        async def generate_clinical_guidelines(
            guidelines_request: Dict[str, Any],
            generator: ResearchGenerator = Depends(get_research_generator),
            current_user: User = Depends(get_current_user),
        ):
            """
            Generate evidence-based clinical guidelines from case outcomes
            NEW ENDPOINT - Creates clinical protocols from successful cases
            """
            try:
                # Generate guidelines
                guidelines = generator.generate_clinical_guidelines(
                    guidelines_request.get("criteria", {})
                )

                # Add metadata
                guidelines["metadata"] = {
                    "generated_by": current_user.username,
                    "generation_date": datetime.now().isoformat(),
                    "guideline_scope": guidelines_request.get("scope", "General"),
                }

                return {"status": "success", "guidelines": guidelines}

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Guidelines generation failed: {str(e)}"
                )

        @self.router.get("/data/research-opportunities")
        async def identify_research_opportunities(
            analyzer: CohortAnalyzer = Depends(get_cohort_analyzer),
            adapter: SurgifyAdapter = Depends(get_surgify_adapter),
            current_user: User = Depends(get_current_user),
        ):
            """
            Identify research opportunities from existing data
            NEW ENDPOINT - Discovers research potential in clinical database
            """
            try:
                # Get all available data for analysis
                all_data_criteria = {}  # Get all cases
                cohort_data = adapter.get_research_cohort(all_data_criteria)

                # Identify opportunities
                opportunities = analyzer.identify_research_opportunities(cohort_data)

                return {
                    "status": "success",
                    "opportunities": opportunities,
                    "metadata": {
                        "analyzed_by": current_user.username,
                        "analysis_date": datetime.now().isoformat(),
                        "total_cases_analyzed": len(cohort_data),
                    },
                }

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Opportunity analysis failed: {str(e)}"
                )

        @self.router.get("/statistics/research-metrics")
        async def get_research_metrics(
            adapter: SurgifyAdapter = Depends(get_surgify_adapter),
            current_user: User = Depends(get_current_user),
        ):
            """
            Get comprehensive research metrics from clinical database
            NEW ENDPOINT - Provides research dashboard metrics
            """
            try:
                # Get research-ready cases
                research_criteria = {"status": "completed"}
                research_cohort = adapter.get_research_cohort(research_criteria)

                # Calculate research metrics
                metrics = {
                    "total_research_eligible_cases": len(research_cohort),
                    "procedure_type_distribution": self._calculate_procedure_distribution(
                        research_cohort
                    ),
                    "outcome_completeness": self._calculate_outcome_completeness(
                        research_cohort
                    ),
                    "data_quality_metrics": self._calculate_data_quality_metrics(
                        research_cohort
                    ),
                    "research_potential_score": self._calculate_research_potential(
                        research_cohort
                    ),
                }

                return {
                    "status": "success",
                    "metrics": metrics,
                    "metadata": {
                        "calculated_by": current_user.username,
                        "calculation_date": datetime.now().isoformat(),
                    },
                }

            except Exception as e:
                raise HTTPException(
                    status_code=500, detail=f"Metrics calculation failed: {str(e)}"
                )

    def enhance_existing_endpoints(self, app):
        """
        Enhance existing endpoints with optional research features
        Maintains backward compatibility while adding research capabilities
        """
        # This would be called to add research enhancements to existing endpoints
        # Implementation would depend on the specific existing endpoint structure

        # Example: Enhance existing case endpoint
        @app.middleware("http")
        async def add_research_enhancements(request, call_next):
            """Middleware to add research enhancements to existing endpoints"""
            response = await call_next(request)

            # Check if research enhancement is requested
            include_research = (
                request.query_params.get("include_research", "false").lower() == "true"
            )

            if include_research and hasattr(response, "body"):
                # This is a simplified example - actual implementation would be more sophisticated
                pass

            return response

    def get_router(self) -> APIRouter:
        """Get the research router to include in the main FastAPI app"""
        return self.router

    # Helper methods for endpoint implementations
    def _calculate_procedure_distribution(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate distribution of procedure types"""
        distribution = {}
        for case in cohort_data:
            procedure_type = case.get("procedure_type", "unknown")
            distribution[procedure_type] = distribution.get(procedure_type, 0) + 1
        return distribution

    def _calculate_outcome_completeness(
        self, cohort_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate percentage of cases with complete outcome data"""
        if not cohort_data:
            return 0.0

        complete_outcomes = len(
            [
                case
                for case in cohort_data
                if case.get("research_metadata", {}).get("outcome_category")
            ]
        )

        return (complete_outcomes / len(cohort_data)) * 100

    def _calculate_data_quality_metrics(
        self, cohort_data: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """Calculate data quality metrics"""
        if not cohort_data:
            return {}

        total_cases = len(cohort_data)

        metrics = {
            "demographic_completeness": len(
                [
                    case
                    for case in cohort_data
                    if case.get("patient_demographics", {}).get("age")
                ]
            )
            / total_cases
            * 100,
            "procedure_documentation": len(
                [case for case in cohort_data if case.get("procedure_type")]
            )
            / total_cases
            * 100,
            "outcome_documentation": self._calculate_outcome_completeness(cohort_data),
        }

        return metrics

    def _calculate_research_potential(self, cohort_data: List[Dict[str, Any]]) -> float:
        """Calculate overall research potential score"""
        if not cohort_data:
            return 0.0

        # Calculate based on sample size, data quality, and diversity
        sample_size_score = min(1.0, len(cohort_data) / 100)  # Normalize to 100 cases

        data_quality_metrics = self._calculate_data_quality_metrics(cohort_data)
        quality_score = (
            sum(data_quality_metrics.values()) / len(data_quality_metrics) / 100
            if data_quality_metrics
            else 0
        )

        procedure_diversity = len(
            set(
                case.get("procedure_type")
                for case in cohort_data
                if case.get("procedure_type")
            )
        )
        diversity_score = min(
            1.0, procedure_diversity / 10
        )  # Normalize to 10 different procedures

        # Weighted average
        research_potential = (
            sample_size_score * 0.4 + quality_score * 0.4 + diversity_score * 0.2
        ) * 100

        return round(research_potential, 2)
