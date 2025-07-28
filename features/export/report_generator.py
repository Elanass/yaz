"""
Report Generator
Generates reports in various formats (CSV, JSON, PDF)
"""

import csv
import json
import logging
import os
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime

from core.utils.helpers import log_action, handle_error

logger = logging.getLogger(__name__)

class IntelligentReportGenerator:
    """
    Intelligent Report Generator for creating reports in various formats
    """
    
    def __init__(self, output_dir: str = "reports"):
        """Initialize the report generator"""
        logger.info("Initializing Intelligent Report Generator")
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Supported formats
        self.formats = ["csv", "json", "pdf"]
    
    def _flatten_data(self, data: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionary for CSV export"""
        flattened = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively flatten nested dictionaries
                nested = self._flatten_data(value, prefix=f"{prefix}{key}_")
                flattened.update(nested)
            elif isinstance(value, list):
                # Convert lists to comma-separated values
                if all(not isinstance(item, (dict, list)) for item in value):
                    flattened[f"{prefix}{key}"] = ",".join(str(item) for item in value)
                else:
                    # For lists of dictionaries, add index to key
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            nested = self._flatten_data(item, prefix=f"{prefix}{key}_{i}_")
                            flattened.update(nested)
            else:
                flattened[f"{prefix}{key}"] = value
        
        return flattened
    
    def _export_csv(self, data: List[Dict[str, Any]], file_path: str) -> str:
        """Export data to CSV file"""
        try:
            if not data:
                raise ValueError("No data to export")
            
            # Flatten each record
            flattened_data = [self._flatten_data(record) for record in data]
            
            # Get all unique keys
            all_keys = set()
            for record in flattened_data:
                all_keys.update(record.keys())
            
            # Sort keys for consistent column order
            sorted_keys = sorted(all_keys)
            
            # Write CSV file
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=sorted_keys)
                writer.writeheader()
                writer.writerows(flattened_data)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def _export_json(self, data: Any, file_path: str) -> str:
        """Export data to JSON file"""
        try:
            with open(file_path, "w", encoding="utf-8") as jsonfile:
                json.dump(data, jsonfile, indent=2)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
    
    def _export_pdf(self, data: Any, file_path: str) -> str:
        """Export data to PDF file"""
        try:
            # Note: In a real implementation, use a PDF library like ReportLab or WeasyPrint
            logger.warning("PDF export is not fully implemented. Creating a placeholder file.")
            
            # Create a placeholder file with JSON content
            with open(file_path, "w", encoding="utf-8") as pdffile:
                pdffile.write("PDF PLACEHOLDER\n\n")
                pdffile.write(json.dumps(data, indent=2))
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting to PDF: {e}")
            raise
    
    def generate_report(self, data: Any, params: Dict[str, Any], user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a report in the specified format
        
        Args:
            data: Data to include in the report
            params: Report parameters including format and filters
            user_id: User ID for audit logging
            
        Returns:
            Dictionary containing report details
        """
        try:
            # Extract parameters
            report_format = params.get("format", "json").lower()
            report_title = params.get("title", "Generated Report")
            filters = params.get("filters", {})
            
            # Validate format
            if report_format not in self.formats:
                raise ValueError(f"Unsupported format: {report_format}. Supported formats: {self.formats}")
            
            # Apply filters if data is a list of dictionaries
            filtered_data = data
            if isinstance(data, list) and filters:
                filtered_data = []
                for item in data:
                    include = True
                    for key, value in filters.items():
                        if key in item and item[key] != value:
                            include = False
                            break
                    if include:
                        filtered_data.append(item)
            
            # Generate report ID and file path
            report_id = str(uuid.uuid4())
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"{timestamp}_{report_id}.{report_format}"
            file_path = os.path.join(self.output_dir, file_name)
            
            # Generate report based on format
            if report_format == "csv":
                if not isinstance(filtered_data, list):
                    filtered_data = [filtered_data]
                output_path = self._export_csv(filtered_data, file_path)
            elif report_format == "json":
                output_path = self._export_json(filtered_data, file_path)
            elif report_format == "pdf":
                output_path = self._export_pdf(filtered_data, file_path)
            
            # Log action if user ID provided
            if user_id:
                log_action(user_id, "generate_report", {
                    "report_id": report_id,
                    "format": report_format,
                    "title": report_title
                })
            
            return {
                "success": True,
                "report": {
                    "id": report_id,
                    "title": report_title,
                    "format": report_format,
                    "timestamp": str(datetime.now()),
                    "file_path": output_path,
                    "record_count": len(filtered_data) if isinstance(filtered_data, list) else 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return handle_error(e)
