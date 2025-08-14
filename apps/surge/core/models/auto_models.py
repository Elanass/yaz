"""Dynamic Auto-Generated Models Module
Automatically generates Pydantic models from CSV schema detection.
"""

import json
import logging
from datetime import datetime
from typing import Any, Optional

import pandas as pd
from pydantic import BaseModel, Field, create_model

from .processing_models import DataDomain, FieldType


logger = logging.getLogger(__name__)


class AutoModelRegistry:
    """Registry for dynamically generated models."""

    def __init__(self) -> None:
        self._models: dict[str, type[BaseModel]] = {}
        self._schemas: dict[str, dict[str, Any]] = {}

    def register_model(
        self, name: str, model_class: type[BaseModel], schema: dict[str, Any]
    ) -> None:
        """Register a dynamically generated model."""
        self._models[name] = model_class
        self._schemas[name] = schema
        logger.info(f"Registered auto-generated model: {name}")

    def get_model(self, name: str) -> type[BaseModel] | None:
        """Get a registered model by name."""
        return self._models.get(name)

    def get_schema(self, name: str) -> dict[str, Any] | None:
        """Get schema definition for a model."""
        return self._schemas.get(name)

    def list_models(self) -> list[str]:
        """List all registered model names."""
        return list(self._models.keys())

    def get_all_schemas(self) -> dict[str, dict[str, Any]]:
        """Get all registered schemas."""
        return self._schemas.copy()


# Global registry instance
auto_model_registry = AutoModelRegistry()


