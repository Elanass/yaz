"""Insurance Domain Plugin
Handles insurance claims, coverage, and reimbursement data analysis.
"""

from typing import Any

import pandas as pd

from src.shared.core.domains import DomainSpec


class InsuranceSpec(DomainSpec):
    """Insurance domain specification."""

    def __init__(self) -> None:
        super().__init__(
            name="insurance",
            description="Insurance claims and reimbursement analysis",
            version="1.0.0",
        )

    def schema_detect(self, columns: list[str]) -> float:
        """Detect insurance dataset based on column patterns."""
        insurance_indicators = [
            "claim",
            "coverage",
            "premium",
            "deductible",
            "copay",
            "reimbursement",
            "policy",
            "benefit",
            "provider",
            "diagnosis_code",
            "procedure_code",
            "cpt",
            "icd",
            "amount",
            "approved",
            "denied",
            "pending",
        ]

        matches = 0
        for col in columns:
            col_lower = col.lower()
            for indicator in insurance_indicators:
                if indicator in col_lower:
                    matches += 1
                    break

        return min(matches / len(columns), 1.0) if columns else 0.0

    def parse(self, df: pd.DataFrame) -> dict[str, Any]:
        """Parse insurance dataset."""
        parsed_data = {
            "total_claims": len(df),
            "columns": list(df.columns),
            "claim_status": {},
            "financial_metrics": {},
            "coverage_analysis": {},
            "provider_performance": {},
        }

        # Claim status analysis
        status_cols = [col for col in df.columns if "status" in col.lower()]
        if status_cols:
            for col in status_cols:
                parsed_data["claim_status"][col] = df[col].value_counts().to_dict()

        # Financial metrics
        amount_cols = [
            col
            for col in df.columns
            if any(
                term in col.lower() for term in ["amount", "cost", "charge", "payment"]
            )
        ]
        if amount_cols:
            for col in amount_cols:
                if df[col].dtype in ["float64", "int64"]:
                    parsed_data["financial_metrics"][col] = {
                        "total": float(df[col].sum()),
                        "average": float(df[col].mean()),
                        "median": float(df[col].median()),
                    }

        return parsed_data

    def stats(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate insurance statistics."""
        stats = {
            "summary": {
                "total_claims": len(df),
                "data_completeness": (df.notna().sum() / len(df)).mean() * 100,
            },
            "financial_summary": {},
            "approval_rates": {},
            "reimbursement_metrics": {},
        }

        # Financial summary
        amount_cols = [col for col in df.columns if "amount" in col.lower()]
        for col in amount_cols:
            if col in df.columns and df[col].dtype in ["float64", "int64"]:
                stats["financial_summary"][col] = {
                    "total_value": float(df[col].sum()),
                    "average_claim": float(df[col].mean()),
                    "claim_variance": float(df[col].var()),
                }

        # Approval rate analysis
        status_cols = [col for col in df.columns if "status" in col.lower()]
        for col in status_cols:
            if col in df.columns:
                status_counts = df[col].value_counts()
                total = len(df)
                stats["approval_rates"][col] = {
                    "distribution": status_counts.to_dict(),
                    "approval_rate": status_counts.get("approved", 0) / total * 100
                    if total > 0
                    else 0,
                }

        return stats

    def insights(self, df: pd.DataFrame) -> list[str]:
        """Generate insurance insights."""
        insights = []

        insights.append(
            f"Insurance dataset contains {len(df)} claims with {len(df.columns)} data fields"
        )

        # Financial insights
        amount_cols = [col for col in df.columns if "amount" in col.lower()]
        if amount_cols:
            total_amount = (
                df[amount_cols[0]].sum()
                if df[amount_cols[0]].dtype in ["float64", "int64"]
                else 0
            )
            insights.append(f"Total claim value: ${total_amount:,.2f}")

        # Approval rate insights
        status_cols = [col for col in df.columns if "status" in col.lower()]
        if status_cols:
            approved = df[status_cols[0]].str.lower().str.contains("approved").sum()
            total = len(df)
            approval_rate = (approved / total * 100) if total > 0 else 0
            insights.append(f"Claim approval rate: {approval_rate:.1f}%")

        # Provider analysis
        provider_cols = [col for col in df.columns if "provider" in col.lower()]
        if provider_cols:
            unique_providers = df[provider_cols[0]].nunique()
            insights.append(f"Network includes {unique_providers} healthcare providers")

        return insights

    def deliverables(self, df: pd.DataFrame, audience: str) -> dict[str, Any]:
        """Generate audience-specific deliverables."""
        stats = self.stats(df)
        insights = self.insights(df)

        base_content = {
            "title": f"Insurance Analysis Report - {audience.title()} Edition",
            "summary": insights,
            "data_overview": stats["summary"],
            "generated_at": pd.Timestamp.now().isoformat(),
        }

        if audience == "practitioner":
            return {
                **base_content,
                "focus": "Reimbursement Optimization",
                "key_metrics": stats["financial_summary"],
                "recommendations": [
                    "Optimize claim submission processes",
                    "Focus on high-approval procedures",
                ],
            }

        if audience == "researcher":
            return {
                **base_content,
                "focus": "Healthcare Economics Research",
                "statistical_summary": stats,
                "research_opportunities": [
                    "Reimbursement pattern analysis",
                    "Provider network optimization",
                ],
            }

        if audience == "community":
            return {
                **base_content,
                "focus": "Healthcare Coverage Overview",
                "key_findings": insights[:2],
            }

        return base_content


def get_insurance_spec():
    return InsuranceSpec()
