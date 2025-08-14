"""Healthcare-specific repository implementations."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func

from .base import (
    Repository,
    CacheableRepository,
    AuditableRepository,
    SearchableRepository
)


class PatientRepository(SearchableRepository):
    """Repository for patient data management."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """Initialize patient repository."""
        search_fields = ['first_name', 'last_name', 'mrn', 'email']
        super().__init__(session, model_class, search_fields)
        self._audit_repository = AuditableRepository(session, model_class, audit_logger)
    
    async def create(self, entity):
        """Create with audit logging."""
        return await self._audit_repository.create(entity)
    
    async def update(self, entity):
        """Update with audit logging."""
        return await self._audit_repository.update(entity)
    
    async def delete(self, entity_id):
        """Delete with audit logging."""
        return await self._audit_repository.delete(entity_id)
    
    async def get_by_mrn(self, mrn: str) -> Optional:
        """Get patient by medical record number."""
        return self.session.query(self.model_class).filter(
            self.model_class.mrn == mrn
        ).first()
    
    async def get_by_email(self, email: str) -> Optional:
        """Get patient by email address."""
        return self.session.query(self.model_class).filter(
            self.model_class.email == email
        ).first()
    
    async def search_by_demographics(
        self,
        first_name: str = None,
        last_name: str = None,
        date_of_birth: date = None,
        phone: str = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Search patients by demographic information."""
        query = self.session.query(self.model_class)
        
        conditions = []
        
        if first_name:
            conditions.append(
                self.model_class.first_name.ilike(f"%{first_name}%")
            )
        
        if last_name:
            conditions.append(
                self.model_class.last_name.ilike(f"%{last_name}%")
            )
        
        if date_of_birth:
            conditions.append(
                self.model_class.date_of_birth == date_of_birth
            )
        
        if phone:
            # Clean phone number for search
            clean_phone = ''.join(filter(str.isdigit, phone))
            conditions.append(
                func.regexp_replace(self.model_class.phone, r'[^\d]', '', 'g')
                .like(f"%{clean_phone}%")
            )
        
        if conditions:
            query = query.filter(and_(*conditions))
        
        return query.offset(skip).limit(limit).all()
    
    async def get_patients_by_provider(
        self,
        provider_id: Union[str, UUID],
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get patients assigned to a specific provider."""
        return self.session.query(self.model_class).filter(
            self.model_class.primary_provider_id == provider_id
        ).offset(skip).limit(limit).all()
    
    async def get_patients_by_age_range(
        self,
        min_age: int = None,
        max_age: int = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get patients within an age range."""
        query = self.session.query(self.model_class)
        
        current_date = datetime.now().date()
        
        if min_age is not None:
            min_birth_date = date(current_date.year - min_age, 1, 1)
            query = query.filter(self.model_class.date_of_birth <= min_birth_date)
        
        if max_age is not None:
            max_birth_date = date(current_date.year - max_age - 1, 12, 31)
            query = query.filter(self.model_class.date_of_birth >= max_birth_date)
        
        return query.offset(skip).limit(limit).all()


class ProviderRepository(SearchableRepository):
    """Repository for healthcare provider data management."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """Initialize provider repository."""
        search_fields = ['first_name', 'last_name', 'npi', 'specialty', 'organization']
        super().__init__(session, model_class, search_fields)
        self._audit_repository = AuditableRepository(session, model_class, audit_logger)
    
    async def create(self, entity):
        """Create with audit logging."""
        return await self._audit_repository.create(entity)
    
    async def update(self, entity):
        """Update with audit logging."""
        return await self._audit_repository.update(entity)
    
    async def delete(self, entity_id):
        """Delete with audit logging."""
        return await self._audit_repository.delete(entity_id)
    
    async def get_by_npi(self, npi: str) -> Optional[Any]:
        """Get provider by National Provider Identifier."""
        return self.session.query(self.model_class).filter(
            self.model_class.npi == npi
        ).first()
    
    async def get_by_specialty(
        self,
        specialty: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get providers by specialty."""
        return self.session.query(self.model_class).filter(
            self.model_class.specialty.ilike(f"%{specialty}%")
        ).offset(skip).limit(limit).all()
    
    async def get_by_organization(
        self,
        organization: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get providers by organization."""
        return self.session.query(self.model_class).filter(
            self.model_class.organization.ilike(f"%{organization}%")
        ).offset(skip).limit(limit).all()
    
    async def get_active_providers(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get all active providers."""
        return self.session.query(self.model_class).filter(
            self.model_class.is_active == True
        ).offset(skip).limit(limit).all()


class EncounterRepository(Repository, AuditableRepository):
    """Repository for medical encounter data management."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """Initialize encounter repository."""
        super().__init__(session, model_class)
        self.audit_logger = audit_logger
    
    async def get_by_patient(
        self,
        patient_id: Union[str, UUID],
        skip: int = 0,
        limit: int = 100,
        include_details: bool = False
    ) -> List:
        """Get encounters for a specific patient."""
        query = self.session.query(self.model_class).filter(
            self.model_class.patient_id == patient_id
        )
        
        if include_details:
            query = query.options(
                joinedload(self.model_class.observations),
                joinedload(self.model_class.diagnoses),
                joinedload(self.model_class.procedures)
            )
        
        return query.order_by(
            self.model_class.encounter_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_by_provider(
        self,
        provider_id: Union[str, UUID],
        start_date: date = None,
        end_date: date = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get encounters for a specific provider."""
        query = self.session.query(self.model_class).filter(
            self.model_class.provider_id == provider_id
        )
        
        if start_date:
            query = query.filter(self.model_class.encounter_date >= start_date)
        
        if end_date:
            query = query.filter(self.model_class.encounter_date <= end_date)
        
        return query.order_by(
            self.model_class.encounter_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_by_encounter_type(
        self,
        encounter_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get encounters by type."""
        return self.session.query(self.model_class).filter(
            self.model_class.encounter_type == encounter_type
        ).offset(skip).limit(limit).all()
    
    async def get_recent_encounters(
        self,
        days: int = 30,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get recent encounters within specified days."""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        return self.session.query(self.model_class).filter(
            self.model_class.encounter_date >= cutoff_date
        ).order_by(
            self.model_class.encounter_date.desc()
        ).offset(skip).limit(limit).all()


class ObservationRepository(Repository, AuditableRepository):
    """Repository for clinical observation data management."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """Initialize observation repository."""
        super().__init__(session, model_class)
        self.audit_logger = audit_logger
    
    async def get_by_patient(
        self,
        patient_id: Union[str, UUID],
        observation_code: str = None,
        start_date: date = None,
        end_date: date = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get observations for a specific patient."""
        query = self.session.query(self.model_class).filter(
            self.model_class.patient_id == patient_id
        )
        
        if observation_code:
            query = query.filter(
                self.model_class.code == observation_code
            )
        
        if start_date:
            query = query.filter(
                self.model_class.observation_date >= start_date
            )
        
        if end_date:
            query = query.filter(
                self.model_class.observation_date <= end_date
            )
        
        return query.order_by(
            self.model_class.observation_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_by_encounter(
        self,
        encounter_id: Union[str, UUID],
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get observations for a specific encounter."""
        return self.session.query(self.model_class).filter(
            self.model_class.encounter_id == encounter_id
        ).offset(skip).limit(limit).all()
    
    async def get_vital_signs(
        self,
        patient_id: Union[str, UUID],
        start_date: date = None,
        end_date: date = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get vital sign observations for a patient."""
        vital_codes = [
            '8480-6',  # Systolic blood pressure
            '8462-4',  # Diastolic blood pressure
            '8867-4',  # Heart rate
            '9279-1',  # Respiratory rate
            '8310-5',  # Body temperature
            '29463-7', # Body weight
            '8302-2',  # Body height
        ]
        
        query = self.session.query(self.model_class).filter(
            and_(
                self.model_class.patient_id == patient_id,
                self.model_class.code.in_(vital_codes)
            )
        )
        
        if start_date:
            query = query.filter(
                self.model_class.observation_date >= start_date
            )
        
        if end_date:
            query = query.filter(
                self.model_class.observation_date <= end_date
            )
        
        return query.order_by(
            self.model_class.observation_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_lab_results(
        self,
        patient_id: Union[str, UUID],
        lab_code: str = None,
        start_date: date = None,
        end_date: date = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get laboratory result observations for a patient."""
        query = self.session.query(self.model_class).filter(
            and_(
                self.model_class.patient_id == patient_id,
                self.model_class.category == 'laboratory'
            )
        )
        
        if lab_code:
            query = query.filter(self.model_class.code == lab_code)
        
        if start_date:
            query = query.filter(
                self.model_class.observation_date >= start_date
            )
        
        if end_date:
            query = query.filter(
                self.model_class.observation_date <= end_date
            )
        
        return query.order_by(
            self.model_class.observation_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_abnormal_results(
        self,
        patient_id: Union[str, UUID] = None,
        start_date: date = None,
        end_date: date = None,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get observations with abnormal results."""
        query = self.session.query(self.model_class).filter(
            self.model_class.interpretation.in_(['H', 'L', 'A', 'AA'])
        )
        
        if patient_id:
            query = query.filter(self.model_class.patient_id == patient_id)
        
        if start_date:
            query = query.filter(
                self.model_class.observation_date >= start_date
            )
        
        if end_date:
            query = query.filter(
                self.model_class.observation_date <= end_date
            )
        
        return query.order_by(
            self.model_class.observation_date.desc()
        ).offset(skip).limit(limit).all()


class DiagnosisRepository(Repository, AuditableRepository):
    """Repository for diagnosis data management."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """Initialize diagnosis repository."""
        super().__init__(session, model_class)
        self.audit_logger = audit_logger
    
    async def get_by_patient(
        self,
        patient_id: Union[str, UUID],
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get diagnoses for a specific patient."""
        query = self.session.query(self.model_class).filter(
            self.model_class.patient_id == patient_id
        )
        
        if active_only:
            query = query.filter(
                self.model_class.clinical_status == 'active'
            )
        
        return query.order_by(
            self.model_class.onset_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_by_icd_code(
        self,
        icd_code: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get diagnoses by ICD code."""
        return self.session.query(self.model_class).filter(
            self.model_class.icd_code == icd_code
        ).offset(skip).limit(limit).all()
    
    async def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get diagnoses by category."""
        return self.session.query(self.model_class).filter(
            self.model_class.category.ilike(f"%{category}%")
        ).offset(skip).limit(limit).all()


class MedicationRepository(Repository, AuditableRepository):
    """Repository for medication data management."""
    
    def __init__(self, session: Session, model_class: type, audit_logger=None):
        """Initialize medication repository."""
        super().__init__(session, model_class)
        self.audit_logger = audit_logger
    
    async def get_by_patient(
        self,
        patient_id: Union[str, UUID],
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get medications for a specific patient."""
        query = self.session.query(self.model_class).filter(
            self.model_class.patient_id == patient_id
        )
        
        if active_only:
            query = query.filter(
                self.model_class.status == 'active'
            )
        
        return query.order_by(
            self.model_class.prescribed_date.desc()
        ).offset(skip).limit(limit).all()
    
    async def get_by_drug_code(
        self,
        drug_code: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Get medications by drug code."""
        return self.session.query(self.model_class).filter(
            self.model_class.code == drug_code
        ).offset(skip).limit(limit).all()
    
    async def search_by_name(
        self,
        medication_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        """Search medications by name."""
        return self.session.query(self.model_class).filter(
            self.model_class.display_name.ilike(f"%{medication_name}%")
        ).offset(skip).limit(limit).all()
