"""
Advanced CSV Processing Engine for Surgify Platform
Handles intelligent schema detection, validation, and domain-specific processing
"""

import asyncio
import io
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from .models.processing_models import (DataSchema, DomainInsights,
                                       ProcessingResult, QualityReport,
                                       ValidationError)


class DataDomain(Enum):
    """Supported data domains"""

    SURGERY = "surgery"
    LOGISTICS = "logistics"
    INSURANCE = "insurance"
    GENERAL = "general"


class FieldType(Enum):
    """Field data types"""

    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATE = "date"
    TEXT = "text"
    MEDICAL_CODE = "medical_code"
    IDENTIFIER = "identifier"


@dataclass
class FieldSchema:
    """Schema definition for a data field"""

    name: str
    field_type: FieldType
    is_required: bool = False
    constraints: Dict[str, Any] = field(default_factory=dict)
    domain_specific: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingConfig:
    """Configuration for CSV processing"""

    max_file_size_mb: int = 100
    streaming_threshold_rows: int = 10000
    validation_sample_size: int = 1000
    auto_detect_types: bool = True
    domain: Optional[DataDomain] = None


class SchemaDetector:
    """Intelligent schema detection for CSV files"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._domain_patterns = self._load_domain_patterns()

    def _load_domain_patterns(self) -> Dict[DataDomain, Dict[str, List[str]]]:
        """Load patterns for domain detection"""
        return {
            DataDomain.SURGERY: {
                "headers": [
                    "patient_id",
                    "patient",
                    "surgery",
                    "procedure",
                    "operation",
                    "diagnosis",
                    "complication",
                    "outcome",
                    "mortality",
                    "morbidity",
                    "stage",
                    "histology",
                    "tumor",
                    "cancer",
                    "treatment",
                    "therapy",
                    "hospital",
                    "surgeon",
                    "age",
                    "gender",
                    "bmi",
                    "ast",
                    "operative_time",
                ],
                "values": [
                    "IA",
                    "IB",
                    "II",
                    "III",
                    "IV",
                    "T1",
                    "T2",
                    "T3",
                    "T4",
                    "N0",
                    "N1",
                    "M0",
                    "M1",
                ],
            },
            DataDomain.LOGISTICS: {
                "headers": [
                    "resource",
                    "allocation",
                    "capacity",
                    "utilization",
                    "workflow",
                    "efficiency",
                    "throughput",
                    "bottleneck",
                    "delay",
                    "schedule",
                    "inventory",
                    "supply",
                    "demand",
                    "cost",
                    "budget",
                    "roi",
                ],
                "values": [
                    "available",
                    "allocated",
                    "in_use",
                    "maintenance",
                    "scheduled",
                ],
            },
            DataDomain.INSURANCE: {
                "headers": [
                    "claim",
                    "policy",
                    "premium",
                    "coverage",
                    "deductible",
                    "copay",
                    "risk",
                    "fraud",
                    "underwriting",
                    "actuarial",
                    "loss_ratio",
                    "member",
                    "provider",
                    "network",
                    "authorization",
                    "denial",
                ],
                "values": [
                    "approved",
                    "denied",
                    "pending",
                    "in_network",
                    "out_network",
                ],
            },
        }

    def detect_domain(self, df: pd.DataFrame) -> DataDomain:
        """Detect the data domain based on headers and content"""
        headers = [col.lower().replace(" ", "_") for col in df.columns]

        domain_scores = {}
        for domain, patterns in self._domain_patterns.items():
            score = 0

            # Score based on header matches
            header_matches = sum(
                1 for h in headers if any(p in h for p in patterns["headers"])
            )
            score += header_matches * 2

            # Score based on value patterns (sample first 100 rows)
            sample_df = df.head(100)
            for col in sample_df.select_dtypes(include=["object"]).columns:
                values = sample_df[col].astype(str).str.lower().tolist()
                value_matches = sum(
                    1 for v in values if any(p in v for p in patterns["values"])
                )
                score += value_matches

            domain_scores[domain] = score

        if max(domain_scores.values()) == 0:
            return DataDomain.GENERAL

        return max(domain_scores, key=domain_scores.get)

    def detect_field_type(
        self, series: pd.Series, field_name: str, domain: DataDomain
    ) -> FieldType:
        """Detect the type of a field"""
        field_name_lower = field_name.lower().replace(" ", "_")

        # Check for identifiers first
        if any(id_term in field_name_lower for id_term in ["id", "uuid", "key"]):
            return FieldType.IDENTIFIER

        # Check for dates
        if any(
            date_term in field_name_lower
            for date_term in ["date", "time", "created", "updated"]
        ):
            return FieldType.DATE

        # Check for medical codes (domain-specific)
        if domain == DataDomain.SURGERY and any(
            code_term in field_name_lower
            for code_term in ["icd", "cpt", "stage", "histology"]
        ):
            return FieldType.MEDICAL_CODE

        # Analyze the data
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return FieldType.TEXT

        # Check if numeric
        try:
            pd.to_numeric(non_null_series)
            return FieldType.NUMERIC
        except (ValueError, TypeError):
            pass

        # Check if categorical (low cardinality)
        unique_ratio = len(non_null_series.unique()) / len(non_null_series)
        if unique_ratio < 0.1:  # Less than 10% unique values
            return FieldType.CATEGORICAL

        return FieldType.TEXT

    def generate_schema(self, df: pd.DataFrame, domain: DataDomain) -> DataSchema:
        """Generate a complete schema for the dataframe"""
        fields = []
        for col in df.columns:
            field_type = self.detect_field_type(df[col], col, domain)

            # Determine if field is required based on null percentage
            null_percentage = df[col].isnull().sum() / len(df)
            is_required = null_percentage < 0.1  # Less than 10% nulls

            # Generate constraints
            constraints = {}
            if field_type == FieldType.NUMERIC:
                constraints["min"] = (
                    float(df[col].min()) if not pd.isna(df[col].min()) else None
                )
                constraints["max"] = (
                    float(df[col].max()) if not pd.isna(df[col].max()) else None
                )
            elif field_type == FieldType.CATEGORICAL:
                constraints["allowed_values"] = df[col].dropna().unique().tolist()

            fields.append(
                FieldSchema(
                    name=col,
                    field_type=field_type,
                    is_required=is_required,
                    constraints=constraints,
                )
            )

        return DataSchema(
            domain=domain,
            fields=fields,
            total_fields=len(fields),
            detected_at=datetime.utcnow(),
        )


class DataValidator:
    """Advanced data validation engine"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate_data(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> Tuple[pd.DataFrame, QualityReport]:
        """Validate data against schema and return cleaned data with quality report"""
        errors = []
        warnings = []
        cleaned_df = df.copy()

        # Validate each field
        for field in schema.fields:
            if field.name not in df.columns:
                if field.is_required:
                    errors.append(
                        ValidationError(
                            field=field.name,
                            error_type="missing_required_field",
                            message=f"Required field '{field.name}' is missing",
                        )
                    )
                continue

            # Validate field data
            field_errors, field_warnings = self._validate_field(
                cleaned_df[field.name], field
            )
            errors.extend(field_errors)
            warnings.extend(field_warnings)

        # Calculate quality metrics
        total_cells = df.shape[0] * df.shape[1]
        null_cells = df.isnull().sum().sum()
        completeness = 1 - (null_cells / total_cells)

        # Detect outliers for numeric columns
        outlier_percentage = self._calculate_outlier_percentage(df)

        quality_report = QualityReport(
            completeness_score=completeness,
            consistency_score=self._calculate_consistency_score(df, schema),
            validity_score=1 - (len(errors) / max(len(schema.fields), 1)),
            outlier_percentage=outlier_percentage,
            errors=errors,
            warnings=warnings,
            total_records=len(df),
            valid_records=len(df)
            - len([e for e in errors if e.error_type == "invalid_record"]),
        )

        return cleaned_df, quality_report

    def _validate_field(
        self, series: pd.Series, field: FieldSchema
    ) -> Tuple[List[ValidationError], List[str]]:
        """Validate a single field"""
        errors = []
        warnings = []

        # Check required fields
        if field.is_required and series.isnull().any():
            null_count = series.isnull().sum()
            errors.append(
                ValidationError(
                    field=field.name,
                    error_type="null_required_field",
                    message=f"Required field has {null_count} null values",
                )
            )

        # Type-specific validation
        if field.field_type == FieldType.NUMERIC:
            non_numeric = (
                pd.to_numeric(series, errors="coerce").isnull() & series.notnull()
            )
            if non_numeric.any():
                errors.append(
                    ValidationError(
                        field=field.name,
                        error_type="invalid_numeric",
                        message=f"Found {non_numeric.sum()} non-numeric values in numeric field",
                    )
                )

        # Constraint validation
        if "min" in field.constraints and field.field_type == FieldType.NUMERIC:
            below_min = series < field.constraints["min"]
            if below_min.any():
                warnings.append(
                    f"Field '{field.name}' has {below_min.sum()} values below minimum"
                )

        if "allowed_values" in field.constraints:
            invalid_values = (
                ~series.isin(field.constraints["allowed_values"]) & series.notnull()
            )
            if invalid_values.any():
                errors.append(
                    ValidationError(
                        field=field.name,
                        error_type="invalid_categorical_value",
                        message=f"Found {invalid_values.sum()} invalid categorical values",
                    )
                )

        return errors, warnings

    def _calculate_consistency_score(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> float:
        """Calculate data consistency score"""
        consistency_issues = 0
        total_checks = 0

        for field in schema.fields:
            if field.name not in df.columns:
                continue

            series = df[field.name]
            total_checks += 1

            # Check for format consistency in text fields
            if field.field_type == FieldType.TEXT:
                if self._has_format_inconsistency(series):
                    consistency_issues += 1

        return 1 - (consistency_issues / max(total_checks, 1))

    def _has_format_inconsistency(self, series: pd.Series) -> bool:
        """Check if a text series has format inconsistencies"""
        # Simple check for mixed case patterns
        non_null = series.dropna().astype(str)
        if len(non_null) < 2:
            return False

        upper_count = sum(1 for s in non_null if s.isupper())
        lower_count = sum(1 for s in non_null if s.islower())
        title_count = sum(1 for s in non_null if s.istitle())

        # If we have significant mixing of cases, consider it inconsistent
        total = len(non_null)
        if upper_count > 0.1 * total and lower_count > 0.1 * total:
            return True
        if title_count > 0.1 * total and (
            upper_count > 0.1 * total or lower_count > 0.1 * total
        ):
            return True

        return False

    def _calculate_outlier_percentage(self, df: pd.DataFrame) -> float:
        """Calculate percentage of outliers in numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) == 0:
            return 0.0

        total_outliers = 0
        total_values = 0

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 4:  # Need at least 4 values for IQR
                continue

            Q1 = series.quantile(0.25)
            Q3 = series.quantile(0.75)
            IQR = Q3 - Q1

            outliers = (series < (Q1 - 1.5 * IQR)) | (series > (Q3 + 1.5 * IQR))
            total_outliers += outliers.sum()
            total_values += len(series)

        return total_outliers / max(total_values, 1)


class CSVProcessor:
    """Main CSV processing engine"""

    def __init__(self, config: Optional[ProcessingConfig] = None):
        self.config = config or ProcessingConfig()
        self.schema_detector = SchemaDetector()
        self.validator = DataValidator()
        self.logger = logging.getLogger(__name__)

    async def analyze_csv(
        self,
        file_path: Optional[str] = None,
        file_content: Optional[bytes] = None,
        domain: Optional[str] = None,
    ) -> ProcessingResult:
        """
        Analyze CSV data and generate comprehensive processing result
        """
        try:
            # Load data
            if file_path:
                df = await self._load_csv_file(file_path)
            elif file_content:
                df = await self._load_csv_content(file_content)
            else:
                raise ValueError("Either file_path or file_content must be provided")

            # Detect domain if not specified
            detected_domain = (
                DataDomain(domain) if domain else self.schema_detector.detect_domain(df)
            )

            # Generate schema
            schema = self.schema_detector.generate_schema(df, detected_domain)

            # Validate data
            cleaned_df, quality_report = self.validator.validate_data(df, schema)

            # Generate insights
            insights = await self._generate_insights(cleaned_df, schema)

            # Create processing result
            result = ProcessingResult(
                schema=schema,
                data=cleaned_df,
                quality_report=quality_report,
                insights=insights,
                processing_metadata={
                    "original_rows": len(df),
                    "processed_rows": len(cleaned_df),
                    "processing_time": datetime.utcnow(),
                    "domain": detected_domain.value,
                },
            )

            self.logger.info(
                f"Successfully processed CSV with {len(df)} rows, domain: {detected_domain.value}"
            )
            return result

        except Exception as e:
            self.logger.error(f"Error processing CSV: {str(e)}")
            raise

    async def _load_csv_file(self, file_path: str) -> pd.DataFrame:
        """Load CSV from file path"""
        return pd.read_csv(file_path, encoding="utf-8")

    async def _load_csv_content(self, content: bytes) -> pd.DataFrame:
        """Load CSV from byte content"""
        return pd.read_csv(io.BytesIO(content), encoding="utf-8")

    async def _generate_insights(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> DomainInsights:
        """Generate domain-specific insights"""
        # This will be expanded with domain-specific logic
        basic_stats = {}

        # Generate basic statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            basic_stats[col] = {
                "mean": float(df[col].mean()),
                "median": float(df[col].median()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "null_count": int(df[col].isnull().sum()),
            }

        # Generate categorical summaries
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns
        categorical_stats = {}
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            categorical_stats[col] = {
                "unique_count": len(value_counts),
                "most_common": value_counts.head(5).to_dict(),
                "null_count": int(df[col].isnull().sum()),
            }

        return DomainInsights(
            domain=schema.domain,
            statistical_summary=basic_stats,
            categorical_summary=categorical_stats,
            correlations=self._calculate_correlations(df),
            patterns=self._detect_patterns(df, schema),
            recommendations=self._generate_recommendations(df, schema),
        )

    def _calculate_correlations(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns"""
        numeric_df = df.select_dtypes(include=[np.number])
        if len(numeric_df.columns) < 2:
            return {}

        corr_matrix = numeric_df.corr()

        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(corr_matrix.columns):
            for j, col2 in enumerate(corr_matrix.columns):
                if i < j:  # Avoid duplicates
                    corr_value = corr_matrix.loc[col1, col2]
                    if abs(corr_value) > 0.7:  # Strong correlation threshold
                        strong_correlations.append(
                            {
                                "field1": col1,
                                "field2": col2,
                                "correlation": float(corr_value),
                            }
                        )

        return {
            "matrix": corr_matrix.to_dict(),
            "strong_correlations": strong_correlations,
        }

    def _detect_patterns(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> List[Dict[str, Any]]:
        """Detect interesting patterns in the data"""
        patterns = []

        # Check for missing data patterns
        missing_by_row = df.isnull().sum(axis=1)
        if missing_by_row.max() > len(df.columns) * 0.5:
            patterns.append(
                {
                    "type": "high_missing_rows",
                    "description": f"Found {(missing_by_row > len(df.columns) * 0.5).sum()} rows with >50% missing data",
                    "severity": "warning",
                }
            )

        # Check for duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            patterns.append(
                {
                    "type": "duplicate_rows",
                    "description": f"Found {duplicate_count} duplicate rows",
                    "severity": "info",
                }
            )

        return patterns

    def _generate_recommendations(
        self, df: pd.DataFrame, schema: DataSchema
    ) -> List[str]:
        """Generate recommendations for data improvement"""
        recommendations = []

        # Check for fields with high null rates
        for field in schema.fields:
            if field.name in df.columns:
                null_rate = df[field.name].isnull().sum() / len(df)
                if null_rate > 0.3:
                    recommendations.append(
                        f"Consider improving data collection for '{field.name}' (30%+ missing values)"
                    )

        # Check for categorical fields with high cardinality
        categorical_fields = [
            f for f in schema.fields if f.field_type == FieldType.CATEGORICAL
        ]
        for field in categorical_fields:
            if field.name in df.columns:
                unique_ratio = len(df[field.name].unique()) / len(df)
                if unique_ratio > 0.5:
                    recommendations.append(
                        f"Field '{field.name}' may need standardization (high variety of values)"
                    )

        return recommendations
