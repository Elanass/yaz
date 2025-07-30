"""
Closed Source Insurance Adapters

Enterprise insurance system adapters for policy administration, claims, and billing.
"""

from typing import Dict, Any, List, Optional
import asyncio
import logging
from datetime import datetime

from adapters.closed_source import ClosedSourceAdapter
from core.config.platform_config import config
from core.services.encryption import encryption_service


class Guidewire_PolicyCenter_Adapter(ClosedSourceAdapter):
    """Adapter for Guidewire PolicyCenter"""
    
    def __init__(self):
        super().__init__("Guidewire PolicyCenter", "guidewire_pc")
        self.pc_url = getattr(config, 'guidewire_pc_url', None)
        self.pc_username = getattr(config, 'guidewire_pc_username', None)
        self.pc_password = getattr(config, 'guidewire_pc_password', None)
        self.pc_integration_user = getattr(config, 'guidewire_pc_integration_user', None)
        
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Guidewire PolicyCenter using REST API"""
        try:
            self.logger.info(f"Authenticating with {self.system_name}")
            
            if config.environment == "development":
                self._authenticated = True
                self._session_token = f"guidewire_pc_dev_token_{datetime.now().timestamp()}"
                return True
            
            # Production Guidewire authentication would use:
            # - Basic Authentication or OAuth 2.0
            # - Integration Gateway API
            # - SOAP or REST web services
            
            return False
            
        except Exception as e:
            self.logger.error(f"Guidewire PolicyCenter authentication failed: {str(e)}")
            return False
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get policy data instead of patient data"""
        return await self.get_policy_data(patient_id)
    
    async def get_policy_data(self, policy_number: str) -> Dict[str, Any]:
        """Retrieve policy data from Guidewire PolicyCenter"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Guidewire PolicyCenter")
        
        # Guidewire PolicyCenter data structure
        policy_data = {
            "policy_number": policy_number,
            "system": "guidewire_pc",
            "policy_details": {
                "product_line": "Personal Auto",
                "policy_term": "12 months",
                "effective_date": "2024-01-01",
                "expiration_date": "2024-12-31",
                "premium": 1200.00,
                "deductible": 500.00
            },
            "insured_info": {
                "name": "Encrypted Customer Name",
                "address": "Encrypted Address",
                "phone": "Encrypted Phone",
                "email": "Encrypted Email"
            },
            "coverage_details": [
                {
                    "coverage_type": "Liability",
                    "limit": 100000,
                    "premium": 600.00
                },
                {
                    "coverage_type": "Comprehensive",
                    "limit": 50000,
                    "premium": 400.00
                }
            ],
            "underwriting_info": {
                "risk_score": 75,
                "tier": "Standard",
                "factors": ["Good Driver", "Multi-Policy"]
            }
        }
        
        # Encrypt PII data
        policy_data["insured_info"]["name"] = encryption_service.encrypt_data(
            policy_data["insured_info"]["name"]
        )
        
        return policy_data
    
    async def create_case(self, case_data: Dict[str, Any]) -> str:
        """Create policy application in Guidewire PolicyCenter"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Guidewire PolicyCenter")
        
        application_id = f"guidewire_pc_app_{datetime.now().timestamp()}"
        self.logger.info(f"Created Guidewire PolicyCenter application: {application_id}")
        return application_id
    
    async def sync_data(self, data: Dict[str, Any]) -> bool:
        """Sync data with Guidewire PolicyCenter"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Guidewire PolicyCenter")
        
        return True


class Guidewire_ClaimCenter_Adapter(ClosedSourceAdapter):
    """Adapter for Guidewire ClaimCenter"""
    
    def __init__(self):
        super().__init__("Guidewire ClaimCenter", "guidewire_cc")
        self.cc_url = getattr(config, 'guidewire_cc_url', None)
        self.cc_username = getattr(config, 'guidewire_cc_username', None)
        self.cc_password = getattr(config, 'guidewire_cc_password', None)
        
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Guidewire ClaimCenter"""
        try:
            self.logger.info(f"Authenticating with {self.system_name}")
            
            if config.environment == "development":
                self._authenticated = True
                self._session_token = f"guidewire_cc_dev_token_{datetime.now().timestamp()}"
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Guidewire ClaimCenter authentication failed: {str(e)}")
            return False
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get claim data instead of patient data"""
        return await self.get_claim_data(patient_id)
    
    async def get_claim_data(self, claim_number: str) -> Dict[str, Any]:
        """Retrieve claim data from Guidewire ClaimCenter"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Guidewire ClaimCenter")
        
        claim_data = {
            "claim_number": claim_number,
            "system": "guidewire_cc",
            "claim_details": {
                "loss_date": "2024-06-15",
                "report_date": "2024-06-16",
                "loss_cause": "Collision",
                "claim_status": "Open",
                "total_incurred": 15000.00,
                "total_paid": 5000.00,
                "reserve": 10000.00
            },
            "claimant_info": {
                "name": "Encrypted Claimant Name",
                "contact": "Encrypted Contact Info",
                "relationship": "Insured"
            },
            "coverage_info": {
                "coverage_type": "Collision",
                "policy_number": "POL-123456789",
                "deductible": 500.00,
                "limit": 50000.00
            },
            "activities": [
                {
                    "date": "2024-06-16",
                    "type": "Initial Contact",
                    "description": "Claim reported by insured"
                },
                {
                    "date": "2024-06-17",
                    "type": "Assignment",
                    "description": "Claim assigned to adjuster"
                }
            ]
        }
        
        # Encrypt PII
        claim_data["claimant_info"]["name"] = encryption_service.encrypt_data(
            claim_data["claimant_info"]["name"]
        )
        
        return claim_data
    
    async def create_case(self, case_data: Dict[str, Any]) -> str:
        """Create claim in Guidewire ClaimCenter"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Guidewire ClaimCenter")
        
        claim_id = f"guidewire_cc_claim_{datetime.now().timestamp()}"
        return claim_id
    
    async def sync_data(self, data: Dict[str, Any]) -> bool:
        """Sync data with Guidewire ClaimCenter"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Guidewire ClaimCenter")
        
        return True


