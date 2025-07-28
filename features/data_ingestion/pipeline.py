"""
Data Ingestion Pipeline
Handles data ingestion from multiple sources and formats
"""

import os
import csv
import json
import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

from core.utils.helpers import load_csv, log_action, handle_error

logger = logging.getLogger(__name__)

class DataProcessor(ABC):
    """Abstract base class for data processors"""
    
    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Validate input data"""
        pass
    
    @abstractmethod
    def process(self, data: Any) -> Dict[str, Any]:
        """Process input data"""
        pass

class CSVProcessor(DataProcessor):
    """CSV data processor"""
    
    def validate(self, file_path: str) -> bool:
        """Validate CSV file"""
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                header = next(reader)
                # Validate header has required fields
                required_fields = ['id', 'age', 'gender', 'stage']
                for field in required_fields:
                    if field not in header:
                        logger.error(f"Missing required field: {field}")
                        return False
            return True
        except Exception as e:
            logger.error(f"CSV validation error: {e}")
            return False
    
    def process(self, file_path: str) -> List[Dict[str, Any]]:
        """Process CSV file"""
        try:
            data = load_csv(file_path)
            # Normalize field names
            normalized_data = []
            for row in data:
                normalized_row = {}
                for key, value in row.items():
                    normalized_key = key.lower().strip().replace(' ', '_')
                    normalized_row[normalized_key] = value
                normalized_data.append(normalized_row)
            return normalized_data
        except Exception as e:
            logger.error(f"CSV processing error: {e}")
            raise

class HL7Processor(DataProcessor):
    """HL7 data processor"""
    
    def validate(self, hl7_message: str) -> bool:
        """Validate HL7 message"""
        # Basic validation - check for MSH segment
        if not hl7_message.startswith('MSH|'):
            logger.error("Invalid HL7 message: Missing MSH segment")
            return False
        return True
    
    def process(self, hl7_message: str) -> Dict[str, Any]:
        """Process HL7 message"""
        # Simple HL7 parsing
        segments = hl7_message.split('\n')
        result = {}
        
        for segment in segments:
            fields = segment.split('|')
            segment_type = fields[0]
            
            if segment_type == 'PID':
                # Patient Identification
                if len(fields) > 5:
                    result['id'] = fields[3]
                if len(fields) > 8:
                    gender = fields[8]
                    result['gender'] = 'male' if gender == 'M' else 'female' if gender == 'F' else 'other'
                    
            elif segment_type == 'OBX':
                # Observation Result
                if len(fields) > 5:
                    observation_id = fields[3]
                    value = fields[5]
                    result[f'observation_{observation_id}'] = value
        
        return result

class DICOMProcessor(DataProcessor):
    """DICOM data processor"""
    
    def validate(self, dicom_data: bytes) -> bool:
        """Validate DICOM data"""
        # Check for DICOM magic number
        if not dicom_data[:4] == b'DICM':
            logger.error("Invalid DICOM data: Missing DICM magic number")
            return False
        return True
    
    def process(self, dicom_data: bytes) -> Dict[str, Any]:
        """Process DICOM data"""
        # Simplified DICOM processing
        # In a real implementation, use pydicom or similar library
        result = {
            'id': 'dicom_patient',
            'type': 'imaging',
            'size': len(dicom_data),
            'format': 'dicom'
        }
        return result

class APIProcessor(DataProcessor):
    """API data processor"""
    
    def validate(self, api_data: Dict[str, Any]) -> bool:
        """Validate API data"""
        required_fields = ['patient_id', 'clinical_data']
        for field in required_fields:
            if field not in api_data:
                logger.error(f"Missing required field in API data: {field}")
                return False
        return True
    
    def process(self, api_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process API data"""
        # Extract and normalize API data
        result = {
            'id': api_data.get('patient_id'),
            'data_source': 'api',
            'timestamp': api_data.get('timestamp')
        }
        
        # Merge clinical data
        clinical_data = api_data.get('clinical_data', {})
        for key, value in clinical_data.items():
            normalized_key = key.lower().replace(' ', '_')
            result[normalized_key] = value
            
        return result

class MultiCenterDataPipeline:
    """Main data ingestion pipeline for multi-center data"""
    
    def __init__(self):
        self.processors = {
            'csv': CSVProcessor(),
            'hl7': HL7Processor(),
            'dicom': DICOMProcessor(),
            'api': APIProcessor()
        }
    
    def detect_format(self, data: Any) -> str:
        """Detect data format"""
        if isinstance(data, str):
            if os.path.exists(data) and data.endswith('.csv'):
                return 'csv'
            elif data.startswith('MSH|'):
                return 'hl7'
        elif isinstance(data, bytes) and data[:4] == b'DICM':
            return 'dicom'
        elif isinstance(data, dict) and 'patient_id' in data:
            return 'api'
        
        raise ValueError(f"Unknown data format: {type(data)}")
    
    def ingest(self, data: Any, center_id: str, user_id: str) -> Dict[str, Any]:
        """Ingest data from any source"""
        try:
            # Detect format
            format_type = self.detect_format(data)
            logger.info(f"Detected format: {format_type} from center: {center_id}")
            
            # Get appropriate processor
            processor = self.processors.get(format_type)
            if not processor:
                raise ValueError(f"No processor available for format: {format_type}")
            
            # Validate
            if not processor.validate(data):
                raise ValueError(f"Data validation failed for format: {format_type}")
            
            # Process
            processed_data = processor.process(data)
            
            # Add metadata
            if isinstance(processed_data, list):
                for item in processed_data:
                    item['center_id'] = center_id
                    item['ingestion_timestamp'] = str(datetime.now())
            else:
                processed_data['center_id'] = center_id
                processed_data['ingestion_timestamp'] = str(datetime.now())
            
            # Log action
            log_action(user_id, "data_ingestion", {
                "center_id": center_id,
                "format": format_type,
                "record_count": len(processed_data) if isinstance(processed_data, list) else 1
            })
            
            return {
                "success": True,
                "format": format_type,
                "data": processed_data
            }
            
        except Exception as e:
            logger.error(f"Data ingestion error: {e}")
            return handle_error(e)
