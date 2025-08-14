#!/usr/bin/env python3
"""Enhanced CSV Processing Engine for SurgifyAI Platform
Advanced medical data processing with French terminology support
Statistical analysis, survival curves, and treatment effectiveness.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .models.medical import (
    CohortAnalysis,
    FrenchSymptoms,
    HistologyType,
    MetastasisStage,
    NodeStage,
    SRCCCase,
    SurgicalOutcome,
    SurvivalMetrics,
    TNMStaging,
    TreatmentProtocol,
    TreatmentProtocolModel,
    TumorStage,
)


logger = logging.getLogger(__name__)


class FrenchMedicalTranslator:
    """French to English medical terminology translator."""

    FRENCH_TERMS = {
        # Symptoms
        "épigastralgie": "epigastric_pain",
        "vomissement": "vomiting",
        "dysphagie": "dysphagia",
        "amaigrissement": "weight_loss",
        "asthénie": "fatigue",
        "anorexie": "loss_of_appetite",
        "hématémèse": "hematemesis",
        "méléna": "melena",
        "dyspepsie": "dyspepsia",
        # Tumor locations
        "estomac": "stomach",
        "antrale": "antral",
        "fundique": "fundic",
        "corporéale": "body",
        "cardiaque": "cardiac",
        # Histology
        "adénocarcinome": "adenocarcinoma",
        "cellules en bague à chaton": "signet_ring_cell",
        "peu différencié": "poorly_differentiated",
        "bien différencié": "well_differentiated",
        "moyennement différencié": "moderately_differentiated",
        # Surgical procedures
        "gastrectomie": "gastrectomy",
        "gastrectomie totale": "total_gastrectomy",
        "gastrectomie partielle": "partial_gastrectomy",
        "laparoscopie": "laparoscopic",
        "laparotomie": "open_surgery",
        # Outcomes
        "complet": "complete",
        "partiel": "partial",
        "incomplet": "incomplete",
        "rémission": "remission",
        "récidive": "recurrence",
        "progression": "progression",
    }

    @classmethod
    def translate_term(cls, french_term: str) -> str:
        """Translate French medical term to English."""
        normalized = french_term.lower().strip()
        return cls.FRENCH_TERMS.get(normalized, french_term)

    @classmethod
    def detect_french_symptoms(cls, text: str) -> list[FrenchSymptoms]:
        """Detect French symptoms in text."""
        symptoms = []
        text_lower = text.lower()

        for symptom in FrenchSymptoms:
            if symptom.value.lower() in text_lower:
                symptoms.append(symptom)

        return symptoms


class TNMStageParser:
    """Parse and validate TNM staging information."""

    TNM_PATTERN = re.compile(
        r"T(\d+[ab]?|is|x)\s*N(\d+[ab]?|x)\s*M(\d+[ab]?|x)", re.IGNORECASE
    )

    @classmethod
    def parse_tnm_string(cls, tnm_string: str) -> TNMStaging | None:
        """Parse TNM string into staging object."""
        if not tnm_string:
            return None

        # Clean the string
        tnm_clean = re.sub(r"[^\w]", "", tnm_string.upper())

        # Try direct mapping first
        try:
            if len(tnm_clean) >= 6:  # e.g., T3N1M0
                t_part = (
                    tnm_clean[1:3]
                    if tnm_clean[2].isdigit() or tnm_clean[2] in "ABIS"
                    else tnm_clean[1:2]
                )
                n_part = (
                    tnm_clean[3:5]
                    if len(tnm_clean) > 4
                    and (tnm_clean[4].isdigit() or tnm_clean[4] in "AB")
                    else tnm_clean[3:4]
                )
                m_part = (
                    tnm_clean[5:7]
                    if len(tnm_clean) > 6
                    and (tnm_clean[6].isdigit() or tnm_clean[6] in "AB")
                    else tnm_clean[5:6]
                )

                # Map to enum values
                tumor = cls._map_tumor_stage(t_part)
                node = cls._map_node_stage(n_part)
                metastasis = cls._map_metastasis_stage(m_part)

                if tumor and node and metastasis:
                    return TNMStaging(tumor=tumor, node=node, metastasis=metastasis)
        except Exception as e:
            logger.warning(f"Error parsing TNM string {tnm_string}: {e}")

        return None

    @staticmethod
    def _map_tumor_stage(t_str: str) -> TumorStage | None:
        """Map tumor string to TumorStage enum."""
        mapping = {
            "0": TumorStage.T0,
            "IS": TumorStage.TIS,
            "1": TumorStage.T1,
            "1A": TumorStage.T1A,
            "1B": TumorStage.T1B,
            "2": TumorStage.T2,
            "3": TumorStage.T3,
            "4": TumorStage.T4,
            "4A": TumorStage.T4A,
            "4B": TumorStage.T4B,
            "X": TumorStage.TX,
        }
        return mapping.get(t_str.upper())

    @staticmethod
    def _map_node_stage(n_str: str) -> NodeStage | None:
        """Map node string to NodeStage enum."""
        mapping = {
            "0": NodeStage.N0,
            "1": NodeStage.N1,
            "2": NodeStage.N2,
            "3": NodeStage.N3,
            "3A": NodeStage.N3A,
            "3B": NodeStage.N3B,
            "X": NodeStage.NX,
        }
        return mapping.get(n_str.upper())

    @staticmethod
    def _map_metastasis_stage(m_str: str) -> MetastasisStage | None:
        """Map metastasis string to MetastasisStage enum."""
        mapping = {
            "0": MetastasisStage.M0,
            "1": MetastasisStage.M1,
            "1A": MetastasisStage.M1A,
            "1B": MetastasisStage.M1B,
            "X": MetastasisStage.MX,
        }
        return mapping.get(m_str.upper())


class SurvivalAnalyzer:
    """Advanced survival analysis calculations."""

    @staticmethod
    def calculate_kaplan_meier(cases: list[SRCCCase]) -> dict[str, Any]:
        """Calculate Kaplan-Meier survival estimates."""
        # Extract survival data
        survival_data = []
        for case in cases:
            if case.survival_metrics and case.survival_metrics.overall_survival_months:
                survival_data.append(
                    {
                        "time": case.survival_metrics.overall_survival_months,
                        "event": case.survival_metrics.event_occurred,
                        "case_id": case.case_id,
                    }
                )

        if not survival_data:
            return {"error": "No survival data available"}

        # Sort by survival time
        survival_data.sort(key=lambda x: x["time"])

        # Calculate Kaplan-Meier estimates
        n_at_risk = len(survival_data)
        survival_prob = 1.0
        km_estimates = []

        for _i, data_point in enumerate(survival_data):
            if data_point["event"]:
                survival_prob *= (n_at_risk - 1) / n_at_risk

            km_estimates.append(
                {
                    "time": data_point["time"],
                    "survival_probability": survival_prob,
                    "n_at_risk": n_at_risk,
                    "event": data_point["event"],
                }
            )

            n_at_risk -= 1

        # Calculate median survival
        median_survival = None
        for estimate in km_estimates:
            if estimate["survival_probability"] <= 0.5:
                median_survival = estimate["time"]
                break

        return {
            "estimates": km_estimates,
            "median_survival": median_survival,
            "total_cases": len(survival_data),
            "events": sum(1 for d in survival_data if d["event"]),
        }

    @staticmethod
    def calculate_survival_by_stage(cases: list[SRCCCase]) -> dict[str, dict[str, Any]]:
        """Calculate survival by TNM stage."""
        stage_groups = {}

        for case in cases:
            stage = case.tnm_staging.stage_group or "Unknown"
            if stage not in stage_groups:
                stage_groups[stage] = []
            stage_groups[stage].append(case)

        results = {}
        for stage, stage_cases in stage_groups.items():
            results[stage] = SurvivalAnalyzer.calculate_kaplan_meier(stage_cases)

        return results


class TreatmentEffectivenessAnalyzer:
    """Analyze treatment protocol effectiveness."""

    @staticmethod
    def analyze_protocol_outcomes(cases: list[SRCCCase]) -> dict[str, dict[str, Any]]:
        """Analyze outcomes by treatment protocol."""
        protocol_outcomes = {}

        for case in cases:
            for treatment in case.treatment_protocols:
                protocol_name = treatment.protocol.value

                if protocol_name not in protocol_outcomes:
                    protocol_outcomes[protocol_name] = {
                        "cases": [],
                        "complete_responses": 0,
                        "complications": 0,
                        "survival_times": [],
                        "completion_rates": [],
                    }

                outcome_data = protocol_outcomes[protocol_name]
                outcome_data["cases"].append(case.case_id)

                # Analyze surgical outcomes
                if case.surgical_outcome == SurgicalOutcome.COMPLETE:
                    outcome_data["complete_responses"] += 1

                # Count complications
                if case.complications:
                    outcome_data["complications"] += len(case.complications)

                # Collect survival data
                if (
                    case.survival_metrics
                    and case.survival_metrics.overall_survival_months
                ):
                    outcome_data["survival_times"].append(
                        case.survival_metrics.overall_survival_months
                    )

                # Collect completion rates
                if treatment.completion_rate:
                    outcome_data["completion_rates"].append(treatment.completion_rate)

        # Calculate summary statistics
        for protocol_name, data in protocol_outcomes.items():
            total_cases = len(data["cases"])
            data["response_rate"] = (
                (data["complete_responses"] / total_cases * 100)
                if total_cases > 0
                else 0
            )
            data["complication_rate"] = (
                (data["complications"] / total_cases * 100) if total_cases > 0 else 0
            )

            if data["survival_times"]:
                data["median_survival"] = np.median(data["survival_times"])
                data["mean_survival"] = np.mean(data["survival_times"])
            else:
                data["median_survival"] = None
                data["mean_survival"] = None

            if data["completion_rates"]:
                data["mean_completion_rate"] = np.mean(data["completion_rates"])
            else:
                data["mean_completion_rate"] = None

        return protocol_outcomes


class EnhancedCSVProcessor:
    """Enhanced CSV processor for medical data with French support."""

    def __init__(self) -> None:
        self.translator = FrenchMedicalTranslator()
        self.tnm_parser = TNMStageParser()
        self.survival_analyzer = SurvivalAnalyzer()
        self.treatment_analyzer = TreatmentEffectivenessAnalyzer()

    def process_srcc_dataset(
        self, csv_path: Path
    ) -> tuple[list[SRCCCase], dict[str, Any]]:
        """Process SRCC dataset from CSV file."""
        logger.info(f"Processing SRCC dataset: {csv_path}")

        # Read CSV
        df = pd.read_csv(csv_path)

        # Detect schema
        schema_info = self._analyze_schema(df)

        # Process cases
        cases = []
        errors = []

        for index, row in df.iterrows():
            try:
                case = self._create_srcc_case_from_row(row)
                cases.append(case)
            except Exception as e:
                error_msg = f"Error processing row {index}: {e}"
                logger.exception(error_msg)
                errors.append(error_msg)

        # Generate analytics
        analytics = self._generate_analytics(cases, df)

        results = {
            "total_cases": len(cases),
            "successful_cases": len(cases),
            "errors": errors,
            "schema": schema_info,
            "analytics": analytics,
        }

        logger.info(f"Successfully processed {len(cases)} SRCC cases")
        return cases, results

    def _analyze_schema(self, df: pd.DataFrame) -> dict[str, Any]:
        """Analyze CSV schema and detect medical fields."""
        schema = {}

        for col in df.columns:
            col_lower = col.lower()
            completeness = (1 - df[col].isnull().mean()) * 100

            # Detect field types
            if "patient" in col_lower or "id" in col_lower:
                field_type = "Patient Identifier"
            elif "age" in col_lower:
                field_type = "Demographics"
            elif any(term in col_lower for term in ["tnm", "stage", "tumor"]):
                field_type = "TNM Staging"
            elif any(
                term in col_lower for term in ["histolog", "adenocarcinoma", "signet"]
            ):
                field_type = "Histology"
            elif any(
                term in col_lower for term in ["treatment", "protocol", "flot", "xelox"]
            ):
                field_type = "Treatment Protocol"
            elif any(term in col_lower for term in ["survival", "outcome", "follow"]):
                field_type = "Survival/Outcome"
            elif any(
                term in col_lower
                for term in ["symptom", "épigastralgie", "vomissement"]
            ):
                field_type = "Clinical Symptoms"
            else:
                field_type = "Other"

            schema[col] = {
                "type": field_type,
                "completeness": round(completeness, 1),
                "unique_values": df[col].nunique(),
                "sample_values": df[col].dropna().head(3).tolist(),
            }

        return schema

    def _create_srcc_case_from_row(self, row: pd.Series) -> SRCCCase:
        """Create SRCCCase from CSV row."""
        # Extract basic demographics
        patient_id = str(
            row.get("patient_id", f"PAT_{datetime.now().strftime('%Y%m%d%H%M%S')}")
        )
        age = int(row.get("age", 0))
        gender = str(row.get("gender", "M")).upper()

        # Parse TNM staging
        tnm_string = (
            row.get("tumor_stage", "")
            or row.get("tnm_stage", "")
            or row.get("stage", "")
        )
        tnm_staging = self.tnm_parser.parse_tnm_string(str(tnm_string))

        if not tnm_staging:
            # Create default staging if parsing fails
            tnm_staging = TNMStaging(
                tumor=TumorStage.T1, node=NodeStage.N0, metastasis=MetastasisStage.M0
            )

        # Determine histology
        histology_str = str(row.get("histology", "Adenocarcinoma")).lower()
        if "signet" in histology_str or "ring" in histology_str:
            histology = HistologyType.SIGNET_RING
        elif "adenocarcinoma" in histology_str:
            histology = HistologyType.ADENOCARCINOMA
        else:
            histology = HistologyType.ADENOCARCINOMA

        # Parse treatment protocols
        treatment_protocols = []
        if "flot_cycles" in row.index or "treatment_protocol" in row.index:
            cycles = row.get("flot_cycles", 0) or row.get("cycles", 0)
            if cycles > 0:
                treatment_protocols.append(
                    TreatmentProtocolModel(
                        protocol=TreatmentProtocol.FLOT,
                        cycles_planned=cycles,
                        cycles_completed=cycles,
                    )
                )

        # Parse surgical outcome
        outcome_str = str(row.get("surgical_outcome", "Complete")).lower()
        if "complete" in outcome_str:
            surgical_outcome = SurgicalOutcome.COMPLETE
        elif "partial" in outcome_str:
            surgical_outcome = SurgicalOutcome.PARTIAL
        else:
            surgical_outcome = SurgicalOutcome.COMPLETE

        # Parse survival metrics
        survival_months = row.get("survival_months", None)
        survival_metrics = None
        if survival_months and not pd.isna(survival_months):
            survival_metrics = SurvivalMetrics(
                overall_survival_months=float(survival_months),
                vital_status="Alive",  # Default assumption
            )

        # Detect French symptoms
        symptoms_french = []
        symptom_columns = [col for col in row.index if "symptom" in col.lower()]
        for col in symptom_columns:
            symptom_text = str(row.get(col, ""))
            symptoms_french.extend(self.translator.detect_french_symptoms(symptom_text))

        return SRCCCase(
            patient_id=patient_id,
            age=age,
            gender=gender,
            tnm_staging=tnm_staging,
            histology=histology,
            treatment_protocols=treatment_protocols,
            surgical_outcome=surgical_outcome,
            survival_metrics=survival_metrics,
            symptoms_french=symptoms_french,
        )

    def _generate_analytics(
        self, cases: list[SRCCCase], df: pd.DataFrame
    ) -> dict[str, Any]:
        """Generate comprehensive analytics."""
        analytics = {}

        # Basic demographics
        analytics["demographics"] = {
            "total_cases": len(cases),
            "median_age": np.median([case.age for case in cases]),
            "gender_distribution": {
                "male": sum(1 for case in cases if case.gender == "M"),
                "female": sum(1 for case in cases if case.gender == "F"),
            },
        }

        # TNM staging distribution
        stage_dist = {}
        for case in cases:
            stage = case.tnm_staging.stage_group or "Unknown"
            stage_dist[stage] = stage_dist.get(stage, 0) + 1
        analytics["stage_distribution"] = stage_dist

        # Treatment effectiveness
        analytics[
            "treatment_effectiveness"
        ] = self.treatment_analyzer.analyze_protocol_outcomes(cases)

        # Survival analysis
        analytics["survival_analysis"] = self.survival_analyzer.calculate_kaplan_meier(
            cases
        )
        analytics[
            "survival_by_stage"
        ] = self.survival_analyzer.calculate_survival_by_stage(cases)

        # French terminology detection
        french_symptoms_count = sum(len(case.symptoms_french) for case in cases)
        analytics["french_terminology"] = {
            "cases_with_french_symptoms": sum(
                1 for case in cases if case.symptoms_french
            ),
            "total_french_symptoms": french_symptoms_count,
        }

        return analytics

    def create_cohort_analysis(
        self, cases: list[SRCCCase], cohort_name: str
    ) -> CohortAnalysis:
        """Create comprehensive cohort analysis."""
        return CohortAnalysis(
            cohort_id=f"COHORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name=cohort_name,
            description=f"SRCC cohort analysis with {len(cases)} cases",
            cases=cases,
        )


class UniversalDataProcessor(EnhancedCSVProcessor):
    """Universal processor for all supported data formats."""

    def ingest(self, file_path: Path, file_type: str | None = None) -> Any:
        """Ingest and parse any supported dataset format."""
        if not file_type:
            file_type = file_path.suffix.lower().replace(".", "")
        if file_type in ["csv"]:
            return self.process_srcc_dataset(file_path)
        if file_type in ["xlsx", "xls"]:
            df = pd.read_excel(file_path)
            return self._analyze_schema(df), df
        if file_type in ["json"]:
            import json

            with open(file_path) as f:
                return json.load(f)
        elif file_type in ["xml"]:
            import xml.etree.ElementTree as ET

            tree = ET.parse(file_path)
            return tree.getroot()
        # Add more handlers for HL7 FHIR, DICOM, Database, etc.
        else:
            msg = f"Unsupported file type: {file_type}"
            raise ValueError(msg)


# Factory function for easy access
def create_enhanced_csv_processor() -> EnhancedCSVProcessor:
    """Create an enhanced CSV processor instance."""
    return EnhancedCSVProcessor()
