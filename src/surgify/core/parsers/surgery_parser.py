"""
Surgery Domain Parser

Handles parsing of surgical case data, patient information,
procedures, and surgical outcomes.
"""

import logging
from typing import Any, Dict, List

import pandas as pd

from surgify.core.parsers import BaseParser

logger = logging.getLogger(__name__)


class SurgeryParser(BaseParser):
    """Parser for surgical domain data"""

    def get_schema_patterns(self) -> List[str]:
        """Surgery-specific header patterns"""
        return [
            "surgery",
            "surgical",
            "procedure",
            "operation",
            "patient",
            "diagnosis",
            "surgeon",
            "anesthesia",
            "case",
            "outcome",
            "preop",
            "postop",
            "complication",
            "asa_score",
            "los",
        ]

    def parse(self, data: Any) -> Dict[str, Any]:
        """Parse surgical data"""
        try:
            if isinstance(data, pd.DataFrame):
                return self._parse_dataframe(data)
            elif isinstance(data, dict):
                return self._parse_dict(data)
            elif isinstance(data, str):
                return self._parse_text(data)
            else:
                return {"error": f"Unsupported data type: {type(data)}"}
        except Exception as e:
            logger.error(f"Error parsing surgery data: {e}")
            return {"error": str(e)}

    def _parse_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse surgical DataFrame"""
        result = {
            "domain": "surgery",
            "data_type": "dataframe",
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "summary": {},
        }

        # Surgery-specific analysis
        surgery_columns = self._identify_surgery_columns(df)

        if surgery_columns.get("procedure"):
            result["summary"]["procedures"] = (
                df[surgery_columns["procedure"]].value_counts().to_dict()
            )

        if surgery_columns.get("outcome"):
            result["summary"]["outcomes"] = (
                df[surgery_columns["outcome"]].value_counts().to_dict()
            )

        if surgery_columns.get("los"):  # Length of stay
            los_col = surgery_columns["los"]
            if pd.api.types.is_numeric_dtype(df[los_col]):
                result["summary"]["avg_length_of_stay"] = float(df[los_col].mean())

        if surgery_columns.get("asa_score"):
            result["summary"]["asa_distribution"] = (
                df[surgery_columns["asa_score"]].value_counts().to_dict()
            )

        return result

    def _parse_dict(self, data: dict) -> Dict[str, Any]:
        """Parse surgical dictionary data"""
        return {
            "domain": "surgery",
            "data_type": "dictionary",
            "keys": list(data.keys()),
            "case_data": data,
            "summary": {
                "fields_identified": len(data),
                "has_patient_info": any(
                    key in data for key in ["patient_id", "patient_name", "mrn"]
                ),
                "has_procedure_info": any(
                    key in data for key in ["procedure", "surgery_type", "operation"]
                ),
                "has_outcome_info": any(
                    key in data for key in ["outcome", "result", "status"]
                ),
            },
        }

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse surgical text data"""
        surgical_keywords = [
            "surgery",
            "operation",
            "procedure",
            "patient",
            "diagnosis",
        ]
        found_keywords = [kw for kw in surgical_keywords if kw.lower() in text.lower()]

        return {
            "domain": "surgery",
            "data_type": "text",
            "text_length": len(text),
            "surgical_keywords_found": found_keywords,
            "likely_surgical_text": len(found_keywords) > 0,
        }

    def _identify_surgery_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify surgery-related columns in the DataFrame"""
        columns = df.columns.tolist()
        identified = {}

        # Common surgical column mappings
        mappings = {
            "procedure": ["procedure", "surgery", "operation", "surgery_type"],
            "outcome": ["outcome", "result", "status", "complication"],
            "los": ["los", "length_of_stay", "stay_duration", "days"],
            "asa_score": ["asa", "asa_score", "risk_score"],
            "diagnosis": ["diagnosis", "condition", "indication"],
            "surgeon": ["surgeon", "primary_surgeon", "attending"],
        }

        for field, patterns in mappings.items():
            for col in columns:
                for pattern in patterns:
                    if pattern.lower() in col.lower():
                        identified[field] = col
                        break
                if field in identified:
                    break

        return identified
