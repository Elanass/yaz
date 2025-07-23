"""
Cohort Management Service
Handles cohort input, validation, processing, and analysis
"""

import csv
import json
import base64
import hashlib
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta
from io import StringIO, BytesIO
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import structlog
import asyncio
from concurrent.futures import ThreadPoolExecutor

from ..core.config import settings
from ..db.models import (
    CohortStudy, CohortPatient, InferenceSession, PatientDecisionResult,
    CohortExportTask, CohortHypothesis, User
)
from ..schemas.cohort import (
    CohortUploadRequest, CohortPatientInput, InferenceSessionRequest,
    CohortUploadFormat, CohortStatus, InferenceStatus
)
from ..services.audit_service import AuditService, AuditEvent, AuditEventType, AuditSeverity
from ..services.evidence_service import TamperProofEvidenceService, EvidenceRecord
from ..engines.decision_engine import DecisionEngine  # Existing decision engine

logger = structlog.get_logger(__name__)

class CohortValidationError(Exception):
    """Exception for cohort validation errors"""
    pass

class CohortDataValidator:
    """Validates cohort patient data"""
    
    REQUIRED_FIELDS = {"patient_identifier"}
    NUMERIC_FIELDS = {"age", "ecog_score", "karnofsky_score"}
    CATEGORICAL_FIELDS = {
        "gender": {"male", "female", "other", "unknown"},
        "tumor_stage": {"T1", "T2", "T3", "T4", "TX"},
        "tumor_grade": {"G1", "G2", "G3", "G4", "GX"}
    }
    
    @classmethod
    def validate_patient(cls, patient_data: Dict[str, Any]) -> Tuple[bool, List[str], List[str]]:
        """
        Validate individual patient data
        Returns: (is_valid, errors, warnings)
        """
        errors = []
        warnings = []
        
        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if not patient_data.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate numeric fields
        for field in cls.NUMERIC_FIELDS:
            value = patient_data.get(field)
            if value is not None:
                try:
                    num_value = float(value)
                    if field == "age" and (num_value < 0 or num_value > 150):
                        errors.append(f"Invalid age: {num_value}")
                    elif field == "ecog_score" and (num_value < 0 or num_value > 5):
                        errors.append(f"Invalid ECOG score: {num_value}")
                    elif field == "karnofsky_score" and (num_value < 0 or num_value > 100):
                        errors.append(f"Invalid Karnofsky score: {num_value}")
                except (ValueError, TypeError):
                    errors.append(f"Invalid numeric value for {field}: {value}")
        
        # Validate categorical fields
        for field, valid_values in cls.CATEGORICAL_FIELDS.items():
            value = patient_data.get(field)
            if value and value.lower() not in {v.lower() for v in valid_values}:
                warnings.append(f"Unexpected value for {field}: {value}")
        
        # Check data completeness
        total_fields = len(patient_data)
        empty_fields = sum(1 for v in patient_data.values() if v is None or v == "")
        completeness = (total_fields - empty_fields) / total_fields if total_fields > 0 else 0
        
        if completeness < 0.5:
            warnings.append(f"Low data completeness: {completeness:.1%}")
        
        return len(errors) == 0, errors, warnings

