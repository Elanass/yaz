"""Surgery Domain Plugin
Handles surgical dataset parsing, analysis, and deliverable generation.
"""

from typing import Any

import pandas as pd

from src.shared.core.domains import DomainSpec


class SurgerySpec(DomainSpec):
    """Surgery domain specification."""

    def __init__(self) -> None:
        super().__init__(
            name="surgery",
            description="Surgical case analysis and outcome tracking",
            version="1.0.0",
        )

    def schema_detect(self, columns: list[str]) -> float:
        """Detect surgery dataset based on column patterns."""
        surgery_indicators = [
            "tnm",
            "staging",
            "surgery",
            "operation",
            "procedure",
            "gastric",
            "cancer",
            "tumor",
            "carcinoma",
            "grade",
            "protocol",
            "treatment",
            "survival",
            "outcome",
            "histology",
            "pathology",
            "diagnosis",
        ]

        matches = 0
        for col in columns:
            col_lower = col.lower()
            for indicator in surgery_indicators:
                if indicator in col_lower:
                    matches += 1
                    break

        return min(matches / len(columns), 1.0) if columns else 0.0

    def parse(self, df: pd.DataFrame) -> dict[str, Any]:
        """Parse surgical dataset."""
        parsed_data = {
            "total_cases": len(df),
            "columns": list(df.columns),
            "case_types": {},
            "staging_distribution": {},
            "treatment_protocols": {},
            "outcomes": {},
        }

        # Detect and parse TNM staging
        tnm_cols = [
            col
            for col in df.columns
            if "tnm" in col.lower() or "staging" in col.lower()
        ]
        if tnm_cols:
            for col in tnm_cols:
                parsed_data["staging_distribution"][col] = (
                    df[col].value_counts().to_dict()
                )

        # Detect treatment protocols
        treatment_cols = [
            col
            for col in df.columns
            if any(
                term in col.lower()
                for term in ["protocol", "treatment", "therapy", "chemo"]
            )
        ]
        if treatment_cols:
            for col in treatment_cols:
                parsed_data["treatment_protocols"][col] = (
                    df[col].value_counts().to_dict()
                )

        # Detect case types (cancer types, procedures)
        case_cols = [
            col
            for col in df.columns
            if any(
                term in col.lower()
                for term in ["type", "diagnosis", "cancer", "carcinoma"]
            )
        ]
        if case_cols:
            for col in case_cols:
                parsed_data["case_types"][col] = df[col].value_counts().to_dict()

        return parsed_data

    def stats(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate surgical statistics."""
        stats = {
            "summary": {
                "total_cases": len(df),
                "data_completeness": (df.notna().sum() / len(df)).mean() * 100,
                "date_range": None,
            },
            "staging_stats": {},
            "treatment_effectiveness": {},
            "survival_metrics": {},
        }

        # Date range analysis
        date_cols = [
            col
            for col in df.columns
            if any(
                term in col.lower() for term in ["date", "time", "created", "admission"]
            )
        ]
        if date_cols:
            for col in date_cols:
                try:
                    dates = pd.to_datetime(df[col], errors="coerce")
                    if not dates.isna().all():
                        stats["summary"]["date_range"] = {
                            "start": str(dates.min()),
                            "end": str(dates.max()),
                            "span_days": (dates.max() - dates.min()).days,
                        }
                        break
                except:
                    continue

        # TNM staging analysis
        tnm_cols = [col for col in df.columns if "tnm" in col.lower()]
        for col in tnm_cols:
            if col in df.columns:
                staging_counts = df[col].value_counts()
                stats["staging_stats"][col] = {
                    "distribution": staging_counts.to_dict(),
                    "most_common": staging_counts.index[0]
                    if len(staging_counts) > 0
                    else None,
                    "diversity_index": len(staging_counts) / len(df)
                    if len(df) > 0
                    else 0,
                }

        return stats

    def insights(self, df: pd.DataFrame) -> list[str]:
        """Generate surgical insights."""
        insights = []

        # Basic dataset insights
        insights.append(
            f"Dataset contains {len(df)} surgical cases with {len(df.columns)} data fields"
        )

        # Completeness insight
        completeness = (df.notna().sum() / len(df)).mean() * 100
        if completeness > 90:
            insights.append(f"Excellent data completeness: {completeness:.1f}%")
        elif completeness > 70:
            insights.append(f"Good data completeness: {completeness:.1f}%")
        else:
            insights.append(f"Data completeness needs improvement: {completeness:.1f}%")

        # TNM staging insights
        tnm_cols = [
            col
            for col in df.columns
            if "tnm" in col.lower() or "staging" in col.lower()
        ]
        if tnm_cols:
            for col in tnm_cols:
                top_stage = (
                    df[col].mode().iloc[0] if len(df[col].mode()) > 0 else "Unknown"
                )
                insights.append(f"Most common staging in {col}: {top_stage}")

        # Treatment protocol insights
        protocol_cols = [col for col in df.columns if "protocol" in col.lower()]
        if protocol_cols:
            for col in protocol_cols:
                protocols = df[col].value_counts()
                if len(protocols) > 1:
                    insights.append(
                        f"Multiple treatment protocols detected: {', '.join(protocols.head(3).index.tolist())}"
                    )

        # French medical terminology detection
        french_terms = ["épigastralgie", "vomissement", "dysphagie", "amaigrissement"]
        has_french = any(term in str(df.values).lower() for term in french_terms)
        if has_french:
            insights.append(
                "Dataset contains French medical terminology - international case data detected"
            )

        return insights

    def deliverables(self, df: pd.DataFrame, audience: str) -> dict[str, Any]:
        """Generate audience-specific deliverables."""
        stats = self.stats(df)
        insights = self.insights(df)

        base_content = {
            "title": f"Surgical Case Analysis Report - {audience.title()} Edition",
            "summary": insights,
            "data_overview": stats["summary"],
            "generated_at": pd.Timestamp.now().isoformat(),
        }

        if audience == "practitioner":
            return {
                **base_content,
                "focus": "Clinical Decision Support",
                "key_metrics": {
                    "total_cases": len(df),
                    "staging_distribution": stats.get("staging_stats", {}),
                    "treatment_patterns": self._extract_treatment_patterns(df),
                },
                "clinical_recommendations": self._generate_clinical_recommendations(df),
            }

        if audience == "researcher":
            return {
                **base_content,
                "focus": "Research Analysis",
                "statistical_summary": stats,
                "research_opportunities": self._identify_research_gaps(df),
                "methodology_notes": "TNM staging analysis with French terminology support",
            }

        if audience == "community":
            return {
                **base_content,
                "focus": "Public Health Overview",
                "key_findings": insights[:3],  # Top 3 insights for general audience
                "visual_summary": "Simplified charts and trend analysis",
            }

        return base_content

    def _extract_treatment_patterns(self, df: pd.DataFrame) -> dict[str, Any]:
        """Extract treatment patterns for practitioners."""
        patterns = {}

        # Protocol analysis
        protocol_cols = [col for col in df.columns if "protocol" in col.lower()]
        for col in protocol_cols:
            patterns[f"{col}_distribution"] = df[col].value_counts().to_dict()

        return patterns

    def _generate_clinical_recommendations(self, df: pd.DataFrame) -> list[str]:
        """Generate clinical recommendations."""
        recommendations = []

        # Based on staging distribution
        tnm_cols = [col for col in df.columns if "tnm" in col.lower()]
        if tnm_cols:
            recommendations.append(
                "Consider early staging protocols for improved outcomes"
            )

        # Based on treatment diversity
        protocol_cols = [col for col in df.columns if "protocol" in col.lower()]
        if protocol_cols and len(df[protocol_cols[0]].unique()) > 3:
            recommendations.append(
                "Multiple treatment protocols suggest personalized approach needed"
            )

        return recommendations

    def _identify_research_gaps(self, df: pd.DataFrame) -> list[str]:
        """Identify research opportunities."""
        gaps = []

        # Missing survival data
        survival_cols = [
            col
            for col in df.columns
            if "survival" in col.lower() or "outcome" in col.lower()
        ]
        if not survival_cols:
            gaps.append(
                "Survival outcome data collection could enhance prognostic analysis"
            )

        # Limited follow-up data
        if "follow_up" not in str(df.columns).lower():
            gaps.append("Long-term follow-up data would enable longitudinal studies")

        return gaps


# Create instance for entry point registration
def get_surgery_spec():
    return SurgerySpec()
