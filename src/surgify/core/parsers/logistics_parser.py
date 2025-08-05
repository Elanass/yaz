"""
Logistics Domain Parser

Handles parsing of logistics data including supply chain,
inventory management, transportation, and delivery information.
"""

from typing import Any, Dict, List
import pandas as pd
import logging
from surgify.core.parsers import BaseParser

logger = logging.getLogger(__name__)


class LogisticsParser(BaseParser):
    """Parser for logistics domain data"""
    
    def get_schema_patterns(self) -> List[str]:
        """Logistics-specific header patterns"""
        return [
            "logistics", "supply", "inventory", "shipment", "delivery",
            "warehouse", "stock", "transport", "vendor", "supplier",
            "quantity", "cost", "lead_time", "tracking", "order"
        ]
    
    def parse(self, data: Any) -> Dict[str, Any]:
        """Parse logistics data"""
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
            logger.error(f"Error parsing logistics data: {e}")
            return {"error": str(e)}
    
    def _parse_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse logistics DataFrame"""
        result = {
            "domain": "logistics",
            "data_type": "dataframe",
            "shape": df.shape,
            "columns": df.columns.tolist(),
            "summary": {}
        }
        
        # Logistics-specific analysis
        logistics_columns = self._identify_logistics_columns(df)
        
        if logistics_columns.get("supplier"):
            result["summary"]["suppliers"] = df[logistics_columns["supplier"]].value_counts().to_dict()
        
        if logistics_columns.get("quantity"):
            qty_col = logistics_columns["quantity"]
            if pd.api.types.is_numeric_dtype(df[qty_col]):
                result["summary"]["total_quantity"] = float(df[qty_col].sum())
                result["summary"]["avg_quantity"] = float(df[qty_col].mean())
        
        if logistics_columns.get("cost"):
            cost_col = logistics_columns["cost"]
            if pd.api.types.is_numeric_dtype(df[cost_col]):
                result["summary"]["total_cost"] = float(df[cost_col].sum())
                result["summary"]["avg_cost"] = float(df[cost_col].mean())
        
        if logistics_columns.get("lead_time"):
            lt_col = logistics_columns["lead_time"]
            if pd.api.types.is_numeric_dtype(df[lt_col]):
                result["summary"]["avg_lead_time"] = float(df[lt_col].mean())
        
        return result
    
    def _parse_dict(self, data: dict) -> Dict[str, Any]:
        """Parse logistics dictionary data"""
        return {
            "domain": "logistics",
            "data_type": "dictionary",
            "keys": list(data.keys()),
            "logistics_data": data,
            "summary": {
                "fields_identified": len(data),
                "has_supplier_info": any(key in data for key in ["supplier", "vendor", "provider"]),
                "has_inventory_info": any(key in data for key in ["quantity", "stock", "inventory"]),
                "has_cost_info": any(key in data for key in ["cost", "price", "amount"])
            }
        }
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse logistics text data"""
        logistics_keywords = ["logistics", "supply", "inventory", "shipment", "delivery"]
        found_keywords = [kw for kw in logistics_keywords if kw.lower() in text.lower()]
        
        return {
            "domain": "logistics",
            "data_type": "text",
            "text_length": len(text),
            "logistics_keywords_found": found_keywords,
            "likely_logistics_text": len(found_keywords) > 0
        }
    
    def _identify_logistics_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify logistics-related columns in the DataFrame"""
        columns = df.columns.tolist()
        identified = {}
        
        # Common logistics column mappings
        mappings = {
            "supplier": ["supplier", "vendor", "provider", "company"],
            "quantity": ["quantity", "qty", "amount", "count", "units"],
            "cost": ["cost", "price", "amount", "total", "value"],
            "lead_time": ["lead_time", "delivery_time", "transit_time", "duration"],
            "product": ["product", "item", "material", "goods"],
            "tracking": ["tracking", "tracking_number", "shipment_id"]
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