class CohortFileProcessor:
    """Processes different cohort file formats"""
    
    @staticmethod
    def process_csv(file_content: str) -> List[Dict[str, Any]]:
        """Process CSV file content"""
        try:
            # Handle both string and bytes
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8')
            
            csv_reader = csv.DictReader(StringIO(file_content))
            patients = []
            
            for row_num, row in enumerate(csv_reader, start=1):
                # Clean and standardize field names
                cleaned_row = {}
                for key, value in row.items():
                    if key:
                        clean_key = key.strip().lower().replace(' ', '_').replace('-', '_')
                        cleaned_row[clean_key] = value.strip() if value else None
                
                # Map common field variants
                field_mapping = {
                    'patient_id': 'patient_identifier',
                    'id': 'patient_identifier',
                    'subject_id': 'patient_identifier',
                    'ecog': 'ecog_score',
                    'karnofsky': 'karnofsky_score',
                    'sex': 'gender'
                }
                
                for old_key, new_key in field_mapping.items():
                    if old_key in cleaned_row and new_key not in cleaned_row:
                        cleaned_row[new_key] = cleaned_row.pop(old_key)
                
                cleaned_row['import_row_number'] = row_num
                patients.append(cleaned_row)
            
            return patients
            
        except Exception as e:
            logger.error("Failed to process CSV", error=str(e))
            raise CohortValidationError(f"CSV processing failed: {str(e)}")
    
    @staticmethod
    def process_json(file_content: str) -> List[Dict[str, Any]]:
        """Process JSON file content"""
        try:
            data = json.loads(file_content)
            
            # Handle different JSON structures
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                if 'patients' in data:
                    return data['patients']
                elif 'entry' in data:  # FHIR Bundle-like structure
                    return [entry.get('resource', entry) for entry in data['entry']]
                else:
                    return [data]  # Single patient
            else:
                raise ValueError("Unexpected JSON structure")
                
        except Exception as e:
            logger.error("Failed to process JSON", error=str(e))
            raise CohortValidationError(f"JSON processing failed: {str(e)}")
    
    @staticmethod
    def process_fhir_bundle(file_content: str) -> List[Dict[str, Any]]:
        """Process FHIR Bundle"""
        try:
            bundle = json.loads(file_content)
            
            if bundle.get('resourceType') != 'Bundle':
                raise ValueError("Not a valid FHIR Bundle")
            
            patients = []
            for entry in bundle.get('entry', []):
                resource = entry.get('resource', {})
                if resource.get('resourceType') == 'Patient':
                    # Convert FHIR Patient to cohort format
                    patient_data = CohortFileProcessor._convert_fhir_patient(resource)
                    patients.append(patient_data)
            
            return patients
            
        except Exception as e:
            logger.error("Failed to process FHIR Bundle", error=str(e))
            raise CohortValidationError(f"FHIR Bundle processing failed: {str(e)}")
    
    @staticmethod
    def _convert_fhir_patient(patient_resource: Dict[str, Any]) -> Dict[str, Any]:
        """Convert FHIR Patient resource to cohort format"""
        patient_data = {
            'patient_identifier': patient_resource.get('id'),
            'gender': patient_resource.get('gender'),
        }
        
        # Extract birth date and calculate age
        birth_date = patient_resource.get('birthDate')
        if birth_date:
            try:
                birth_dt = datetime.strptime(birth_date, '%Y-%m-%d')
                age = (datetime.now() - birth_dt).days // 365
                patient_data['age'] = age
            except ValueError:
                pass
        
        # Extract extensions or other data
        # This would need to be customized based on your FHIR profile
        
        return patient_data