class AutoModelGenerator:
    """Generates Pydantic models from CSV schema detection."""

    def __init__(self) -> None:
        self.registry = auto_model_registry

    def generate_model_from_dataframe(
        self, df: pd.DataFrame, model_name: str, domain: DataDomain = DataDomain.GENERAL
    ) -> type[BaseModel]:
        """Generate a Pydantic model from a pandas DataFrame."""
        # Generate field definitions
        field_definitions = {}
        schema_info = {}

        for column in df.columns:
            field_type, pydantic_type, constraints = self._infer_field_type(
                df[column], column
            )

            # Create field with constraints
            field_definition = Field(**constraints)
            field_definitions[column] = (pydantic_type, field_definition)

            # Store schema info
            schema_info[column] = {
                "field_type": field_type.value,
                "python_type": str(pydantic_type),
                "constraints": constraints,
                "sample_values": df[column].dropna().head(3).tolist(),
                "null_count": df[column].isnull().sum(),
                "unique_count": df[column].nunique(),
            }

        # Add metadata fields
        field_definitions.update(
            {
                "record_id": (
                    Optional[str],
                    Field(None, description="Auto-generated record ID"),
                ),
                "source_file": (
                    Optional[str],
                    Field(None, description="Source filename"),
                ),
                "ingested_at": (
                    datetime,
                    Field(
                        default_factory=datetime.utcnow,
                        description="Ingestion timestamp",
                    ),
                ),
                "domain": (
                    str,
                    Field(
                        default=domain.value
                        if hasattr(domain, "value")
                        else str(domain),
                        description="Data domain",
                    ),
                ),
                "schema_version": (
                    str,
                    Field(default="1.0", description="Schema version"),
                ),
            }
        )

        # Create the dynamic model
        dynamic_model = create_model(
            model_name, **field_definitions, __base__=BaseModel, __module__=__name__
        )

        # Add custom configuration
        dynamic_model.__config__ = type(
            "Config",
            (),
            {
                "schema_extra": {
                    "description": f"Auto-generated model for {model_name}",
                    "domain": domain.value if hasattr(domain, "value") else str(domain),
                    "generated_at": datetime.utcnow().isoformat(),
                    "source_schema": schema_info,
                }
            },
        )

        # Register the model
        self.registry.register_model(
            model_name,
            dynamic_model,
            {
                "name": model_name,
                "domain": domain.value if hasattr(domain, "value") else str(domain),
                "fields": schema_info,
                "generated_at": datetime.utcnow().isoformat(),
                "record_count": len(df),
            },
        )

        return dynamic_model

    def _infer_field_type(self, series: pd.Series, column_name: str) -> tuple:
        """Infer field type and generate Pydantic type with constraints."""
        # Handle missing values
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return (
                FieldType.TEXT,
                Optional[str],
                {"default": None, "description": f"Column {column_name}"},
            )

        # Check for numeric types
        if pd.api.types.is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                constraints = {
                    "description": f"Integer field: {column_name}",
                    "ge": int(non_null_series.min())
                    if not pd.isna(non_null_series.min())
                    else None,
                    "le": int(non_null_series.max())
                    if not pd.isna(non_null_series.max())
                    else None,
                }
                return FieldType.NUMERIC, int, constraints
            constraints = {
                "description": f"Float field: {column_name}",
                "ge": float(non_null_series.min())
                if not pd.isna(non_null_series.min())
                else None,
                "le": float(non_null_series.max())
                if not pd.isna(non_null_series.max())
                else None,
            }
            return FieldType.NUMERIC, float, constraints

        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(series):
            constraints = {"description": f"Datetime field: {column_name}"}
            return FieldType.DATE, Optional[datetime], constraints

        # Try to parse as datetime
        try:
            pd.to_datetime(non_null_series.head(10))
            constraints = {"description": f"Date string field: {column_name}"}
            return FieldType.DATE, Optional[str], constraints
        except:
            pass

        # Check for categorical data
        unique_values = non_null_series.unique()
        if len(unique_values) <= 20 and len(unique_values) < len(non_null_series) * 0.5:
            constraints = {
                "description": f"Categorical field: {column_name}",
                "pattern": None,  # Could add regex pattern here
            }
            return FieldType.CATEGORICAL, str, constraints

        # Check for ID patterns
        if any(
            keyword in column_name.lower()
            for keyword in ["id", "identifier", "code", "number"]
        ):
            constraints = {
                "description": f"Identifier field: {column_name}",
                "min_length": 1 if len(non_null_series) > 0 else 0,
            }
            return FieldType.IDENTIFIER, str, constraints

        # Default to text
        max_length = (
            int(non_null_series.astype(str).str.len().max())
            if len(non_null_series) > 0
            else 255
        )
        constraints = {
            "description": f"Text field: {column_name}",
            "max_length": min(max_length * 2, 1000),  # Allow for some growth
        }
        return FieldType.TEXT, str, constraints

    def generate_model_from_file(
        self, file_path: str, model_name: str | None = None
    ) -> type[BaseModel]:
        """Generate model from CSV/Excel/JSON file."""
        import os

        base_name = os.path.splitext(os.path.basename(file_path))[0]
        ext = os.path.splitext(file_path)[1].lower()
        df = None
        if ext == ".csv":
            df = pd.read_csv(file_path)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(file_path)
        elif ext == ".json":
            with open(file_path) as f:
                data = json.load(f)
            # If data is a list of dicts, convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If dict of records, try to infer
                if all(isinstance(v, dict) for v in data.values()):
                    df = pd.DataFrame(list(data.values()))
                else:
                    df = pd.DataFrame([data])
            else:
                msg = f"Unsupported JSON structure in {file_path}"
                raise ValueError(msg)
        else:
            msg = f"Unsupported file format: {file_path}"
            raise ValueError(msg)
        if not model_name:
            model_name = (
                f"AutoModel_{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
        return self.generate_model_from_dataframe(df, model_name)

    def export_model_code(self, model_name: str) -> str:
        """Export the model as Python code."""
        schema = self.registry.get_schema(model_name)
        if not schema:
            msg = f"Model {model_name} not found"
            raise ValueError(msg)

        # Generate Python code
        code_lines = [
            "from datetime import datetime",
            "from typing import Optional",
            "from pydantic import BaseModel, Field\n",
            f"class {model_name}(BaseModel):",
            '    """Auto-generated model"""',
        ]

        for field_name, field_info in schema["fields"].items():
            python_type = field_info["python_type"]
            description = field_info["constraints"].get("description", "")
            constraints = {
                k: v for k, v in field_info["constraints"].items() if k != "description"
            }

            if constraints:
                constraints_str = ", ".join(
                    f"{k}={v!r}" for k, v in constraints.items()
                )
                code_lines.append(
                    f'    {field_name}: {python_type} = Field({constraints_str}, description="{description}")'
                )
            else:
                code_lines.append(
                    f'    {field_name}: {python_type} = Field(description="{description}")'
                )

        # Add metadata fields
        code_lines.extend(
            [
                "",
                "    # Metadata fields",
                '    record_id: Optional[str] = Field(None, description="Auto-generated record ID")',
                '    source_file: Optional[str] = Field(None, description="Source filename")',
                '    ingested_at: datetime = Field(default_factory=datetime.utcnow, description="Ingestion timestamp")',
                f'    domain: str = Field(default="{schema["domain"]}", description="Data domain")',
                '    schema_version: str = Field(default="1.0", description="Schema version")',
            ]
        )

        return "\n".join(code_lines)


# Global instance
auto_model_generator = AutoModelGenerator()


class AutoRecord(BaseModel):
    """Base class for auto-generated records."""

    record_id: str | None = Field(None, description="Auto-generated record ID")
    source_file: str | None = Field(None, description="Source filename")
    ingested_at: datetime = Field(
        default_factory=datetime.utcnow, description="Ingestion timestamp"
    )
    domain: str = Field(default="auto", description="Data domain")
    schema_version: str = Field(default="1.0", description="Schema version")
    raw_data: dict[str, Any] | None = Field(None, description="Original raw data")

    class Config:
        extra = "allow"  # Allow extra fields
        schema_extra = {"description": "Base class for auto-generated data records"}


def get_auto_model_for_file(file_path: str) -> type[BaseModel]:
    """Convenience function to get or generate a model for a file."""
    # Try to find existing model first
    import os

    base_name = os.path.splitext(os.path.basename(file_path))[0]

    # Look for existing models with this base name
    for model_name in auto_model_registry.list_models():
        if base_name in model_name:
            logger.info(f"Found existing model for {file_path}: {model_name}")
            return auto_model_registry.get_model(model_name)

    # Generate new model
    logger.info(f"Generating new model for {file_path}")
    return auto_model_generator.generate_model_from_file(file_path)


def validate_record_with_auto_model(
    data: dict[str, Any], model_name: str
) -> dict[str, Any]:
    """Validate a data record using an auto-generated model."""
    model_class = auto_model_registry.get_model(model_name)
    if not model_class:
        msg = f"Model {model_name} not found"
        raise ValueError(msg)

    try:
        # Create instance and return validated data
        instance = model_class(**data)
        return instance.dict()
    except Exception as e:
        logger.exception(f"Validation failed for model {model_name}: {e}")
        raise
