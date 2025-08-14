"""Logistics Domain Plugin
Handles supply chain, equipment, and operational logistics data.
"""

from typing import Any

import pandas as pd

from shared.core.domains import DomainSpec


class LogisticsSpec(DomainSpec):
    """Logistics domain specification."""

    def __init__(self) -> None:
        super().__init__(
            name="logistics",
            description="Medical supply chain and operational logistics analysis",
            version="1.0.0",
        )

    def schema_detect(self, columns: list[str]) -> float:
        """Detect logistics dataset based on column patterns."""
        logistics_indicators = [
            "supply",
            "inventory",
            "equipment",
            "stock",
            "vendor",
            "delivery",
            "shipment",
            "order",
            "procurement",
            "cost",
            "quantity",
            "warehouse",
            "distribution",
            "supplier",
            "lead_time",
            "backorder",
            "availability",
        ]

        matches = 0
        for col in columns:
            col_lower = col.lower()
            for indicator in logistics_indicators:
                if indicator in col_lower:
                    matches += 1
                    break

        return min(matches / len(columns), 1.0) if columns else 0.0

    def parse(self, df: pd.DataFrame) -> dict[str, Any]:
        """Parse logistics dataset."""
        parsed_data = {
            "total_items": len(df),
            "columns": list(df.columns),
            "supply_categories": {},
            "cost_analysis": {},
            "availability_metrics": {},
            "vendor_performance": {},
        }

        # Supply category analysis
        category_cols = [
            col
            for col in df.columns
            if any(
                term in col.lower() for term in ["category", "type", "class", "group"]
            )
        ]
        if category_cols:
            for col in category_cols:
                parsed_data["supply_categories"][col] = df[col].value_counts().to_dict()

        # Cost analysis
        cost_cols = [
            col
            for col in df.columns
            if any(term in col.lower() for term in ["cost", "price", "amount", "value"])
        ]
        if cost_cols:
            for col in cost_cols:
                if df[col].dtype in ["float64", "int64"]:
                    parsed_data["cost_analysis"][col] = {
                        "mean": float(df[col].mean()),
                        "median": float(df[col].median()),
                        "total": float(df[col].sum()),
                    }

        return parsed_data

    def stats(self, df: pd.DataFrame) -> dict[str, Any]:
        """Generate logistics statistics."""
        stats = {
            "summary": {
                "total_items": len(df),
                "data_completeness": (df.notna().sum() / len(df)).mean() * 100,
            },
            "cost_metrics": {},
            "supply_efficiency": {},
            "vendor_metrics": {},
        }

        # Cost analysis
        cost_cols = [
            col for col in df.columns if "cost" in col.lower() or "price" in col.lower()
        ]
        for col in cost_cols:
            if col in df.columns and df[col].dtype in ["float64", "int64"]:
                stats["cost_metrics"][col] = {
                    "total_spend": float(df[col].sum()),
                    "average_cost": float(df[col].mean()),
                    "cost_variance": float(df[col].var()),
                }

        return stats

    def insights(self, df: pd.DataFrame) -> list[str]:
        """Generate logistics insights."""
        insights = []

        insights.append(
            f"Logistics dataset contains {len(df)} items across {len(df.columns)} attributes"
        )

        # Cost insights
        cost_cols = [col for col in df.columns if "cost" in col.lower()]
        if cost_cols:
            total_cost = (
                df[cost_cols[0]].sum()
                if df[cost_cols[0]].dtype in ["float64", "int64"]
                else 0
            )
            insights.append(f"Total logistics cost tracked: ${total_cost:,.2f}")

        # Vendor diversity
        vendor_cols = [
            col
            for col in df.columns
            if "vendor" in col.lower() or "supplier" in col.lower()
        ]
        if vendor_cols:
            unique_vendors = df[vendor_cols[0]].nunique()
            insights.append(
                f"Supply chain diversity: {unique_vendors} unique vendors/suppliers"
            )

        return insights

    def deliverables(self, df: pd.DataFrame, audience: str) -> dict[str, Any]:
        """Generate audience-specific deliverables."""
        stats = self.stats(df)
        insights = self.insights(df)

        base_content = {
            "title": f"Logistics Analysis Report - {audience.title()} Edition",
            "summary": insights,
            "data_overview": stats["summary"],
            "generated_at": pd.Timestamp.now().isoformat(),
        }

        if audience == "practitioner":
            return {
                **base_content,
                "focus": "Operational Efficiency",
                "key_metrics": stats["cost_metrics"],
                "recommendations": [
                    "Optimize supply chain costs",
                    "Improve vendor management",
                ],
            }

        if audience == "researcher":
            return {
                **base_content,
                "focus": "Supply Chain Research",
                "statistical_summary": stats,
                "research_opportunities": [
                    "Cost optimization models",
                    "Vendor performance analytics",
                ],
            }

        if audience == "community":
            return {
                **base_content,
                "focus": "Healthcare Logistics Overview",
                "key_findings": insights[:2],
            }

        return base_content


def get_logistics_spec():
    return LogisticsSpec()
