"""
Shared Medical Utilities - DRY Implementation
Common functions used across all medical modules
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
import logging
import hashlib
from decimal import Decimal

from core.config.platform_config import config
from core.services.encryption import encryption_service


class MedicalValidation:
    """Centralized medical data validation"""
    
    @staticmethod
    def validate_patient_data(data: Dict[str, Any]) -> List[str]:
        """Validate patient data according to medical standards"""
        errors = []
        
        # Required fields
        required_fields = ['age', 'gender']
        for field in required_fields:
            if not data.get(field):
                errors.append(f"{field} is required")
        
        # Age validation
        age = data.get('age')
        if age and (not isinstance(age, (int, float)) or age < 0 or age > 120):
            errors.append("Age must be between 0 and 120")
        
        # Gender validation
        gender = data.get('gender')
        if gender and gender.lower() not in ['male', 'female', 'other']:
            errors.append("Gender must be 'male', 'female', or 'other'")
        
        return errors
    
    @staticmethod
    def validate_clinical_data(data: Dict[str, Any]) -> List[str]:
        """Validate clinical data"""
        errors = []
        
        # Tumor stage validation
        stage = data.get('tumor_stage')
        if stage:
            valid_stages = ['T1', 'T2', 'T3', 'T4', 'Tx']
            if not any(stage.startswith(s) for s in valid_stages):
                errors.append("Invalid tumor stage format")
        
        # Performance status validation
        ecog = data.get('ecog_performance_status')
        if ecog is not None and ecog not in [0, 1, 2, 3, 4]:
            errors.append("ECOG performance status must be 0-4")
        
        return errors
    
    @staticmethod
    def validate_surgery_data(data: Dict[str, Any]) -> List[str]:
        """Validate surgery-specific data"""
        errors = []
        
        # Procedure validation
        procedure = data.get('procedure_type')
        valid_procedures = [
            'total_gastrectomy', 'subtotal_gastrectomy', 
            'proximal_gastrectomy', 'distal_gastrectomy'
        ]
        if procedure and procedure not in valid_procedures:
            errors.append(f"Invalid procedure type: {procedure}")
        
        return errors


class MedicalCalculations:
    """Centralized medical calculations"""
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_m: float) -> float:
        """Calculate Body Mass Index"""
        if height_m <= 0:
            raise ValueError("Height must be greater than 0")
        return round(weight_kg / (height_m ** 2), 1)
    
    @staticmethod
    def calculate_bsa(weight_kg: float, height_cm: float) -> float:
        """Calculate Body Surface Area using Mosteller formula"""
        return round(((weight_kg * height_cm) / 3600) ** 0.5, 2)
    
    @staticmethod
    def calculate_creatinine_clearance(
        serum_creatinine: float, 
        age: int, 
        weight_kg: float, 
        gender: str
    ) -> float:
        """Calculate creatinine clearance using Cockcroft-Gault equation"""
        
        clearance = ((140 - age) * weight_kg) / (72 * serum_creatinine)
        
        if gender.lower() == 'female':
            clearance *= 0.85
        
        return round(clearance, 1)
    
    @staticmethod
    def calculate_risk_score(factors: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate composite risk score"""
        
        score = 0
        risk_factors = []
        
        # Age factor
        age = factors.get('age', 0)
        if age > 75:
            score += 2
            risk_factors.append('Advanced age')
        elif age > 65:
            score += 1
            risk_factors.append('Elderly')
        
        # BMI factor
        bmi = factors.get('bmi', 0)
        if bmi > 30:
            score += 1
            risk_factors.append('Obesity')
        elif bmi < 18.5:
            score += 1
            risk_factors.append('Underweight')
        
        # Comorbidities
        comorbidities = factors.get('comorbidities', [])
        score += len(comorbidities)
        risk_factors.extend(comorbidities)
        
        # Performance status
        ecog = factors.get('ecog_performance_status', 0)
        if ecog >= 2:
            score += 2
            risk_factors.append('Poor performance status')
        
        return {
            'score': score,
            'risk_level': 'high' if score >= 5 else 'medium' if score >= 3 else 'low',
            'risk_factors': risk_factors
        }


class MedicalFormatting:
    """Centralized medical data formatting"""
    
    @staticmethod
    def format_confidence_score(score: float) -> str:
        """Format confidence score with appropriate styling"""
        percentage = score * 100
        if percentage >= 85:
            return f"<span class='text-green-600 font-bold'>{percentage:.1f}%</span>"
        elif percentage >= 65:
            return f"<span class='text-yellow-600 font-bold'>{percentage:.1f}%</span>"
        else:
            return f"<span class='text-red-600 font-bold'>{percentage:.1f}%</span>"
    
    @staticmethod
    def format_risk_level(risk_level: str) -> str:
        """Format risk level with appropriate styling"""
        colors = {
            'low': 'text-green-600',
            'medium': 'text-yellow-600', 
            'high': 'text-red-600'
        }
        color = colors.get(risk_level.lower(), 'text-gray-600')
        return f"<span class='{color} font-semibold'>{risk_level.title()}</span>"
    
    @staticmethod
    def format_tumor_stage(stage: str) -> str:
        """Format tumor stage consistently"""
        return stage.upper() if stage else 'Unknown'
    
    @staticmethod
    def format_medical_date(date: datetime) -> str:
        """Format date for medical records"""
        return date.strftime('%Y-%m-%d %H:%M') if date else 'Not recorded'


