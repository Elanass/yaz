"""
Specific Purpose Operators Package
Domain-specific operators for healthcare, education, hospitality, and other specialized business domains
"""

# Healthcare domain
from .healthcare_operations import HealthcareOperationsOperator
from .surgery_operations import SurgeryOperationsOperator
from .patient_management_operations import PatientManagementOperationsOperator

# Education domain  
from .education_operations import EducationOperationsOperator
# TODO: Add training_operations and certification_operations modules

# Hospitality domain
from .hospitality_operations import HospitalityOperationsOperator
# TODO: Add patient_experience_operations and accommodation_operations modules

# Insurance domain
from .insurance_operations import InsuranceOperationsOperator
# TODO: Add claims_operations and coverage_operations modules

# Logistics domain
from .logistics_operations import LogisticsOperationsOperator
# TODO: Add supply_chain_operations and transportation_operations modules

__all__ = [
    # Healthcare domain
    "HealthcareOperationsOperator",
    "SurgeryOperationsOperator", 
    "PatientManagementOperationsOperator",
    
    # Education domain
    "EducationOperationsOperator",
    
    # Hospitality domain
    "HospitalityOperationsOperator",
    
    # Insurance domain
    "InsuranceOperationsOperator",
    
    # Logistics domain
    "LogisticsOperationsOperator",
]
