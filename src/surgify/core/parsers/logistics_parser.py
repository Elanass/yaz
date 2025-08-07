"""
Logistics Domain Parser

Handles parsing of logistics data including supply chain,
inventory management, transportation, and delivery information.
"""

import logging
from typing import Any, Dict, List

import pandas as pd

from . import BaseParser

logger = logging.getLogger(__name__)


class LogisticsParser(BaseParser):
    """Parser for logistics domain data"""

    def get_schema_patterns(self) -> List[str]:
        """Logistics-specific header patterns"""
        return [
            "logistics",
            "supply",
            "inventory",
            "shipment",
            "delivery",
            "warehouse",
            "stock",
            "transport",
            "vendor",
            "supplier",
            "quantity",
            "cost",
            "lead_time",
            "tracking",
            "order",
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
            elif isinstance(data, list):
                return self._parse_image_list(data)
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
            "summary": {},
        }

        # Logistics-specific analysis
        logistics_columns = self._identify_logistics_columns(df)

        if logistics_columns.get("supplier"):
            result["summary"]["suppliers"] = (
                df[logistics_columns["supplier"]].value_counts().to_dict()
            )

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
                "has_supplier_info": any(
                    key in data for key in ["supplier", "vendor", "provider"]
                ),
                "has_inventory_info": any(
                    key in data for key in ["quantity", "stock", "inventory"]
                ),
                "has_cost_info": any(
                    key in data for key in ["cost", "price", "amount"]
                ),
            },
        }

    def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse logistics text data with enhanced supply chain context analysis"""
        logistics_keywords = [
            "logistics", "supply", "inventory", "shipment", "delivery",
            "warehouse", "procurement", "supplier", "vendor", "transport",
            "shipping", "freight", "distribution", "fulfillment", "tracking"
        ]
        
        # Enhanced keyword detection
        found_keywords = [kw for kw in logistics_keywords if kw.lower() in text.lower()]
        
        # Extract logistics-specific entities
        import re
        
        # Look for tracking numbers
        tracking_pattern = r'\b(?:tracking|track|shipment)[\s:]*([\w\d-]+)\b'
        tracking_numbers = re.findall(tracking_pattern, text, re.IGNORECASE)
        
        # Look for quantities and measurements
        quantity_pattern = r'\b\d+\s*(?:units?|pieces?|boxes?|pallets?|tons?|kg|lbs?)\b'
        quantities = re.findall(quantity_pattern, text, re.IGNORECASE)
        
        # Look for monetary values
        currency_pattern = r'\$[\d,]+\.?\d*|€[\d,]+\.?\d*|£[\d,]+\.?\d*'
        currency_values = re.findall(currency_pattern, text)
        
        # Look for dates and timelines
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'
        dates_found = re.findall(date_pattern, text)
        
        # Look for location references
        location_keywords = ['warehouse', 'depot', 'facility', 'dock', 'terminal', 'port']
        locations_found = [word for word in location_keywords if word.lower() in text.lower()]
        
        # Assess text type
        text_type = "unknown"
        if any(word in text.lower() for word in ["purchase", "order", "po"]):
            text_type = "purchase_order"
        elif any(word in text.lower() for word in ["delivery", "shipment", "tracking"]):
            text_type = "delivery_info"
        elif any(word in text.lower() for word in ["invoice", "payment", "billing"]):
            text_type = "invoice"
        elif any(word in text.lower() for word in ["inventory", "stock", "count"]):
            text_type = "inventory_report"
        elif any(word in text.lower() for word in ["quality", "inspection", "damage"]):
            text_type = "quality_report"

        return {
            "domain": "logistics",
            "data_type": "text",
            "text_length": len(text),
            "logistics_keywords_found": found_keywords,
            "likely_logistics_text": len(found_keywords) > 0,
        }
    
    def _parse_image_list(self, images: List[str]) -> Dict[str, Any]:
        """Parse logistics-related image list"""
        logistics_image_types = {
            'product': ['product', 'item', 'goods', 'material'],
            'shipment': ['shipment', 'package', 'box', 'container', 'cargo'],
            'warehouse': ['warehouse', 'storage', 'facility', 'dock'],
            'transportation': ['truck', 'vehicle', 'transport', 'delivery'],
            'damage': ['damage', 'broken', 'defect', 'problem'],
            'inspection': ['inspection', 'quality', 'check', 'review'],
            'documentation': ['label', 'barcode', 'qr', 'receipt', 'invoice']
        }
        
        categorized_images = {category: [] for category in logistics_image_types.keys()}
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.tiff', '.pdf', '.bmp'}
        valid_images = []
        
        for img_path in images:
            # Check if valid image/document extension
            if any(img_path.lower().endswith(ext) for ext in valid_extensions):
                valid_images.append(img_path)
                
                # Categorize by content
                img_lower = img_path.lower()
                for category, keywords in logistics_image_types.items():
                    if any(keyword in img_lower for keyword in keywords):
                        categorized_images[category].append(img_path)
                        break
        
        return {
            "domain": "logistics",
            "data_type": "image_list",
            "total_images": len(images),
            "valid_image_count": len(valid_images),
            "valid_images": valid_images,
            "categorized_images": categorized_images,
            "image_types_detected": [cat for cat, imgs in categorized_images.items() if imgs],
            "documentation_ratio": len([img for img in valid_images if any(keyword in img.lower() for keyword in ['pdf', 'doc', 'invoice', 'receipt'])]) / max(len(valid_images), 1)
        }