class CohortProcessingEngine:
    """Handles batch processing of cohort patients through decision engines"""
    
    def __init__(self, db: Session):
        self.db = db
        self.decision_engine = DecisionEngine()
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def process_cohort_batch(
        self,
        inference_session: InferenceSession,
        cohort_patients: List[CohortPatient]
    ) -> None:
        """Process a batch of cohort patients"""
        
        try:
            # Update session status
            inference_session.status = InferenceStatus.RUNNING
            inference_session.started_at = datetime.utcnow()
            inference_session.total_patients = len(cohort_patients)
            self.db.commit()
            
            # Process patients in batches
            batch_size = 10
            for i in range(0, len(cohort_patients), batch_size):
                batch = cohort_patients[i:i + batch_size]
                
                # Process batch concurrently
                tasks = [
                    self._process_single_patient(inference_session, patient)
                    for patient in batch
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Update progress
                processed_count = i + len(batch)
                failed_count = sum(1 for r in results if isinstance(r, Exception))
                
                inference_session.processed_patients = processed_count
                inference_session.failed_patients += failed_count
                inference_session.progress_percentage = (processed_count / len(cohort_patients)) * 100
                
                self.db.commit()
                
                logger.info(
                    "Processed cohort batch",
                    session_id=inference_session.id,
                    processed=processed_count,
                    total=len(cohort_patients),
                    failed=failed_count
                )
            
            # Complete session
            inference_session.status = InferenceStatus.COMPLETED
            inference_session.completed_at = datetime.utcnow()
            inference_session.duration_seconds = (
                inference_session.completed_at - inference_session.started_at
            ).total_seconds()
            
            # Generate results summary
            inference_session.results_summary = self._generate_results_summary(inference_session)
            
            self.db.commit()
            
        except Exception as e:
            logger.error("Cohort processing failed", session_id=inference_session.id, error=str(e))
            
            inference_session.status = InferenceStatus.FAILED
            inference_session.error_log = {"error": str(e), "timestamp": datetime.utcnow().isoformat()}
            self.db.commit()
            raise
    
    async def _process_single_patient(
        self,
        inference_session: InferenceSession,
        cohort_patient: CohortPatient
    ) -> PatientDecisionResult:
        """Process a single patient through decision engines"""
        
        start_time = datetime.utcnow()
        
        try:
            # Convert cohort patient to decision engine input format
            patient_data = self._convert_to_decision_input(cohort_patient)
            
            # Initialize result
            result = PatientDecisionResult(
                cohort_patient_id=cohort_patient.id,
                inference_session_id=inference_session.id,
                input_completeness=cohort_patient.data_completeness_score or 0.0
            )
            
            # Run decision engines
            if "adci" in inference_session.decision_engines:
                adci_result = await self._run_adci_engine(patient_data)
                result.adci_score = adci_result.get('score')
                result.adci_confidence = adci_result.get('confidence')
                result.adci_recommendation = adci_result.get('recommendation')
            
            if "gastrectomy" in inference_session.decision_engines:
                gastrectomy_result = await self._run_gastrectomy_engine(patient_data)
                result.gastrectomy_recommendation = gastrectomy_result.get('recommendation')
                result.gastrectomy_confidence = gastrectomy_result.get('confidence')
                result.gastrectomy_risk_factors = gastrectomy_result.get('risk_factors')
            
            if "flot" in inference_session.decision_engines:
                flot_result = await self._run_flot_engine(patient_data)
                result.flot_eligibility = flot_result.get('eligible')
                result.flot_recommendation = flot_result.get('recommendation')
                result.flot_confidence = flot_result.get('confidence')
            
            # Generate overall recommendation
            result.primary_recommendation = self._generate_primary_recommendation(result)
            result.recommendation_confidence = self._calculate_overall_confidence(result)
            
            # Processing metadata
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            result.processing_time_ms = processing_time
            result.engine_versions = {"adci": "1.0", "gastrectomy": "1.0", "flot": "1.0"}
            
            # Save result
            self.db.add(result)
            self.db.flush()
            
            return result
            
        except Exception as e:
            logger.error(
                "Patient processing failed",
                patient_id=cohort_patient.patient_identifier,
                error=str(e)
            )
            raise
    
    def _convert_to_decision_input(self, cohort_patient: CohortPatient) -> Dict[str, Any]:
        """Convert cohort patient to decision engine input format"""
        return {
            "patient_id": cohort_patient.patient_identifier,
            "age": cohort_patient.age,
            "gender": cohort_patient.gender,
            "tumor_stage": cohort_patient.tumor_stage,
            "tumor_grade": cohort_patient.tumor_grade,
            "tumor_location": cohort_patient.tumor_location,
            "ecog_score": cohort_patient.ecog_score,
            "karnofsky_score": cohort_patient.karnofsky_score,
            "biomarkers": cohort_patient.biomarkers or {},
            "genetic_mutations": cohort_patient.genetic_mutations or {},
            "prior_treatments": cohort_patient.prior_treatments or [],
            "comorbidities": cohort_patient.comorbidities or [],
            "lab_values": cohort_patient.lab_values or {},
            "vital_signs": cohort_patient.vital_signs or {}
        }
    
    async def _run_adci_engine(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run ADCI decision engine"""
        # This would integrate with your existing ADCI engine
        # For now, return mock results
        return {
            "score": 0.75,
            "confidence": 0.85,
            "recommendation": "surgical_candidate",
            "factors": ["good_performance_status", "resectable_tumor"]
        }
    
    async def _run_gastrectomy_engine(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run gastrectomy decision engine"""
        return {
            "recommendation": "total_gastrectomy",
            "confidence": 0.80,
            "risk_factors": ["advanced_age"],
            "surgical_approach": "laparoscopic"
        }
    
    async def _run_flot_engine(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run FLOT protocol engine"""
        return {
            "eligible": True,
            "recommendation": "neoadjuvant_flot",
            "confidence": 0.90,
            "cycles": 4,
            "contraindications": []
        }
    
    def _generate_primary_recommendation(self, result: PatientDecisionResult) -> str:
        """Generate primary treatment recommendation"""
        # Logic to combine engine results into primary recommendation
        if result.flot_eligibility and result.adci_score and result.adci_score > 0.7:
            return "neoadjuvant_chemotherapy_then_surgery"
        elif result.adci_score and result.adci_score > 0.6:
            return "primary_surgical_resection"
        else:
            return "palliative_care"
    
    def _calculate_overall_confidence(self, result: PatientDecisionResult) -> float:
        """Calculate overall recommendation confidence"""
        confidences = []
        if result.adci_confidence:
            confidences.append(result.adci_confidence)
        if result.gastrectomy_confidence:
            confidences.append(result.gastrectomy_confidence)
        if result.flot_confidence:
            confidences.append(result.flot_confidence)
        
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def _generate_results_summary(self, inference_session: InferenceSession) -> Dict[str, Any]:
        """Generate summary statistics for inference session"""
        results = self.db.query(PatientDecisionResult).filter(
            PatientDecisionResult.inference_session_id == inference_session.id
        ).all()
        
        if not results:
            return {}
        
        # Calculate statistics
        adci_scores = [r.adci_score for r in results if r.adci_score is not None]
        surgical_candidates = sum(1 for r in results if r.adci_score and r.adci_score > 0.6)
        flot_eligible = sum(1 for r in results if r.flot_eligibility)
        
        return {
            "total_patients": len(results),
            "average_adci_score": sum(adci_scores) / len(adci_scores) if adci_scores else 0,
            "surgical_candidates": surgical_candidates,
            "surgical_candidate_percentage": surgical_candidates / len(results) if results else 0,
            "flot_eligible_patients": flot_eligible,
            "flot_eligible_percentage": flot_eligible / len(results) if results else 0,
            "high_confidence_decisions": sum(
                1 for r in results 
                if r.recommendation_confidence and r.recommendation_confidence > 0.8
            ),
            "processing_statistics": {
                "total_processing_time": inference_session.duration_seconds,
                "average_time_per_patient": (
                    inference_session.duration_seconds / len(results) 
                    if results and inference_session.duration_seconds else 0
                )
            }
        }

class CohortService:
    """Main cohort management service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)
        self.evidence_service = TamperProofEvidenceService(db)
        self.processing_engine = CohortProcessingEngine(db)
        
    async def create_cohort_study(
        self,
        request: CohortUploadRequest,
        user: User,
        file_content: Optional[str] = None
    ) -> CohortStudy:
        """Create a new cohort study"""
        
        try:
            # Create cohort study
            cohort_study = CohortStudy(
                name=request.name,
                description=request.description,
                upload_format=request.upload_format,
                study_type=request.study_type,
                contains_phi=request.contains_phi,
                anonymization_level=request.anonymization_level,
                consent_status=request.consent_status,
                created_by=user.id,
                status=CohortStatus.DRAFT
            )
            
            self.db.add(cohort_study)
            self.db.flush()  # Get ID
            
            # Process patient data
            patients_data = []
            
            if request.upload_format == CohortUploadFormat.MANUAL and request.patients:
                patients_data = [p.dict() for p in request.patients]
            elif file_content:
                patients_data = self._process_file_content(file_content, request.upload_format)
            
            # Store original data in IPFS
            if patients_data:
                evidence_record = EvidenceRecord(
                    evidence_id=f"cohort_{cohort_study.id}",
                    evidence_type="cohort_data",
                    title=f"Cohort Data: {request.name}",
                    description="Original cohort patient data",
                    content=patients_data,
                    metadata={},
                    source="cohort_upload",
                    created_by=user.id,
                    tags=["cohort", "patient_data"],
                    clinical_context={"cohort_id": str(cohort_study.id)}
                )
                
                ipfs_result = await self.evidence_service.store_evidence(evidence_record)
                cohort_study.ipfs_hash = ipfs_result["ipfs_hash"]
                cohort_study.file_hash = ipfs_result["content_hash"]
            
            # Validate and store patients
            await self._process_and_validate_patients(cohort_study, patients_data)
            
            # Update status
            if cohort_study.invalid_patients == 0:
                cohort_study.status = CohortStatus.VALIDATED
            else:
                cohort_study.status = CohortStatus.VALIDATING
            
            self.db.commit()
            
            # Log creation
            await self.audit_service.log_event(
                AuditEvent(
                    event_type=AuditEventType.DATA_CREATE,
                    user_id=user.id,
                    resource_type="cohort_study",
                    resource_id=str(cohort_study.id),
                    action="create_cohort",
                    details={
                        "cohort_name": request.name,
                        "upload_format": request.upload_format.value,
                        "total_patients": cohort_study.total_patients,
                        "valid_patients": cohort_study.valid_patients
                    },
                    ip_address="",
                    user_agent="",
                    severity=AuditSeverity.MEDIUM
                )
            )
            
            return cohort_study
            
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to create cohort study", error=str(e))
            raise
    
    def _process_file_content(
        self,
        file_content: str,
        upload_format: CohortUploadFormat
    ) -> List[Dict[str, Any]]:
        """Process uploaded file content"""
        
        # Decode base64 content
        try:
            decoded_content = base64.b64decode(file_content).decode('utf-8')
        except Exception:
            decoded_content = file_content  # Assume it's already decoded
        
        if upload_format == CohortUploadFormat.CSV:
            return CohortFileProcessor.process_csv(decoded_content)
        elif upload_format == CohortUploadFormat.JSON:
            return CohortFileProcessor.process_json(decoded_content)
        elif upload_format == CohortUploadFormat.FHIR_BUNDLE:
            return CohortFileProcessor.process_fhir_bundle(decoded_content)
        else:
            raise ValueError(f"Unsupported upload format: {upload_format}")
    
    async def _process_and_validate_patients(
        self,
        cohort_study: CohortStudy,
        patients_data: List[Dict[str, Any]]
    ) -> None:
        """Process and validate patient data"""
        
        total_patients = 0
        valid_patients = 0
        invalid_patients = 0
        validation_errors = []
        validation_warnings = []
        
        for patient_data in patients_data:
            total_patients += 1
            
            # Validate patient
            is_valid, errors, warnings = CohortDataValidator.validate_patient(patient_data)
            
            if errors:
                validation_errors.extend([
                    f"Patient {patient_data.get('patient_identifier', total_patients)}: {error}"
                    for error in errors
                ])
            
            if warnings:
                validation_warnings.extend([
                    f"Patient {patient_data.get('patient_identifier', total_patients)}: {warning}"
                    for warning in warnings
                ])
            
            # Calculate completeness score
            non_empty_fields = sum(1 for v in patient_data.values() if v is not None and v != "")
            completeness_score = non_empty_fields / len(patient_data) if patient_data else 0
            
            # Create cohort patient record
            cohort_patient = CohortPatient(
                cohort_study_id=cohort_study.id,
                patient_identifier=patient_data.get('patient_identifier', f'PATIENT_{total_patients}'),
                external_patient_id=patient_data.get('external_patient_id'),
                age=patient_data.get('age'),
                gender=patient_data.get('gender'),
                ethnicity=patient_data.get('ethnicity'),
                primary_diagnosis=patient_data.get('primary_diagnosis'),
                tumor_stage=patient_data.get('tumor_stage'),
                tumor_grade=patient_data.get('tumor_grade'),
                tumor_location=patient_data.get('tumor_location'),
                ecog_score=patient_data.get('ecog_score'),
                karnofsky_score=patient_data.get('karnofsky_score'),
                biomarkers=patient_data.get('biomarkers'),
                genetic_mutations=patient_data.get('genetic_mutations'),
                prior_treatments=patient_data.get('prior_treatments'),
                current_medications=patient_data.get('current_medications'),
                comorbidities=patient_data.get('comorbidities'),
                lab_values=patient_data.get('lab_values'),
                vital_signs=patient_data.get('vital_signs'),
                is_valid=is_valid,
                validation_errors=errors if errors else None,
                data_completeness_score=completeness_score,
                import_row_number=patient_data.get('import_row_number'),
                data_source=patient_data.get('data_source', 'upload')
            )
            
            self.db.add(cohort_patient)
            
            if is_valid:
                valid_patients += 1
            else:
                invalid_patients += 1
        
        # Update cohort study statistics
        cohort_study.total_patients = total_patients
        cohort_study.valid_patients = valid_patients
        cohort_study.invalid_patients = invalid_patients
        cohort_study.validation_errors = validation_errors if validation_errors else None
        cohort_study.validation_warnings = validation_warnings if validation_warnings else None
    
    async def start_inference_session(
        self,
        request: InferenceSessionRequest,
        user: User
    ) -> InferenceSession:
        """Start a new inference session for cohort processing"""
        
        # Get cohort study
        cohort_study = self.db.query(CohortStudy).filter(
            CohortStudy.id == request.cohort_study_id
        ).first()
        
        if not cohort_study:
            raise ValueError("Cohort study not found")
        
        if cohort_study.status != CohortStatus.VALIDATED:
            raise ValueError("Cohort study must be validated before processing")
        
        # Create inference session
        inference_session = InferenceSession(
            cohort_study_id=cohort_study.id,
            session_name=request.session_name,
            session_description=request.session_description,
            decision_engines=request.decision_engines,
            processing_parameters=request.processing_parameters,
            created_by=user.id,
            status=InferenceStatus.PENDING
        )
        
        self.db.add(inference_session)
        self.db.commit()
        
        # Start processing in background
        cohort_patients = self.db.query(CohortPatient).filter(
            CohortPatient.cohort_study_id == cohort_study.id,
            CohortPatient.is_valid == True
        ).all()
        
        # Process asynchronously
        asyncio.create_task(
            self.processing_engine.process_cohort_batch(inference_session, cohort_patients)
        )
        
        # Log session start
        await self.audit_service.log_event(
            AuditEvent(
                event_type=AuditEventType.DATA_CREATE,
                user_id=user.id,
                resource_type="inference_session",
                resource_id=str(inference_session.id),
                action="start_inference",
                details={
                    "cohort_study_id": str(cohort_study.id),
                    "session_name": request.session_name,
                    "decision_engines": request.decision_engines,
                    "patient_count": len(cohort_patients)
                },
                ip_address="",
                user_agent="",
                severity=AuditSeverity.HIGH
            )
        )
        
        return inference_session
    
    async def get_cohort_results(
        self,
        cohort_study_id: str,
        inference_session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get cohort analysis results"""
        
        cohort_study = self.db.query(CohortStudy).filter(
            CohortStudy.id == cohort_study_id
        ).first()
        
        if not cohort_study:
            raise ValueError("Cohort study not found")
        
        # Get inference session
        if inference_session_id:
            inference_session = self.db.query(InferenceSession).filter(
                InferenceSession.id == inference_session_id
            ).first()
        else:
            # Get latest completed session
            inference_session = self.db.query(InferenceSession).filter(
                InferenceSession.cohort_study_id == cohort_study_id,
                InferenceSession.status == InferenceStatus.COMPLETED
            ).order_by(desc(InferenceSession.completed_at)).first()
        
        if not inference_session:
            raise ValueError("No completed inference session found")
        
        # Get patient results
        patient_results = self.db.query(PatientDecisionResult).filter(
            PatientDecisionResult.inference_session_id == inference_session.id
        ).all()
        
        return {
            "cohort_study": cohort_study,
            "inference_session": inference_session,
            "patient_results": patient_results,
            "summary_stats": inference_session.results_summary or {}
        }
