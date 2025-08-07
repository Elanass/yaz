"""
Insurance Domain Parser

Handles parsing of insurance data including claims, policies,
coverage information, and risk assessment data.
"""

import logging
from typing import Any, Dict, List

import pandas as pd

from . import BaseParser

logger = logging.getLogger(__name__)


class InsuranceParser(BaseParser):
    """Parser for insurance domain data"""

    def get_schema_patterns(self) -> List[str]:
        """Insurance-specific header patterns"""
        return [
            "insurance",
            "claim",
            "policy",
            "coverage",
            "premium",
            "deductible",
            "copay",
            "benefit",
            "risk",
            "underwriting",
            "member",
            "subscriber",
            "plan",
            "carrier",
            "payer",
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
            elif isinstance(data, list):
                return self._parse_image_list(data)
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
            "summary": {},
        }

        # Insurance-specific analysis
        insurance_columns = self._identify_insurance_columns(df)

        if insurance_columns.get("claim_status"):
            result["summary"]["claim_statuses"] = (
                df[insurance_columns["claim_status"]].value_counts().to_dict()
            )

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
            result["summary"]["policy_types"] = (
                df[insurance_columns["policy_type"]].value_counts().to_dict()
            )

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
                "has_policy_info": any(
                    key in data for key in ["policy_id", "policy_number", "plan"]
                ),
                "has_claim_info": any(
                    key in data for key in ["claim_id", "claim_amount", "claim_status"]
                ),
                "has_member_info": any(
                    key in data for key in ["member_id", "subscriber", "patient"]
                ),
            },
        }

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse insurance text data with enhanced claims and policy context analysis"""
        insurance_keywords = [
            "insurance", "claim", "policy", "coverage", "premium", "deductible",
            "copay", "benefit", "risk", "underwriting", "member", "subscriber",
            "plan", "carrier", "payer", "adjuster", "settlement", "liability"
        ]
        
        # Enhanced keyword detection
        found_keywords = [kw for kw in insurance_keywords if kw.lower() in text.lower()]
        
        # Extract insurance-specific entities
        import re
        
        # Look for policy numbers
        policy_pattern = r'\b(?:policy|pol)[\s#:]*([A-Z0-9-]+)\b'
        policy_numbers = re.findall(policy_pattern, text, re.IGNORECASE)
        
        # Look for claim numbers
        claim_pattern = r'\b(?:claim|clm)[\s#:]*([A-Z0-9-]+)\b'
        claim_numbers = re.findall(claim_pattern, text, re.IGNORECASE)
        
        # Look for monetary amounts
        currency_pattern = r'\$[\d,]+\.?\d*|€[\d,]+\.?\d*|£[\d,]+\.?\d*'
        currency_values = re.findall(currency_pattern, text)
        
        # Look for percentages (deductibles, copays, etc.)
        percentage_pattern = r'\b\d+\.?\d*%'
        percentages = re.findall(percentage_pattern, text)
        
        # Look for dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
        dates_found = re.findall(date_pattern, text)
        
        # Look for medical codes (ICD, CPT)
        medical_code_pattern = r'\b(?:ICD|CPT)[-\s]*\d+\.?\d*[A-Z]?\b|\b[A-Z]\d{2}\.\d{1,2}\b'
        medical_codes = re.findall(medical_code_pattern, text, re.IGNORECASE)
        
        # Assess text type
        text_type = "unknown"
        if any(word in text.lower() for word in ["claim", "settlement", "adjustment"]):
            text_type = "claim_document"
        elif any(word in text.lower() for word in ["policy", "coverage", "terms"]):
            text_type = "policy_document"
        elif any(word in text.lower() for word in ["medical", "diagnosis", "treatment"]):
            text_type = "medical_report"
        elif any(word in text.lower() for word in ["investigation", "fraud", "suspicious"]):
            text_type = "investigation_report"
        elif any(word in text.lower() for word in ["denial", "approve", "decision"]):
            text_type = "decision_document"

        return {
            "domain": "insurance",
            "data_type": "text",
            "text_length": len(text),
            "insurance_keywords_found": found_keywords,
            "likely_insurance_text": len(found_keywords) > 0,
        }
    
    def _parse_image_list(self, images: List[str]) -> Dict[str, Any]:
        """Parse insurance-related image list"""
        insurance_image_types = {
            'incident': ['incident', 'accident', 'crash', 'collision'],
            'damage': ['damage', 'broken', 'destroyed', 'loss'],
            'medical': ['medical', 'xray', 'mri', 'ct', 'scan', 'diagnosis'],
            'property': ['property', 'building', 'home', 'vehicle', 'car'],
            'evidence': ['evidence', 'proof', 'documentation', 'witness'],
            'policy': ['policy', 'contract', 'agreement', 'terms'],
            'claim_form': ['claim', 'form', 'application', 'submission'],
            'appraisal': ['appraisal', 'assessment', 'evaluation', 'estimate']
        }
        
        categorized_images = {category: [] for category in insurance_image_types.keys()}
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.tiff', '.pdf', '.doc', '.docx'}
        valid_images = []
        
        for img_path in images:
            # Check if valid image/document extension
            if any(img_path.lower().endswith(ext) for ext in valid_extensions):
                valid_images.append(img_path)
                
                # Categorize by content
                img_lower = img_path.lower()
                for category, keywords in insurance_image_types.items():
                    if any(keyword in img_lower for keyword in keywords):
                        categorized_images[category].append(img_path)
                        break
        
        return {
            "domain": "insurance",
            "data_type": "image_list",
            "total_images": len(images),
            "valid_image_count": len(valid_images),
            "valid_images": valid_images,
            "categorized_images": categorized_images,
            "image_types_detected": [cat for cat, imgs in categorized_images.items() if imgs],
            "document_ratio": len([img for img in valid_images if any(keyword in img.lower() for keyword in ['pdf', 'doc', 'form', 'policy'])]) / max(len(valid_images), 1),
            "medical_image_ratio": len([img for img in valid_images if any(keyword in img.lower() for keyword in ['medical', 'xray', 'mri', 'ct', 'scan'])]) / max(len(valid_images), 1)
        }
