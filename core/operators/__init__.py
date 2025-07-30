"""
Operators Package
Reorganized into general-purpose and specific-purpose operators for better modularity
"""

# General Purpose Operators (cross-domain functionality)
from .general_purpose.core_operations import CoreOperationsOperator
from .general_purpose.financial_operations import FinancialOperationsOperator
from .general_purpose.communication_operations import CommunicationOperationsOperator
from .general_purpose.infrastructure_operations import InfrastructureOperationsOperator
from .general_purpose.security_operations import SecurityOperationsOperator
from .general_purpose.monitoring_operations import MonitoringOperationsOperator
from .general_purpose.integration_operations import IntegrationOperationsOperator
from .general_purpose.data_sync_operations import DataSyncOperationsOperator

# Specific Purpose Operators (domain-specific functionality)
from .specific_purpose.healthcare_operations import HealthcareOperationsOperator
from .specific_purpose.surgery_operations import SurgeryOperationsOperator
from .specific_purpose.education_operations import EducationOperationsOperator
from .specific_purpose.hospitality_operations import HospitalityOperationsOperator
from .specific_purpose.insurance_operations import InsuranceOperationsOperator
from .specific_purpose.logistics_operations import LogisticsOperationsOperator

__all__ = [
    # General Purpose Operators
    "CoreOperationsOperator",
    "FinancialOperationsOperator",
    "CommunicationOperationsOperator", 
    "InfrastructureOperationsOperator",
    "SecurityOperationsOperator",
    "MonitoringOperationsOperator",
    "IntegrationOperationsOperator",
    "DataSyncOperationsOperator",
    
    # Specific Purpose Operators
    "HealthcareOperationsOperator",
    "SurgeryOperationsOperator",
    "EducationOperationsOperator",
    "HospitalityOperationsOperator",
    "InsuranceOperationsOperator",
    "LogisticsOperationsOperator"
]
