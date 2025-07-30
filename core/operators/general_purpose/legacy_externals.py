"""
External Operations Manager
Handles external integrations, third-party APIs, and external service management
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json

from core.services.base import BaseService
from core.services.logger import get_logger

logger = get_logger(__name__)

class IntegrationType(Enum):
    """Types of external integrations"""
    EHR_SYSTEM = "ehr_system"
    LABORATORY = "laboratory"
    IMAGING = "imaging"
    PHARMACY = "pharmacy"
    INSURANCE = "insurance"
    RESEARCH_DATABASE = "research_database"
    CLINICAL_TRIAL = "clinical_trial"
    REGULATORY = "regulatory"

class IntegrationStatus(Enum):
    """Status of external integrations"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"
    RATE_LIMITED = "rate_limited"

@dataclass
class ExternalService:
    """External service configuration"""
    service_id: str
    name: str
    integration_type: IntegrationType
    base_url: str
    api_version: str
    auth_method: str
    rate_limit_per_hour: int
    timeout_seconds: int
    retry_attempts: int
    last_sync: Optional[datetime] = None
    status: IntegrationStatus = IntegrationStatus.INACTIVE

@dataclass
class SyncResult:
    """Result of external service synchronization"""
    service_id: str
    success: bool
    records_processed: int
    errors: List[str]
    duration_seconds: float
    sync_timestamp: datetime

