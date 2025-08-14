from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.surge.core.models.medical import (
    GastricSystem,
    IndependentCellEntity,
    TumorUnit,
)
from src.surge.core.services.ai_service import AIService
from src.surge.modules.chemo_flot import FLOTCase, analyze_flot_regimen
from src.surge.modules.gastric_surgery import (
    GastricSurgeryCase,
    analyze_gastrectomy_case,
)
from src.surge.modules.precision_engine import (
    IntegratedCase,
    create_gastric_oncology_strategy,
)


router = APIRouter()
ai_service = AIService()


@router.post("/recommendations/risk", response_model=float)
def assess_risk(patient_data: dict) -> float:
    """Assess patient risk."""
    try:
        return ai_service.assess_patient_risk(patient_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations", response_model=list[str])
def get_recommendations(patient_data: dict) -> list[str]:
    """Get recommendations for patient."""
    try:
        return ai_service.get_recommendations(patient_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/outcome", response_model=dict)
def predict_outcome(patient_data: dict) -> dict:
    """Predict patient outcome."""
    try:
        return ai_service.predict_patient_outcome(patient_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/alerts", response_model=list[str])
def generate_alerts(patient_data: dict) -> list[str]:
    """Generate patient alerts."""
    try:
        return ai_service.generate_patient_alerts(patient_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Gastric Oncology Precision Decision Endpoints ===


class GastricDecisionRequest(BaseModel):
    """Request model for gastric decision analysis."""

    case: IntegratedCase
    gastric_system: GastricSystem | None = None
    tumor_unit: TumorUnit | None = None
    cell_entity: IndependentCellEntity | None = None


class GastricOutcomesRequest(BaseModel):
    """Request model for gastric outcomes analysis."""

    gastric_surgery_case: GastricSurgeryCase | None = None
    flot_case: FLOTCase | None = None


@router.post("/recommendations/gastric/decision", response_model=dict)
def gastric_precision_decision(request: GastricDecisionRequest) -> dict:
    """Gastric oncology precision decision endpoint.
    Integrates case data with new entities to provide comprehensive analysis.
    """
    try:
        # Create gastric oncology strategy
        strategy = create_gastric_oncology_strategy()

        # Perform integrated analysis
        analysis = strategy["analyze_function"](
            case=request.case,
            gastric_system=request.gastric_system,
            tumor_unit=request.tumor_unit,
            cell_entity=request.cell_entity,
        )

        return {
            "status": "success",
            "strategy_id": "gastric-oncology",
            "analysis": analysis,
            "confidence": analysis.get("confidence_metrics", {}),
            "recommendations": analysis.get("recommendations", {}),
            "risk_assessment": analysis.get("risk_assessment", {}),
            "outcome_projections": analysis.get("outcome_projections", {}),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gastric decision analysis failed: {e!s}"
        )


@router.post("/recommendations/gastric/outcomes", response_model=dict)
def gastric_outcomes_analysis(request: GastricOutcomesRequest) -> dict:
    """Gastric outcomes analysis endpoint.
    Provides detailed metrics for gastrectomy and FLOT regimens.
    """
    try:
        results = {
            "status": "success",
            "analysis_type": "gastric_outcomes",
            "timestamp": datetime.now().isoformat(),
        }

        # Analyze gastrectomy case if provided
        if request.gastric_surgery_case:
            gastrectomy_analysis = analyze_gastrectomy_case(
                request.gastric_surgery_case
            )
            results["gastrectomy_analysis"] = gastrectomy_analysis

            # Extract key metrics for summary
            results["gastrectomy_summary"] = {
                "r0_achieved": gastrectomy_analysis.get("r0_analysis", {}).get(
                    "r0_achieved"
                ),
                "adequate_lymphadenectomy": gastrectomy_analysis.get(
                    "lymph_node_analysis", {}
                ).get("adequate_harvest"),
                "predicted_los": gastrectomy_analysis.get("length_of_stay", {}).get(
                    "predicted_los_days"
                ),
                "quality_grade": gastrectomy_analysis.get("quality_metrics", {}).get(
                    "quality_grade"
                ),
                "mortality_risk_category": gastrectomy_analysis.get(
                    "mortality_risk", {}
                ).get("risk_category"),
                "readmission_risk_category": gastrectomy_analysis.get(
                    "readmission_risk", {}
                ).get("risk_category"),
            }

        # Analyze FLOT case if provided
        if request.flot_case:
            flot_analysis = analyze_flot_regimen(request.flot_case)
            results["flot_analysis"] = flot_analysis

            # Extract key metrics for summary
            results["flot_summary"] = {
                "applicability_score": flot_analysis.get("applicability", {}).get(
                    "applicability_score"
                ),
                "dose_intensity": flot_analysis.get("dose_intensity", {}).get(
                    "relative_dose_intensity"
                ),
                "toxicity_grade": flot_analysis.get("toxicity", {}).get("max_grade"),
                "response_quality": flot_analysis.get("response", {}).get(
                    "response_quality"
                ),
                "overall_grade": flot_analysis.get("overall_assessment", {}).get(
                    "grade"
                ),
                "narrative": flot_analysis.get("narrative_summary"),
            }

        # Generate combined recommendations if both analyses available
        if request.gastric_surgery_case and request.flot_case:
            results[
                "integrated_recommendations"
            ] = _generate_integrated_recommendations(
                results.get("gastrectomy_summary", {}),
                results.get("flot_summary", {}),
            )

        return results

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Gastric outcomes analysis failed: {e!s}"
        )


def _generate_integrated_recommendations(
    gastrectomy_summary: dict, flot_summary: dict
) -> dict[str, list[str]]:
    """Generate integrated recommendations based on both analyses."""
    recommendations = {
        "clinical_actions": [],
        "quality_improvements": [],
        "monitoring": [],
        "follow_up": [],
    }

    # Clinical actions based on surgical quality
    if not gastrectomy_summary.get("r0_achieved"):
        recommendations["clinical_actions"].append(
            "Consider adjuvant therapy consultation"
        )

    if gastrectomy_summary.get("mortality_risk_category") == "high":
        recommendations["clinical_actions"].append(
            "Enhanced perioperative monitoring required"
        )

    # Quality improvements
    if not gastrectomy_summary.get("adequate_lymphadenectomy"):
        recommendations["quality_improvements"].append(
            "Review lymphadenectomy technique"
        )

    if flot_summary.get("dose_intensity", 0) < 70:
        recommendations["quality_improvements"].append(
            "Optimize supportive care protocols"
        )

    # Monitoring recommendations
    if gastrectomy_summary.get("readmission_risk_category") == "high":
        recommendations["monitoring"].append(
            "Enhanced discharge planning and early follow-up"
        )

    if flot_summary.get("toxicity_grade", "0") in ["3", "4", "5"]:
        recommendations["monitoring"].append(
            "Intensified toxicity monitoring during chemotherapy"
        )

    # Follow-up based on overall outcomes
    overall_quality = [
        gastrectomy_summary.get("quality_grade", ""),
        flot_summary.get("overall_grade", ""),
    ]

    if any(grade in ["D", "Poor", "Needs Improvement"] for grade in overall_quality):
        recommendations["follow_up"].append("Multidisciplinary team review recommended")

    if flot_summary.get("response_quality") == "Poor":
        recommendations["follow_up"].append("Consider alternative treatment strategies")

    return recommendations


# === Individual Analysis Endpoints ===


@router.post("/recommendations/gastric/gastrectomy", response_model=dict)
def analyze_gastrectomy_endpoint(case: GastricSurgeryCase) -> dict:
    """Dedicated gastrectomy analysis endpoint."""
    try:
        analysis = analyze_gastrectomy_case(case)

        return {
            "status": "success",
            "analysis_type": "gastrectomy",
            "case_id": case.case_id,
            "analysis": analysis,
            "summary": {
                "r0_resection": analysis.get("r0_analysis", {}).get("r0_achieved"),
                "quality_score": analysis.get("quality_metrics", {}).get(
                    "quality_percentage"
                ),
                "risk_level": analysis.get("mortality_risk", {}).get("risk_category"),
                "recommendations": analysis.get("recommendations", []),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recommendations/gastric/flot", response_model=dict)
def analyze_flot_endpoint(case: FLOTCase) -> dict:
    """Dedicated FLOT analysis endpoint."""
    try:
        analysis = analyze_flot_regimen(case)

        return {
            "status": "success",
            "analysis_type": "flot_regimen",
            "case_id": case.case_id,
            "analysis": analysis,
            "summary": {
                "applicability": analysis.get("applicability", {}).get(
                    "applicability_score"
                ),
                "dose_intensity": analysis.get("dose_intensity", {}).get(
                    "relative_dose_intensity"
                ),
                "tolerability": analysis.get("toxicity", {}).get(
                    "tolerability_assessment"
                ),
                "response": analysis.get("response", {}).get("response_quality"),
                "overall_grade": analysis.get("overall_assessment", {}).get("grade"),
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Export Endpoints ===


@router.get("/recommendations/gastric/export/{case_id}", response_model=dict)
def export_gastric_analysis(case_id: str, format: str = "json") -> dict:
    """Export gastric analysis results in specified format."""
    try:
        # This would typically fetch from database
        # For now, return a template structure
        return {
            "case_id": case_id,
            "export_format": format,
            "timestamp": datetime.now().isoformat(),
            "analysis_components": [
                "gastric_system_assessment",
                "tumor_characterization",
                "cellular_analysis",
                "surgical_metrics",
                "chemotherapy_metrics",
                "precision_scores",
                "outcome_projections",
            ],
            "export_url": f"/api/v1/recommendations/gastric/download/{case_id}?format={format}",
            "status": "ready",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