class MedicalSecurity:
    """Centralized medical data security"""
    
    @staticmethod
    def anonymize_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize patient data for research/reporting"""
        
        # Create anonymized copy
        anonymized = data.copy()
        
        # Remove direct identifiers
        sensitive_fields = [
            'name', 'first_name', 'last_name', 'ssn', 
            'medical_record_number', 'email', 'phone'
        ]
        
        for field in sensitive_fields:
            if field in anonymized:
                del anonymized[field]
        
        # Generate consistent anonymous ID
        patient_id = data.get('id', str(datetime.utcnow().timestamp()))
        anonymized['anonymous_id'] = hashlib.sha256(
            f"{patient_id}_{config.secret_key}".encode()
        ).hexdigest()[:12]
        
        # Generalize age to ranges for additional privacy
        age = anonymized.get('age')
        if age:
            if age < 18:
                anonymized['age_group'] = 'pediatric'
            elif age < 65:
                anonymized['age_group'] = 'adult'
            else:
                anonymized['age_group'] = 'elderly'
            del anonymized['age']
        
        return anonymized
    
    @staticmethod
    def encrypt_sensitive_fields(
        data: Dict[str, Any], 
        sensitive_fields: List[str]
    ) -> Dict[str, Any]:
        """Encrypt sensitive fields in medical data"""
        
        encrypted_data = data.copy()
        
        for field in sensitive_fields:
            if field in data and data[field]:
                encrypted_data[f'encrypted_{field}'] = encryption_service.encrypt_data(
                    str(data[field])
                )
                del encrypted_data[field]
        
        return encrypted_data
    
    @staticmethod
    def create_audit_entry(
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized audit log entry"""
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'user_id': user_id,
            'details': details or {},
            'ip_address': '0.0.0.0',  # Would be filled by middleware
            'session_id': 'session_placeholder'  # Would be filled by middleware
        }


class MedicalConstants:
    """Medical constants and reference values"""
    
    # Tumor staging
    TNM_T_STAGES = ['Tx', 'T0', 'Tis', 'T1', 'T1a', 'T1b', 'T2', 'T3', 'T4', 'T4a', 'T4b']
    TNM_N_STAGES = ['Nx', 'N0', 'N1', 'N2', 'N3', 'N3a', 'N3b']
    TNM_M_STAGES = ['M0', 'M1']
    
    # Performance status
    ECOG_DESCRIPTIONS = {
        0: "Fully active",
        1: "Restricted but ambulatory", 
        2: "Ambulatory but unable to work",
        3: "Limited self-care",
        4: "Completely disabled"
    }
    
    # ASA Classification
    ASA_CLASSIFICATIONS = {
        1: "Normal healthy patient",
        2: "Patient with mild systemic disease",
        3: "Patient with severe systemic disease", 
        4: "Patient with severe systemic disease that is a constant threat to life",
        5: "Moribund patient who is not expected to survive without the operation"
    }
    
    # Normal lab ranges (example values)
    LAB_RANGES = {
        'hemoglobin': {'male': (13.8, 17.2), 'female': (12.1, 15.1)},  # g/dL
        'hematocrit': {'male': (40.7, 50.3), 'female': (36.1, 44.3)},  # %
        'creatinine': {'male': (0.7, 1.3), 'female': (0.6, 1.1)},      # mg/dL
        'albumin': (3.5, 5.0),  # g/dL
        'total_protein': (6.3, 8.2)  # g/dL
    }


class MedicalReportGenerator:
    """Generate standardized medical reports"""
    
    @staticmethod
    def generate_patient_summary(patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate patient summary report"""
        
        return {
            'patient_id': patient_data.get('id'),
            'demographics': {
                'age': patient_data.get('age'),
                'gender': patient_data.get('gender'),
                'bmi': MedicalCalculations.calculate_bmi(
                    patient_data.get('weight_kg', 70),
                    patient_data.get('height_m', 1.7)
                ) if patient_data.get('weight_kg') and patient_data.get('height_m') else None
            },
            'risk_assessment': MedicalCalculations.calculate_risk_score(patient_data),
            'generated_at': datetime.utcnow().isoformat(),
            'summary_type': 'patient_overview'
        }
    
    @staticmethod
    def generate_decision_report(decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate decision support report"""
        
        return {
            'decision_id': decision_data.get('decision_id'),
            'recommendation': decision_data.get('consolidated_recommendation'),
            'confidence_score': decision_data.get('confidence_score'),
            'evidence_quality': 'high',  # Would be calculated
            'guideline_compliance': 'compliant',  # Would be verified
            'generated_at': datetime.utcnow().isoformat(),
            'report_type': 'clinical_decision'
        }


# Convenience functions for common operations
def validate_all_medical_data(data: Dict[str, Any]) -> List[str]:
    """Validate all types of medical data"""
    errors = []
    errors.extend(MedicalValidation.validate_patient_data(data))
    errors.extend(MedicalValidation.validate_clinical_data(data))
    errors.extend(MedicalValidation.validate_surgery_data(data))
    return errors


def create_secure_medical_record(data: Dict[str, Any]) -> Dict[str, Any]:
    """Create secure medical record with encryption and audit"""
    
    # Validate data
    errors = validate_all_medical_data(data)
    if errors:
        raise ValueError(f"Validation errors: {', '.join(errors)}")
    
    # Encrypt sensitive fields
    sensitive_fields = ['ssn', 'medical_record_number', 'notes', 'address']
    secure_data = MedicalSecurity.encrypt_sensitive_fields(data, sensitive_fields)
    
    # Add metadata
    secure_data.update({
        'created_at': datetime.utcnow().isoformat(),
        'data_version': '1.0',
        'compliance_flags': ['HIPAA', 'GDPR'],
        'encryption_status': 'encrypted'
    })
    
    return secure_data