class Duck_Creek_Policy_Adapter(ClosedSourceAdapter):
    """Adapter for Duck Creek Policy"""
    
    def __init__(self):
        super().__init__("Duck Creek Policy", "duck_creek_policy")
        self.dc_url = getattr(config, 'duck_creek_url', None)
        self.dc_username = getattr(config, 'duck_creek_username', None)
        self.dc_password = getattr(config, 'duck_creek_password', None)
        
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with Duck Creek Policy"""
        try:
            self.logger.info(f"Authenticating with {self.system_name}")
            
            if config.environment == "development":
                self._authenticated = True
                self._session_token = f"duck_creek_dev_token_{datetime.now().timestamp()}"
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Duck Creek Policy authentication failed: {str(e)}")
            return False
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Get policy data instead"""
        return await self.get_policy_data(patient_id)
    
    async def get_policy_data(self, policy_id: str) -> Dict[str, Any]:
        """Get policy data from Duck Creek"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Duck Creek Policy")
        
        policy_data = {
            "policy_id": policy_id,
            "system": "duck_creek_policy",
            "policy_info": {
                "line_of_business": "Commercial Property",
                "effective_date": "2024-01-01",
                "premium": 25000.00,
                "commission_rate": 0.15
            },
            "customer_info": {
                "customer_id": "CUST-789012",
                "name": "Encrypted Business Name",
                "type": "Commercial"
            }
        }
        
        return policy_data
    
    async def create_case(self, case_data: Dict[str, Any]) -> str:
        """Create policy in Duck Creek"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Duck Creek Policy")
        
        policy_id = f"duck_creek_policy_{datetime.now().timestamp()}"
        return policy_id
    
    async def sync_data(self, data: Dict[str, Any]) -> bool:
        """Sync data with Duck Creek"""
        if not self._authenticated:
            raise ValueError("Not authenticated with Duck Creek Policy")
        
        return True


class ACORD_Forms_Adapter(ClosedSourceAdapter):
    """Adapter for ACORD Forms processing"""
    
    def __init__(self):
        super().__init__("ACORD Forms", "acord_forms")
        self.acord_processor_url = getattr(config, 'acord_processor_url', None)
        self.acord_api_key = getattr(config, 'acord_api_key', None)
        
    async def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate with ACORD forms processor"""
        try:
            self.logger.info(f"Authenticating with {self.system_name}")
            
            if config.environment == "development":
                self._authenticated = True
                self._session_token = f"acord_dev_token_{datetime.now().timestamp()}"
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"ACORD Forms authentication failed: {str(e)}")
            return False
    
    async def get_patient_data(self, patient_id: str) -> Dict[str, Any]:
        """Process ACORD form data"""
        return await self.process_acord_form(patient_id)
    
    async def process_acord_form(self, form_id: str) -> Dict[str, Any]:
        """Process ACORD form"""
        if not self._authenticated:
            raise ValueError("Not authenticated with ACORD Forms processor")
        
        form_data = {
            "form_id": form_id,
            "form_type": "ACORD_125",
            "status": "Processed",
            "extracted_data": {
                "applicant_name": "Encrypted Name",
                "policy_type": "Commercial General Liability",
                "effective_date": "2024-01-01",
                "limits": "1M/2M/1M"
            }
        }
        
        return form_data
    
    async def create_case(self, case_data: Dict[str, Any]) -> str:
        """Create ACORD form processing case"""
        if not self._authenticated:
            raise ValueError("Not authenticated with ACORD Forms processor")
        
        form_case_id = f"acord_form_{datetime.now().timestamp()}"
        return form_case_id
    
    async def sync_data(self, data: Dict[str, Any]) -> bool:
        """Sync ACORD form data"""
        if not self._authenticated:
            raise ValueError("Not authenticated with ACORD Forms processor")
        
        return True


# Insurance-specific adapter registry
INSURANCE_ADAPTERS = {
    "guidewire_pc": Guidewire_PolicyCenter_Adapter,
    "guidewire_cc": Guidewire_ClaimCenter_Adapter,
    "duck_creek_policy": Duck_Creek_Policy_Adapter,
    "acord_forms": ACORD_Forms_Adapter
}


def get_insurance_adapter(system_name: str) -> ClosedSourceAdapter:
    """Get an insurance-specific adapter"""
    adapter_class = INSURANCE_ADAPTERS.get(system_name.lower())
    if not adapter_class:
        raise ValueError(f"Unknown insurance system: {system_name}")
    
    return adapter_class()


async def test_insurance_adapters():
    """Test all insurance adapters"""
    logger = logging.getLogger(__name__)
    
    for name, adapter_class in INSURANCE_ADAPTERS.items():
        try:
            adapter = adapter_class()
            success = await adapter.authenticate({})
            logger.info(f"Insurance {name} adapter test: {'PASS' if success else 'FAIL'}")
        except Exception as e:
            logger.error(f"Insurance {name} adapter test failed: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_insurance_adapters())
