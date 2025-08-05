"""
Insurance Domain Parser

Handles parsing of insurance data including claims, policies,
coverage information, and risk assessment data.
"""

from typing import Any, Dict, List
import pandas as pd
import logging
from surgify.core.parsers import BaseParser

logger = logging.getLogger(__name__)


class InsuranceParser(BaseParser):
    """Parser for insurance domain data"""
    
    def get_schema_patterns(self) -> List[str]:
        """Insurance-specific header patterns"""
        return [
            "insurance", "claim", "policy", "coverage", "premium",
            "deductible", "copay", "benefit", "risk", "underwriting",
            "member", "subscriber", "plan", "carrier", "payer"
        ]
    
    def parse(self, data: Any) -> Dict[str, Any]:
        """Parse insurance data"""
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
            logger.error(f"Error parsing insurance data: {e}")
            return {"error": str(e)}
    
    def _parse_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse insurance DataFrame"""
        result = {
            "domain": "insurance",
            "data_type": "dataframe",
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "summary": {}
        }
        
        # Insurance-specific analysis
        insurance_columns = self._identify_insurance_columns(df)
        
        if insurance_columns.get("claim_status"):
            result["summary"]["claim_statuses"] = df[insurance_columns["claim_status"]].value_counts().to_dict()
        
        if insurance_columns.get("claim_amount"):
            amount_col = insurance_columns["claim_amount"]
            if pd.api.types.is_numeric_dtype(df[amount_col]):
                result["summary"]["total_claims"] = float(df[amount_col].sum())
                result["summary"]["avg_claim_amount"] = float(df[amount_col].mean())
        
        if insurance_columns.get("premium"):
            premium_col = insurance_columns["premium"]
            if pd.api.types.is_numeric_dtype(df[premium_col]):
                result["summary"]["total_premiums"] = float(df[premium_col].sum())
                result["summary"]["avg_premium"] = float(df[premium_col].mean())
        
        if insurance_columns.get("policy_type"):
            result["summary"]["policy_types"] = df[insurance_columns["policy_type"]].value_counts().to_dict()
        
        return result
    
    def _parse_dict(self, data: dict) -> Dict[str, Any]:
        """Parse insurance dictionary data"""
        return {
            "domain": "insurance",
            "data_type": "dictionary",
            "keys": list(data.keys()),
            "insurance_data": data,
            "summary": {
                "fields_identified": len(data),
                "has_policy_info": any(key in data for key in ["policy_id", "policy_number", "plan"]),
                "has_claim_info": any(key in data for key in ["claim_id", "claim_amount", "claim_status"]),
                "has_member_info": any(key in data for key in ["member_id", "subscriber", "patient"])
            }
        }
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse insurance text data"""
        insurance_keywords = ["insurance", "claim", "policy", "coverage", "premium"]
        found_keywords = [kw for kw in insurance_keywords if kw.lower() in text.lower()]
        
        return {
            "domain": "insurance",
            "data_type": "text",
            "text_length": len(text),
            "insurance_keywords_found": found_keywords,
            "likely_insurance_text": len(found_keywords) > 0
        }
    
    def _identify_insurance_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify insurance-related columns in the DataFrame"""
        columns = df.columns.tolist()
        identified = {}
        
        # Common insurance column mappings
        mappings = {
            "claim_amount": ["claim_amount", "amount", "cost", "charge", "payment"],
            "claim_status": ["status", "claim_status", "state", "condition"],
            "premium": ["premium", "monthly_premium", "cost", "payment"],
            "policy_type": ["policy_type", "plan_type", "coverage_type", "plan"],
            "member_id": ["member_id", "subscriber_id", "patient_id", "id"],
            "deductible": ["deductible", "copay", "out_of_pocket"]
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
