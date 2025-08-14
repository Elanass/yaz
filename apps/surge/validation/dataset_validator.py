"""Unified Dataset Validator for Surgify Platform
Validates compatibility, quality, and deliverable readiness across domains.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

from ..core.csv_processor import CSVProcessor
from ..core.deliverable_factory import DeliverableFactory
from ..core.models.processing_models import (
    AudienceType,
    DataSchema,
    Deliverable,
    DeliverableFormat,
    DeliverableRequest,
    DomainInsights,
    ProcessingResult,
    QualityReport,
)
from ..core.models.processing_models import DataDomain as ProcessingDataDomain


@dataclass
class ValidationReport:
    compatible: bool
    recommendations: list[str]
    domain_adaptations: dict[str, Any]
    processing_optimizations: dict[str, Any]
    details: dict[str, Any]


class DatasetValidator:
    """Comprehensive dataset compatibility validator."""

    def __init__(self) -> None:
        self.processor = CSVProcessor()
        self.deliverable_factory = DeliverableFactory()

    def detect_format(self, dataset_path: str) -> str:
        suffix = Path(dataset_path).suffix.lower()
        if suffix in {".csv"}:
            return "csv"
        if suffix in {".xlsx", ".xls"}:
            return "excel"
        if suffix in {".json"}:
            return "json"
        return suffix.strip(".") or "unknown"

    def parse_dataset(self, dataset_path: str, dataset_format: str) -> pd.DataFrame:
        path = Path(dataset_path)
        if dataset_format == "csv":
            return pd.read_csv(path)
        if dataset_format == "excel":
            return pd.read_excel(path)
        if dataset_format == "json":
            return pd.read_json(path)
        # Fallback: try pandas auto
        return pd.read_csv(path)

    def analyze_schema(self, df: pd.DataFrame) -> DataSchema:
        # Let CSVProcessor generate a schema by auto-detecting domain (maps to ProcessingDataDomain)
        detected_domain = self.processor.schema_detector.detect_domain(df)
        return self.processor.schema_detector.generate_schema(df, detected_domain)

    def check_domain_fit(self, schema: DataSchema, domain: str) -> bool:
        # Basic check: allow GENERAL to fit anything; map known strings otherwise
        try:
            target = ProcessingDataDomain(domain) if domain else schema.domain
        except Exception:
            target = ProcessingDataDomain.GENERAL
        if target == ProcessingDataDomain.GENERAL:
            return True
        return schema.domain == target

    def assess_data_quality(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> QualityReport:
        cleaned, quality = self.processor.validator.validate_data(df, schema)
        # Attach cleaned data back into a minimal processing result-like structure if needed
        return quality

    def validate_processing_pipeline(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> bool:
        # Try running insights generation; if it works, pipeline is compatible
        try:
            # Private helper returns DomainInsights
            insights = self.processor._generate_insights(df, schema)  # type: ignore
            return isinstance(insights, DomainInsights)
        except Exception:
            return False

    async def test_deliverable_generation(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> bool:
        # Build a minimal ProcessingResult and try API deliverable
        try:
            quality = self.assess_data_quality(df, schema)
            insights = await self.processor._generate_insights(df, schema)  # type: ignore
            result = ProcessingResult(
                schema=schema, quality_report=quality, insights=insights
            )
            result.data = df
            request = DeliverableRequest(
                processing_result_id="validation",
                audience=AudienceType.TECHNICAL,
                format=DeliverableFormat.API,
                customization={},
                include_raw_data=False,
            )
            deliverable: Deliverable = (
                await self.deliverable_factory.generate_deliverable(
                    result, insights, request
                )
            )
            return bool(deliverable and (deliverable.api_response is not None))
        except Exception:
            return False

    async def validate_compatibility(
        self, dataset_path: str, domain: str
    ) -> ValidationReport:
        # 1. Format detection & parsing
        dataset_format = self.detect_format(dataset_path)
        df = self.parse_dataset(dataset_path, dataset_format)

        # 2. Schema analysis
        schema = self.analyze_schema(df)
        domain_ok = self.check_domain_fit(schema, domain)

        # 3. Data quality assessment
        quality = self.assess_data_quality(df, schema)

        # 4. Processing pipeline validation
        pipeline_ok = self.validate_processing_pipeline(df, schema)

        # 5. Deliverable generation test
        deliverable_ok = await self.test_deliverable_generation(df, schema)

        compatible = all([domain_ok, pipeline_ok, deliverable_ok])
        recommendations: list[str] = []
        if quality.completeness_score < 0.9:
            recommendations.append(
                "Improve data completeness; >10% missing values detected"
            )
        if quality.outlier_percentage > 0.05:
            recommendations.append(
                "High outlier rate; consider winsorizing or review measurement protocols"
            )
        if not domain_ok:
            recommendations.append(
                f"Dataset appears as '{schema.domain.value}'; review target domain '{domain}'"
            )
        if not pipeline_ok:
            recommendations.append(
                "Processing pipeline failed; review schema or field types"
            )
        if not deliverable_ok:
            recommendations.append(
                "Deliverable generation failed; check templates or insights"
            )

        domain_adaptations: dict[str, Any] = {
            "detected_domain": schema.domain.value,
            "target_domain": domain or schema.domain.value,
        }
        processing_optimizations: dict[str, Any] = {
            "suggested_batch_size": 10000 if len(df) > 100000 else 1000,
            "vectorized_operations": True,
            "use_polars_candidate": len(df.columns) > 100,
        }

        details: dict[str, Any] = {
            "dataset_format": dataset_format,
            "rows": len(df),
            "columns": list(df.columns),
            "quality": quality.dict(),
            "schema_fields": [f.name for f in schema.fields],
            "checked_at": datetime.utcnow().isoformat(),
        }

        return ValidationReport(
            compatible=compatible,
            recommendations=recommendations,
            domain_adaptations=domain_adaptations,
            processing_optimizations=processing_optimizations,
            details=details,
        )
