"""
Domain Mapper - Maps surgery concepts to universal research concepts
Enables cross-domain research while preserving surgical specificity
"""

from typing import Dict, List, Any, Optional
from enum import Enum


class ResearchDomain(str, Enum):
    SURGERY = "surgery"
    MEDICINE = "medicine"
    HEALTHCARE = "healthcare"
    LOGISTICS = "logistics"
    INSURANCE = "insurance"


class ConceptMapper:
    """
    Maps domain-specific concepts to universal research concepts
    Preserves surgical domain knowledge while enabling universal research
    """

    def __init__(self):
        self.surgical_concepts = self._load_surgical_concepts()
        self.universal_concepts = self._load_universal_concepts()

    def map_surgical_to_universal(
        self, surgical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Maps surgical concepts to universal research concepts
        Enables comparison across different domains
        """
        return {
            # Universal research fields
            "domain": ResearchDomain.SURGERY,
            "entity_type": self._map_entity_type(surgical_data.get("procedure_type")),
            "outcome_measure": self._map_outcome_measure(surgical_data),
            "risk_factors": self._map_risk_factors(surgical_data),
            "success_metrics": self._map_success_metrics(surgical_data),
            "temporal_aspects": self._map_temporal_aspects(surgical_data),
            "stakeholders": self._map_stakeholders(surgical_data),
            # Preserve surgical specificity
            "domain_specific": {
                "surgical_specialty": surgical_data.get("research_metadata", {}).get(
                    "specialty"
                ),
                "procedure_classification": self._classify_procedure(
                    surgical_data.get("procedure_type")
                ),
                "anatomical_system": self._identify_anatomical_system(
                    surgical_data.get("procedure_type")
                ),
                "surgical_approach": self._identify_approach(
                    surgical_data.get("procedure_type")
                ),
            },
            # Universal process metrics
            "process_metrics": {
                "duration": self._calculate_duration(surgical_data),
                "resource_utilization": self._assess_resources(surgical_data),
                "complexity_level": surgical_data.get("research_metadata", {}).get(
                    "complexity_score"
                ),
                "quality_indicators": self._extract_quality_indicators(surgical_data),
            },
        }

    def create_universal_cohort_definition(
        self, surgical_criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates universal cohort definition that can be applied across domains
        """
        return {
            "inclusion_criteria": {
                "entity_characteristics": self._map_entity_characteristics(
                    surgical_criteria
                ),
                "outcome_requirements": self._map_outcome_requirements(
                    surgical_criteria
                ),
                "temporal_constraints": self._map_temporal_constraints(
                    surgical_criteria
                ),
            },
            "exclusion_criteria": {
                "risk_thresholds": self._map_risk_thresholds(surgical_criteria),
                "data_quality_requirements": self._map_quality_requirements(
                    surgical_criteria
                ),
            },
            "stratification_factors": {
                "primary_factors": self._identify_primary_stratification(
                    surgical_criteria
                ),
                "secondary_factors": self._identify_secondary_stratification(
                    surgical_criteria
                ),
            },
        }

    def _load_surgical_concepts(self) -> Dict[str, Any]:
        """Load surgical concept mappings"""
        return {
            "procedures": {
                "cardiac": ["cabg", "valve", "bypass", "stent"],
                "orthopedic": ["joint", "fracture", "arthroscopy", "replacement"],
                "neurological": ["craniotomy", "spine", "tumor", "aneurysm"],
                "general": ["laparoscopy", "appendectomy", "hernia", "gallbladder"],
                "vascular": ["aneurysm", "bypass", "stent", "embolectomy"],
            },
            "outcomes": {
                "mortality": ["death", "survival"],
                "morbidity": ["complication", "infection", "bleeding"],
                "functional": ["mobility", "pain", "quality_of_life"],
                "economic": ["length_of_stay", "readmission", "cost"],
            },
        }

    def _load_universal_concepts(self) -> Dict[str, Any]:
        """Load universal research concepts"""
        return {
            "entity_types": ["intervention", "treatment", "procedure", "service"],
            "outcome_categories": [
                "binary",
                "continuous",
                "categorical",
                "time_to_event",
            ],
            "risk_categories": ["low", "moderate", "high", "critical"],
            "success_measures": [
                "effectiveness",
                "efficiency",
                "safety",
                "satisfaction",
            ],
        }

    def _map_entity_type(self, procedure_type: Optional[str]) -> str:
        """Map surgical procedure to universal entity type"""
        if not procedure_type:
            return "intervention"

        procedure_lower = procedure_type.lower()

        if any(
            term in procedure_lower for term in ["surgery", "operation", "procedure"]
        ):
            return "surgical_intervention"
        elif any(
            term in procedure_lower for term in ["diagnostic", "screening", "test"]
        ):
            return "diagnostic_procedure"
        else:
            return "therapeutic_intervention"

    def _map_outcome_measure(self, surgical_data: Dict[str, Any]) -> str:
        """Map surgical outcomes to universal outcome measures"""
        outcome_category = surgical_data.get("research_metadata", {}).get(
            "outcome_category"
        )

        outcome_map = {
            "excellent": "optimal_outcome",
            "good": "satisfactory_outcome",
            "acceptable": "adequate_outcome",
            "cancelled": "intervention_cancelled",
            "pending": "outcome_pending",
        }

        return outcome_map.get(outcome_category, "outcome_unknown")

    def _map_risk_factors(self, surgical_data: Dict[str, Any]) -> List[str]:
        """Map surgical risk factors to universal risk categories"""
        risk_factors = surgical_data.get("research_insights", {}).get(
            "risk_factors", []
        )

        universal_risks = []
        risk_mapping = {
            "advanced_age": "demographic_risk",
            "obesity": "physiological_risk",
            "diabetes": "comorbidity_risk",
            "cardiac_history": "medical_history_risk",
            "hypertension": "cardiovascular_risk",
            "high_risk_procedure": "procedural_complexity_risk",
        }

        for risk in risk_factors:
            if risk in risk_mapping:
                universal_risks.append(risk_mapping[risk])

        return universal_risks

    def _map_success_metrics(self, surgical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map surgical success to universal success metrics"""
        return {
            "effectiveness": {
                "primary_outcome_achieved": surgical_data.get(
                    "research_metadata", {}
                ).get("outcome_category")
                in ["excellent", "good"],
                "outcome_probability": surgical_data.get("research_insights", {}).get(
                    "outcome_probability", 0.0
                ),
            },
            "efficiency": {
                "resource_utilization": "optimal"
                if surgical_data.get("status") == "completed"
                else "suboptimal",
                "process_efficiency": self._assess_process_efficiency(surgical_data),
            },
            "safety": {
                "risk_level": self._categorize_risk_level(
                    surgical_data.get("risk_score")
                ),
                "adverse_events": "none_documented",  # Would be enhanced with actual adverse event data
            },
        }

    def _map_temporal_aspects(self, surgical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map surgical timing to universal temporal concepts"""
        return {
            "planning_phase": surgical_data.get("scheduled_date") is not None,
            "execution_phase": surgical_data.get("actual_start") is not None,
            "completion_phase": surgical_data.get("actual_end") is not None,
            "follow_up_phase": surgical_data.get("status") == "completed",
        }

    def _map_stakeholders(self, surgical_data: Dict[str, Any]) -> List[str]:
        """Map surgical stakeholders to universal stakeholder categories"""
        stakeholders = ["patient", "primary_provider"]

        if surgical_data.get("provider_info", {}).get("surgeon_id"):
            stakeholders.append("specialist_provider")

        # Would be enhanced with actual team data
        stakeholders.extend(["healthcare_institution", "regulatory_body"])

        return stakeholders

    def _classify_procedure(self, procedure_type: Optional[str]) -> str:
        """Classify surgical procedure"""
        if not procedure_type:
            return "unclassified"

        procedure_lower = procedure_type.lower()

        for specialty, keywords in self.surgical_concepts["procedures"].items():
            if any(keyword in procedure_lower for keyword in keywords):
                return specialty

        return "general"

    def _identify_anatomical_system(self, procedure_type: Optional[str]) -> str:
        """Identify anatomical system involved"""
        if not procedure_type:
            return "unknown"

        procedure_lower = procedure_type.lower()

        system_map = {
            "cardiovascular": ["cardiac", "heart", "vascular", "vessel"],
            "musculoskeletal": ["bone", "joint", "muscle", "orthopedic"],
            "nervous": ["neuro", "brain", "spine", "nerve"],
            "digestive": ["gastro", "bowel", "stomach", "liver"],
            "respiratory": ["lung", "pulmonary", "thoracic"],
            "genitourinary": ["kidney", "bladder", "urological"],
        }

        for system, keywords in system_map.items():
            if any(keyword in procedure_lower for keyword in keywords):
                return system

        return "multi_system"

    def _identify_approach(self, procedure_type: Optional[str]) -> str:
        """Identify surgical approach"""
        if not procedure_type:
            return "unknown"

        procedure_lower = procedure_type.lower()

        if "laparoscopic" in procedure_lower or "minimally invasive" in procedure_lower:
            return "minimally_invasive"
        elif "open" in procedure_lower:
            return "open"
        elif "robotic" in procedure_lower:
            return "robotic_assisted"
        else:
            return "conventional"

    def _calculate_duration(self, surgical_data: Dict[str, Any]) -> Optional[float]:
        """Calculate procedure duration in hours"""
        start = surgical_data.get("actual_start")
        end = surgical_data.get("actual_end")

        if start and end:
            duration = (end - start).total_seconds() / 3600
            return round(duration, 2)

        return None

    def _assess_resources(self, surgical_data: Dict[str, Any]) -> str:
        """Assess resource utilization level"""
        complexity = surgical_data.get("research_metadata", {}).get(
            "complexity_score", 1.0
        )

        if complexity > 3.5:
            return "high"
        elif complexity > 2.0:
            return "moderate"
        else:
            return "standard"

    def _extract_quality_indicators(
        self, surgical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract quality indicators"""
        return {
            "completeness": "complete"
            if surgical_data.get("status") == "completed"
            else "incomplete",
            "timeliness": "on_schedule"
            if surgical_data.get("scheduled_date")
            else "unscheduled",
            "accuracy": "high",  # Would be enhanced with actual quality metrics
        }

    def _assess_process_efficiency(self, surgical_data: Dict[str, Any]) -> str:
        """Assess process efficiency level"""
        if surgical_data.get("status") == "completed":
            return "efficient"
        elif surgical_data.get("status") == "cancelled":
            return "inefficient"
        else:
            return "pending_assessment"

    def _categorize_risk_level(self, risk_score: Optional[float]) -> str:
        """Categorize risk level"""
        if not risk_score:
            return "unknown"

        if risk_score < 0.3:
            return "low"
        elif risk_score < 0.7:
            return "moderate"
        else:
            return "high"

    def _map_entity_characteristics(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Map entity characteristics for cohort definition"""
        return {
            "procedure_category": criteria.get("procedure_type"),
            "complexity_range": criteria.get("complexity_range"),
            "risk_profile": criteria.get("risk_range"),
        }

    def _map_outcome_requirements(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Map outcome requirements"""
        return {
            "outcome_completeness": "required",
            "follow_up_duration": criteria.get("follow_up_period", "30_days"),
            "quality_threshold": criteria.get("quality_threshold", "standard"),
        }

    def _map_temporal_constraints(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Map temporal constraints"""
        return {
            "date_range": criteria.get("date_range"),
            "minimum_follow_up": criteria.get("minimum_follow_up"),
            "data_currency": criteria.get("data_currency", "recent"),
        }

    def _map_risk_thresholds(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Map risk exclusion thresholds"""
        return {
            "maximum_risk_score": criteria.get("max_risk", 1.0),
            "excluded_risk_factors": criteria.get("excluded_risks", []),
        }

    def _map_quality_requirements(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Map data quality requirements"""
        return {
            "completeness_threshold": criteria.get("completeness_threshold", 0.8),
            "required_fields": criteria.get("required_fields", []),
            "data_validation_level": criteria.get("validation_level", "standard"),
        }

    def _identify_primary_stratification(self, criteria: Dict[str, Any]) -> List[str]:
        """Identify primary stratification factors"""
        return criteria.get("primary_stratification", ["procedure_type", "risk_level"])

    def _identify_secondary_stratification(self, criteria: Dict[str, Any]) -> List[str]:
        """Identify secondary stratification factors"""
        return criteria.get(
            "secondary_stratification", ["age_group", "comorbidity_burden"]
        )