class ExternalOperator(BaseService):
    """External service integration and management"""
    
    def __init__(self):
        super().__init__()
        self.services = self._initialize_external_services()
        self.sync_history = []
        self.rate_limit_tracker = {}
    
    def _initialize_external_services(self) -> Dict[str, ExternalService]:
        """Initialize external service configurations"""
        
        services = {
            "epic_ehr": ExternalService(
                service_id="epic_ehr",
                name="Epic EHR System",
                integration_type=IntegrationType.EHR_SYSTEM,
                base_url="https://api.epic.healthcare.local",
                api_version="v1",
                auth_method="oauth2",
                rate_limit_per_hour=1000,
                timeout_seconds=30,
                retry_attempts=3
            ),
            "lab_corp": ExternalService(
                service_id="lab_corp",
                name="LabCorp Laboratory Services",
                integration_type=IntegrationType.LABORATORY,
                base_url="https://api.labcorp.com",
                api_version="v2",
                auth_method="api_key",
                rate_limit_per_hour=500,
                timeout_seconds=15,
                retry_attempts=2
            ),
            "radiology_pacs": ExternalService(
                service_id="radiology_pacs",
                name="Radiology PACS System",
                integration_type=IntegrationType.IMAGING,
                base_url="https://pacs.radiology.local",
                api_version="v1",
                auth_method="basic",
                rate_limit_per_hour=200,
                timeout_seconds=60,
                retry_attempts=3
            ),
            "cerner_pharmacy": ExternalService(
                service_id="cerner_pharmacy",
                name="Cerner Pharmacy System",
                integration_type=IntegrationType.PHARMACY,
                base_url="https://api.cerner.pharmacy.local",
                api_version="v1",
                auth_method="oauth2",
                rate_limit_per_hour=800,
                timeout_seconds=20,
                retry_attempts=2
            ),
            "aetna_insurance": ExternalService(
                service_id="aetna_insurance",
                name="Aetna Insurance Portal",
                integration_type=IntegrationType.INSURANCE,
                base_url="https://api.aetna.com",
                api_version="v1",
                auth_method="oauth2",
                rate_limit_per_hour=300,
                timeout_seconds=25,
                retry_attempts=3
            ),
            "clinicaltrials_gov": ExternalService(
                service_id="clinicaltrials_gov",
                name="ClinicalTrials.gov Database",
                integration_type=IntegrationType.CLINICAL_TRIAL,
                base_url="https://clinicaltrials.gov/api",
                api_version="v2",
                auth_method="none",
                rate_limit_per_hour=100,
                timeout_seconds=30,
                retry_attempts=2
            ),
            "fda_regulatory": ExternalService(
                service_id="fda_regulatory",
                name="FDA Regulatory Database",
                integration_type=IntegrationType.REGULATORY,
                base_url="https://api.fda.gov",
                api_version="v1",
                auth_method="api_key",
                rate_limit_per_hour=50,
                timeout_seconds=45,
                retry_attempts=3
            )
        }
        
        return services
    
    async def sync_external_service(
        self, 
        service_id: str,
        data_types: Optional[List[str]] = None
    ) -> SyncResult:
        """Synchronize data with external service"""
        
        try:
            if service_id not in self.services:
                raise ValueError(f"Unknown service: {service_id}")
            
            service = self.services[service_id]
            
            # Check rate limits
            if not await self._check_rate_limit(service_id):
                return SyncResult(
                    service_id=service_id,
                    success=False,
                    records_processed=0,
                    errors=["Rate limit exceeded"],
                    duration_seconds=0.0,
                    sync_timestamp=datetime.now()
                )
            
            start_time = datetime.now()
            
            # Perform sync based on integration type
            if service.integration_type == IntegrationType.EHR_SYSTEM:
                result = await self._sync_ehr_data(service, data_types)
            elif service.integration_type == IntegrationType.LABORATORY:
                result = await self._sync_lab_data(service, data_types)
            elif service.integration_type == IntegrationType.IMAGING:
                result = await self._sync_imaging_data(service, data_types)
            elif service.integration_type == IntegrationType.PHARMACY:
                result = await self._sync_pharmacy_data(service, data_types)
            elif service.integration_type == IntegrationType.INSURANCE:
                result = await self._sync_insurance_data(service, data_types)
            elif service.integration_type == IntegrationType.CLINICAL_TRIAL:
                result = await self._sync_clinical_trial_data(service, data_types)
            elif service.integration_type == IntegrationType.REGULATORY:
                result = await self._sync_regulatory_data(service, data_types)
            else:
                result = SyncResult(
                    service_id=service_id,
                    success=False,
                    records_processed=0,
                    errors=[f"Unsupported integration type: {service.integration_type}"],
                    duration_seconds=0.0,
                    sync_timestamp=datetime.now()
                )
            
            # Update service status and last sync time
            if result.success:
                service.status = IntegrationStatus.ACTIVE
                service.last_sync = datetime.now()
            else:
                service.status = IntegrationStatus.ERROR
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            result.duration_seconds = duration
            
            # Update rate limit tracker
            await self._update_rate_limit_tracker(service_id)
            
            # Store sync history
            self.sync_history.append(result)
            
            await self._log_sync_result(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error syncing with {service_id}: {e}")
            return SyncResult(
                service_id=service_id,
                success=False,
                records_processed=0,
                errors=[str(e)],
                duration_seconds=0.0,
                sync_timestamp=datetime.now()
            )
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all external integrations"""
        
        try:
            status_summary = {
                "timestamp": datetime.now().isoformat(),
                "total_services": len(self.services),
                "services": []
            }
            
            for service_id, service in self.services.items():
                service_status = {
                    "service_id": service_id,
                    "name": service.name,
                    "type": service.integration_type.value,
                    "status": service.status.value,
                    "last_sync": service.last_sync.isoformat() if service.last_sync else None,
                    "rate_limit_status": await self._get_rate_limit_status(service_id)
                }
                
                # Add recent sync results
                recent_syncs = [
                    s for s in self.sync_history[-10:]
                    if s.service_id == service_id
                ]
                
                if recent_syncs:
                    latest_sync = recent_syncs[-1]
                    service_status["latest_sync"] = {
                        "success": latest_sync.success,
                        "records_processed": latest_sync.records_processed,
                        "duration_seconds": latest_sync.duration_seconds,
                        "errors": latest_sync.errors
                    }
                
                status_summary["services"].append(service_status)
            
            # Add summary statistics
            active_services = sum(1 for s in self.services.values() if s.status == IntegrationStatus.ACTIVE)
            error_services = sum(1 for s in self.services.values() if s.status == IntegrationStatus.ERROR)
            
            status_summary["summary"] = {
                "active_services": active_services,
                "error_services": error_services,
                "inactive_services": len(self.services) - active_services - error_services
            }
            
            return status_summary
            
        except Exception as e:
            self.logger.error(f"Error getting integration status: {e}")
            raise
    
    async def configure_external_service(
        self,
        service_id: str,
        configuration: Dict[str, Any]
    ) -> bool:
        """Configure external service settings"""
        
        try:
            if service_id not in self.services:
                raise ValueError(f"Unknown service: {service_id}")
            
            service = self.services[service_id]
            
            # Update configuration
            if "base_url" in configuration:
                service.base_url = configuration["base_url"]
            if "rate_limit_per_hour" in configuration:
                service.rate_limit_per_hour = configuration["rate_limit_per_hour"]
            if "timeout_seconds" in configuration:
                service.timeout_seconds = configuration["timeout_seconds"]
            if "retry_attempts" in configuration:
                service.retry_attempts = configuration["retry_attempts"]
            
            # Test connection with new configuration
            test_result = await self._test_service_connection(service)
            
            if test_result:
                service.status = IntegrationStatus.ACTIVE
                await self.audit_log(
                    action="external_service_configured",
                    entity_type="external_integration",
                    metadata={
                        "service_id": service_id,
                        "configuration_updated": list(configuration.keys())
                    }
                )
                return True
            else:
                service.status = IntegrationStatus.ERROR
                return False
            
        except Exception as e:
            self.logger.error(f"Error configuring external service {service_id}: {e}")
            return False
    
    async def _sync_ehr_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync data from EHR system"""
        
        # Mock EHR data sync
        await asyncio.sleep(0.5)  # Simulate API call
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=150,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _sync_lab_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync laboratory data"""
        
        # Mock lab data sync
        await asyncio.sleep(0.3)
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=75,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _sync_imaging_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync imaging data"""
        
        # Mock imaging data sync
        await asyncio.sleep(1.0)  # Imaging data takes longer
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=25,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _sync_pharmacy_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync pharmacy data"""
        
        # Mock pharmacy data sync
        await asyncio.sleep(0.4)
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=50,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _sync_insurance_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync insurance data"""
        
        # Mock insurance data sync
        await asyncio.sleep(0.6)
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=30,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _sync_clinical_trial_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync clinical trial data"""
        
        # Mock clinical trial data sync
        await asyncio.sleep(0.8)
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=10,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _sync_regulatory_data(self, service: ExternalService, data_types: Optional[List[str]]) -> SyncResult:
        """Sync regulatory data"""
        
        # Mock regulatory data sync
        await asyncio.sleep(0.7)
        
        return SyncResult(
            service_id=service.service_id,
            success=True,
            records_processed=5,
            errors=[],
            duration_seconds=0.0,
            sync_timestamp=datetime.now()
        )
    
    async def _check_rate_limit(self, service_id: str) -> bool:
        """Check if service is within rate limits"""
        
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        if service_id not in self.rate_limit_tracker:
            self.rate_limit_tracker[service_id] = {}
        
        service_tracker = self.rate_limit_tracker[service_id]
        requests_this_hour = service_tracker.get(current_hour, 0)
        
        service = self.services[service_id]
        
        return requests_this_hour < service.rate_limit_per_hour
    
    async def _update_rate_limit_tracker(self, service_id: str):
        """Update rate limit tracking"""
        
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        
        if service_id not in self.rate_limit_tracker:
            self.rate_limit_tracker[service_id] = {}
        
        service_tracker = self.rate_limit_tracker[service_id]
        service_tracker[current_hour] = service_tracker.get(current_hour, 0) + 1
        
        # Clean up old tracking data (keep only last 24 hours)
        cutoff_time = current_hour - timedelta(hours=24)
        service_tracker = {
            hour: count for hour, count in service_tracker.items()
            if hour >= cutoff_time
        }
        self.rate_limit_tracker[service_id] = service_tracker
    
    async def _get_rate_limit_status(self, service_id: str) -> Dict[str, Any]:
        """Get rate limit status for service"""
        
        current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
        service_tracker = self.rate_limit_tracker.get(service_id, {})
        requests_this_hour = service_tracker.get(current_hour, 0)
        
        service = self.services[service_id]
        
        return {
            "requests_this_hour": requests_this_hour,
            "limit_per_hour": service.rate_limit_per_hour,
            "remaining": service.rate_limit_per_hour - requests_this_hour,
            "percentage_used": (requests_this_hour / service.rate_limit_per_hour) * 100
        }
    
    async def _test_service_connection(self, service: ExternalService) -> bool:
        """Test connection to external service"""
        
        try:
            # Mock connection test
            await asyncio.sleep(0.1)
            return True
            
        except Exception as e:
            self.logger.error(f"Connection test failed for {service.service_id}: {e}")
            return False
    
    async def _log_sync_result(self, result: SyncResult):
        """Log synchronization result"""
        await self.audit_log(
            action="external_service_sync",
            entity_type="external_integration",
            metadata={
                "service_id": result.service_id,
                "success": result.success,
                "records_processed": result.records_processed,
                "duration_seconds": result.duration_seconds,
                "error_count": len(result.errors)
            }
        )
