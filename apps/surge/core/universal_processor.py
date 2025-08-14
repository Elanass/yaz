"""Universal Data Processing Engine for Multi-Domain Medical Analysis
Handles diverse dataset types and sources across surgical and cellular domains.
"""

import logging
from pathlib import Path
from typing import Any

import pandas as pd
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class DatasetCompatibilityReport(BaseModel):
    """Comprehensive dataset compatibility assessment."""

    compatible: bool
    dataset_format: str
    detected_domain: str
    confidence_score: float
    schema_analysis: dict[str, Any]
    quality_metrics: dict[str, float]
    recommendations: list[str]
    domain_adaptations: list[str]
    processing_optimizations: list[str]
    estimated_processing_time: float | None = None

    class Config:
        arbitrary_types_allowed = True


class UniversalDataProcessor:
    """Universal data processing engine for any medical dataset."""

    SUPPORTED_FORMATS = {
        "structured": [".csv", ".xlsx", ".xls", ".json", ".xml", ".tsv"],
        "medical": [".hl7", ".fhir", ".dicom"],
        "research": [".sav", ".dta", ".rds"],
        "text": [".txt", ".md", ".rtf"],
    }

    def __init__(self) -> None:
        self.logger = logger
        self.processing_sessions = {}

    def detect_format(self, dataset_path: str | Path) -> str:
        """Detect dataset format from file extension and content."""
        path = Path(dataset_path)
        extension = path.suffix.lower()

        # Map extensions to format types
        format_mapping = {
            ".csv": "csv",
            ".xlsx": "excel",
            ".xls": "excel",
            ".json": "json",
            ".xml": "xml",
            ".tsv": "tsv",
            ".hl7": "hl7_fhir",
            ".fhir": "hl7_fhir",
            ".dicom": "dicom",
            ".sav": "spss",
            ".dta": "stata",
            ".rds": "r_dataset",
            ".txt": "text",
            ".md": "markdown",
        }

        return format_mapping.get(extension, "unknown")

    def parse_dataset(
        self, dataset_path: str | Path, dataset_format: str
    ) -> pd.DataFrame:
        """Parse dataset based on detected format."""
        path = Path(dataset_path)

        try:
            if dataset_format == "csv":
                return pd.read_csv(path)
            if dataset_format == "excel":
                return pd.read_excel(path)
            if dataset_format == "json":
                return pd.read_json(path)
            if dataset_format == "tsv":
                return pd.read_csv(path, delimiter="\t")
            if dataset_format == "xml":
                # Basic XML parsing - may need enhancement for specific schemas
                return pd.read_xml(path)
            msg = f"Unsupported format: {dataset_format}"
            raise ValueError(msg)

        except Exception as e:
            self.logger.exception(f"Failed to parse {dataset_format} file: {e}")
            raise

    def analyze_schema(self, data: pd.DataFrame) -> dict[str, Any]:
        """Analyze dataset schema and structure."""
        schema_analysis = {
            "columns": list(data.columns),
            "shape": data.shape,
            "dtypes": data.dtypes.to_dict(),
            "memory_usage": data.memory_usage(deep=True).sum(),
            "null_counts": data.isnull().sum().to_dict(),
            "unique_counts": {col: data[col].nunique() for col in data.columns},
            "sample_values": {},
        }

        # Get sample values for each column
        for col in data.columns:
            non_null_values = data[col].dropna()
            if len(non_null_values) > 0:
                schema_analysis["sample_values"][col] = non_null_values.head(3).tolist()

        return schema_analysis

    def check_domain_fit(
        self, schema_analysis: dict[str, Any], target_domain: str
    ) -> bool:
        """Check if dataset fits the target domain requirements."""
        columns = [col.lower() for col in schema_analysis["columns"]]

        # Domain-specific column patterns
        domain_patterns = {
            "surgical": ["patient", "procedure", "outcome", "survival", "complication"],
            "cellular": ["cell", "marker", "expression", "pathology", "tumor"],
            "hybrid": ["patient", "cell", "procedure", "marker", "outcome"],
            "gastric": ["gastric", "stomach", "adenocarcinoma", "helicobacter"],
            "pathology": ["pathology", "biopsy", "grade", "stage", "histology"],
        }

        if target_domain.lower() not in domain_patterns:
            return True  # Accept unknown domains

        patterns = domain_patterns[target_domain.lower()]
        matches = sum(
            1 for pattern in patterns if any(pattern in col for col in columns)
        )

        # Require at least 2 pattern matches for domain compatibility
        return matches >= 2

    def assess_data_quality(self, data: pd.DataFrame) -> dict[str, float]:
        """Assess overall data quality metrics."""
        total_cells = data.shape[0] * data.shape[1]

        return {
            "completeness": 1 - (data.isnull().sum().sum() / total_cells),
            "consistency": self._calculate_consistency_score(data),
            "validity": self._calculate_validity_score(data),
            "outlier_percentage": self._calculate_outlier_percentage(data),
        }

    def _calculate_consistency_score(self, data: pd.DataFrame) -> float:
        """Calculate data consistency score."""
        consistency_score = 1.0

        # Check for obvious inconsistencies
        for col in data.select_dtypes(include=["object"]).columns:
            unique_values = data[col].dropna().unique()
            if len(unique_values) > 0:
                # Penalize columns with too many unique values (possible data entry errors)
                uniqueness_ratio = len(unique_values) / len(data[col].dropna())
                if uniqueness_ratio > 0.8:  # More than 80% unique values
                    consistency_score *= 0.9

        return max(0.0, consistency_score)

    def _calculate_validity_score(self, data: pd.DataFrame) -> float:
        """Calculate data validity score."""
        validity_score = 1.0

        # Check numeric columns for reasonable ranges
        for col in data.select_dtypes(include=["number"]).columns:
            col_data = data[col].dropna()
            if len(col_data) > 0:
                # Check for unreasonable values (e.g., negative ages, impossible dates)
                if "age" in col.lower() and (col_data < 0).any():
                    validity_score *= 0.8

                # Check for extreme outliers
                if len(col_data) > 1:
                    q1, q3 = col_data.quantile([0.25, 0.75])
                    iqr = q3 - q1
                    if iqr > 0:
                        outliers = (
                            (col_data < (q1 - 3 * iqr)) | (col_data > (q3 + 3 * iqr))
                        ).sum()
                        outlier_ratio = outliers / len(col_data)
                        if outlier_ratio > 0.1:  # More than 10% outliers
                            validity_score *= 0.9

        return max(0.0, validity_score)

    def _calculate_outlier_percentage(self, data: pd.DataFrame) -> float:
        """Calculate percentage of outliers in numeric data."""
        total_numeric_values = 0
        total_outliers = 0

        for col in data.select_dtypes(include=["number"]).columns:
            col_data = data[col].dropna()
            if len(col_data) > 1:
                q1, q3 = col_data.quantile([0.25, 0.75])
                iqr = q3 - q1
                if iqr > 0:
                    outliers = (
                        (col_data < (q1 - 1.5 * iqr)) | (col_data > (q3 + 1.5 * iqr))
                    ).sum()
                    total_outliers += outliers
                    total_numeric_values += len(col_data)

        return (
            total_outliers / total_numeric_values if total_numeric_values > 0 else 0.0
        )

    def validate_processing_pipeline(self, data: pd.DataFrame, domain: str) -> bool:
        """Validate that the data can be processed through the domain pipeline."""
        try:
            # Basic validation checks
            if data.empty:
                return False

            # Check minimum requirements for medical data
            if domain in ["surgical", "cellular", "hybrid"]:
                # Must have at least one identifier column
                id_columns = [
                    col
                    for col in data.columns
                    if any(
                        id_word in col.lower()
                        for id_word in ["id", "patient", "case", "specimen"]
                    )
                ]
                if not id_columns:
                    return False

            return True

        except Exception as e:
            self.logger.exception(f"Pipeline validation failed: {e}")
            return False

    def test_deliverable_generation(self, data: pd.DataFrame, domain: str) -> bool:
        """Test that deliverables can be generated from the data."""
        try:
            # Check if data has sufficient content for deliverable generation
            if data.shape[0] < 5:  # Need at least 5 rows
                return False

            # Check for at least one numeric column for analysis
            numeric_cols = data.select_dtypes(include=["number"]).columns
            return len(numeric_cols) != 0

        except Exception as e:
            self.logger.exception(f"Deliverable generation test failed: {e}")
            return False

    def generate_recommendations(
        self, data: pd.DataFrame, quality_metrics: dict[str, float]
    ) -> list[str]:
        """Generate recommendations for improving data quality and processing."""
        recommendations = []

        if quality_metrics["completeness"] < 0.8:
            recommendations.append("Consider data cleaning to address missing values")

        if quality_metrics["consistency"] < 0.8:
            recommendations.append(
                "Review data entry procedures to improve consistency"
            )

        if quality_metrics["validity"] < 0.8:
            recommendations.append("Validate data ranges and remove invalid entries")

        if quality_metrics["outlier_percentage"] > 0.15:
            recommendations.append("Investigate and handle outliers in numeric data")

        # Column-specific recommendations
        if data.shape[1] > 50:
            recommendations.append("Consider feature selection for large datasets")

        if data.shape[0] < 100:
            recommendations.append(
                "Small dataset - consider additional data collection"
            )

        return recommendations

    def suggest_adaptations(
        self, schema_analysis: dict[str, Any], target_domain: str
    ) -> list[str]:
        """Suggest domain-specific adaptations."""
        adaptations = []
        columns = [col.lower() for col in schema_analysis["columns"]]

        if target_domain == "surgical":
            if not any("outcome" in col for col in columns):
                adaptations.append("Add outcome variables for surgical analysis")
            if not any("procedure" in col for col in columns):
                adaptations.append("Include procedure classification")

        elif target_domain == "cellular":
            if not any("marker" in col for col in columns):
                adaptations.append("Add cellular markers or biomarkers")
            if not any("expression" in col for col in columns):
                adaptations.append("Include expression level data")

        elif target_domain == "hybrid":
            adaptations.append("Ensure both patient-level and cellular-level variables")
            adaptations.append("Consider temporal relationships between data types")

        return adaptations

    def optimize_pipeline(self, data: pd.DataFrame) -> list[str]:
        """Suggest processing pipeline optimizations."""
        optimizations = []

        # Memory optimizations
        if data.memory_usage(deep=True).sum() > 100_000_000:  # >100MB
            optimizations.append("Enable chunked processing for large datasets")

        # Performance optimizations
        if data.shape[0] > 50_000:
            optimizations.append("Consider parallel processing for large row counts")

        if data.shape[1] > 100:
            optimizations.append("Implement feature selection to reduce dimensionality")

        # Domain-specific optimizations
        text_columns = data.select_dtypes(include=["object"]).columns
        if len(text_columns) > 10:
            optimizations.append(
                "Consider text preprocessing pipeline for categorical data"
            )

        return optimizations

    def validate_compatibility(
        self, dataset_path: str | Path, domain: str
    ) -> DatasetCompatibilityReport:
        """Comprehensive dataset compatibility validation."""
        try:
            # 1. Format Detection & Parsing
            dataset_format = self.detect_format(dataset_path)
            if dataset_format == "unknown":
                return DatasetCompatibilityReport(
                    compatible=False,
                    dataset_format=dataset_format,
                    detected_domain="unknown",
                    confidence_score=0.0,
                    schema_analysis={},
                    quality_metrics={},
                    recommendations=["Unsupported file format"],
                    domain_adaptations=[],
                    processing_optimizations=[],
                )

            parsed_data = self.parse_dataset(dataset_path, dataset_format)

            # 2. Schema Analysis
            schema_analysis = self.analyze_schema(parsed_data)
            domain_compatibility = self.check_domain_fit(schema_analysis, domain)

            # 3. Data Quality Assessment
            quality_metrics = self.assess_data_quality(parsed_data)

            # 4. Processing Pipeline Validation
            pipeline_compatibility = self.validate_processing_pipeline(
                parsed_data, domain
            )

            # 5. Deliverable Generation Test
            deliverable_test = self.test_deliverable_generation(parsed_data, domain)

            # Generate overall compatibility
            compatibility_checks = [
                domain_compatibility,
                pipeline_compatibility,
                deliverable_test,
            ]
            overall_compatible = all(compatibility_checks)

            # Calculate confidence score
            quality_score = sum(quality_metrics.values()) / len(quality_metrics)
            confidence_score = quality_score * (
                sum(compatibility_checks) / len(compatibility_checks)
            )

            return DatasetCompatibilityReport(
                compatible=overall_compatible,
                dataset_format=dataset_format,
                detected_domain=domain,
                confidence_score=confidence_score,
                schema_analysis=schema_analysis,
                quality_metrics=quality_metrics,
                recommendations=self.generate_recommendations(
                    parsed_data, quality_metrics
                ),
                domain_adaptations=self.suggest_adaptations(schema_analysis, domain),
                processing_optimizations=self.optimize_pipeline(parsed_data),
                estimated_processing_time=self._estimate_processing_time(parsed_data),
            )

        except Exception as e:
            self.logger.exception(f"Compatibility validation failed: {e}")
            return DatasetCompatibilityReport(
                compatible=False,
                dataset_format="error",
                detected_domain="error",
                confidence_score=0.0,
                schema_analysis={},
                quality_metrics={},
                recommendations=[f"Validation failed: {e!s}"],
                domain_adaptations=[],
                processing_optimizations=[],
            )

    def _estimate_processing_time(self, data: pd.DataFrame) -> float:
        """Estimate processing time in seconds."""
        # Simple heuristic based on data size and complexity
        base_time = 1.0  # Base 1 second
        row_factor = data.shape[0] / 1000  # 1ms per 1000 rows
        col_factor = data.shape[1] / 100  # 1ms per 100 columns

        return base_time + row_factor + col_factor
