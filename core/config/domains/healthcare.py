"""
Healthcare Domain Configuration

Specialized configuration for healthcare applications including HIPAA compliance,
clinical workflows, and medical data management.
"""

from typing import Dict, Any
from core.config.domains import DomainConfiguration, DomainComponent, DomainType, ComponentType


class HealthcareDomainConfig(DomainConfiguration):
    """Healthcare-specific platform configuration"""
    
    def __init__(self):
        super().__init__(DomainType.HEALTHCARE)
    
    def _initialize_components(self):
        """Initialize healthcare-specific components"""
        
        # Authentication with HIPAA compliance
        self.components[ComponentType.AUTHENTICATION.value] = DomainComponent(
            component_type=ComponentType.AUTHENTICATION,
            priority=1,
            config={
                "require_mfa": True,
                "session_timeout_minutes": 30,
                "password_complexity": "high",
                "audit_all_access": True,
                "role_based_access": True,
                "roles": ["physician", "nurse", "admin", "researcher", "resident"],
                "permissions": {
                    "physician": ["read:all_patients", "write:all_patients", "prescribe", "diagnose"],
                    "nurse": ["read:assigned_patients", "write:vitals", "write:notes"],
                    "admin": ["admin:users", "admin:system", "read:audit_logs"],
                    "researcher": ["read:anonymized_data", "export:research_data"],
                    "resident": ["read:supervised_patients", "write:supervised_notes"]
                },
                "compliance_features": {
                    "hipaa_logging": True,
                    "gdpr_consent": True,
                    "minimum_necessary_rule": True,
                    "break_glass_access": True
                }
            },
            dependencies=["encryption", "audit_logging"],
            metadata={
                "regulatory_requirements": ["HIPAA", "GDPR", "HITECH"],
                "certification_level": "healthcare_grade"
            }
        )
        
        # Clinical Data Models
        self.components[ComponentType.DATA_MODEL.value] = DomainComponent(
            component_type=ComponentType.DATA_MODEL,
            priority=2,
            config={
                "primary_entities": [
                    "Patient", "Case", "Diagnosis", "Treatment", "Procedure", 
                    "Medication", "Allergy", "Vital", "LabResult", "Imaging"
                ],
                "data_standards": ["HL7_FHIR", "ICD10", "CPT", "SNOMED_CT", "LOINC"],
                "encryption_fields": [
                    "patient.ssn", "patient.dob", "patient.address", 
                    "case.notes", "diagnosis.details", "treatment.notes"
                ],
                "anonymization_rules": {
                    "patient_id": "hash_with_salt",
                    "dates": "shift_by_random_days",
                    "location": "zip_code_truncation",
                    "notes": "phi_redaction"
                },
                "retention_policies": {
                    "active_cases": "indefinite",
                    "completed_cases": "7_years",
                    "research_data": "25_years",
                    "audit_logs": "6_years"
                }
            },
            dependencies=["encryption", "compliance"],
            metadata={
                "interoperability_standards": ["HL7_FHIR_R4", "DICOM"],
                "clinical_terminologies": ["ICD10", "SNOMED_CT", "LOINC", "CPT"]
            }
        )
        
        # Clinical Decision Engine
        self.components[ComponentType.DECISION_ENGINE.value] = DomainComponent(
            component_type=ComponentType.DECISION_ENGINE,
            priority=3,
            config={
                "engine_types": ["ADCI", "Clinical_Guidelines", "Risk_Assessment", "Drug_Interaction"],
                "confidence_thresholds": {
                    "diagnosis": 0.85,
                    "treatment_recommendation": 0.80,
                    "drug_interaction": 0.95,
                    "risk_assessment": 0.75
                },
                "clinical_protocols": {
                    "gastric_cancer": {
                        "staging_protocol": "TNM_8th_edition",
                        "treatment_guidelines": "NCCN_2024",
                        "follow_up_schedule": "standard_oncology"
                    },
                    "emergency_protocols": {
                        "sepsis": "sepsis_3_criteria",
                        "stroke": "NIHSS_protocol",
                        "cardiac_arrest": "AHA_guidelines"
                    }
                },
                "evidence_sources": [
                    "PubMed", "Cochrane", "ClinicalTrials.gov", 
                    "NCCN_Guidelines", "WHO_Guidelines"
                ],
                "quality_metrics": {
                    "sensitivity": 0.90,
                    "specificity": 0.85,
                    "positive_predictive_value": 0.80,
                    "negative_predictive_value": 0.92
                }
            },
            dependencies=["data_model", "compliance"],
            metadata={
                "clinical_validation": "FDA_510k_pathway",
                "evidence_level": "systematic_review"
            }
        )
        
        # Healthcare Workflow Management
        self.components[ComponentType.WORKFLOW.value] = DomainComponent(
            component_type=ComponentType.WORKFLOW,
            priority=4,
            config={
                "workflow_types": [
                    "Patient_Admission", "Diagnostic_Workflow", "Treatment_Planning",
                    "Surgical_Workflow", "Medication_Management", "Discharge_Planning"
                ],
                "approval_workflows": {
                    "high_risk_medications": ["attending_physician", "pharmacist"],
                    "surgical_procedures": ["surgeon", "anesthesiologist", "nurse_manager"],
                    "research_enrollment": ["principal_investigator", "irb_approval"]
                },
                "automation_rules": {
                    "lab_result_alerts": True,
                    "medication_reminders": True,
                    "appointment_scheduling": True,
                    "insurance_verification": True
                },
                "escalation_policies": {
                    "critical_lab_values": "immediate_notification",
                    "medication_allergies": "block_and_alert",
                    "missing_documentation": "24_hour_reminder"
                }
            },
            dependencies=["authentication", "data_model"],
            metadata={
                "workflow_standards": ["BPMN_2.0", "HL7_Workflow"],
                "integration_points": ["EHR", "Laboratory", "Pharmacy", "Radiology"]
            }
        )
        
        # Healthcare Compliance and Audit
        self.components[ComponentType.COMPLIANCE.value] = DomainComponent(
            component_type=ComponentType.COMPLIANCE,
            priority=1,  # High priority for healthcare
            config={
                "regulatory_frameworks": ["HIPAA", "GDPR", "HITECH", "FDA_21_CFR_Part_11"],
                "audit_requirements": {
                    "patient_access": "all_events",
                    "data_modifications": "before_after_values",
                    "system_access": "login_logout_events",
                    "export_operations": "full_audit_trail",
                    "emergency_access": "break_glass_logging"
                },
                "data_protection": {
                    "encryption_at_rest": "AES_256",
                    "encryption_in_transit": "TLS_1.3",
                    "key_management": "HSM_backed",
                    "data_masking": "dynamic_masking",
                    "backup_encryption": True
                },
                "privacy_controls": {
                    "minimum_necessary": True,
                    "purpose_limitation": True,
                    "consent_management": True,
                    "right_to_be_forgotten": "limited_healthcare_context",
                    "data_portability": "HL7_FHIR_format"
                },
                "breach_notification": {
                    "detection_threshold": "any_unauthorized_access",
                    "notification_timeline": "72_hours",
                    "affected_parties": ["patients", "regulators", "law_enforcement"],
                    "mitigation_procedures": "incident_response_plan"
                }
            },
            dependencies=["encryption", "audit_logging"],
            metadata={
                "compliance_certifications": ["SOC_2_Type_II", "HITRUST", "FedRAMP"],
                "regular_audits": ["annual_hipaa_assessment", "quarterly_security_review"]
            }
        )
        
        # Healthcare Reporting and Analytics
        self.components[ComponentType.REPORTING.value] = DomainComponent(
            component_type=ComponentType.REPORTING,
            priority=5,
            config={
                "report_types": [
                    "Clinical_Quality_Measures", "Outcome_Analytics", "Research_Reports",
                    "Regulatory_Reports", "Financial_Reports", "Operational_Dashboards"
                ],
                "quality_measures": {
                    "cms_measures": ["CMS_156", "CMS_165", "CMS_177"],
                    "joint_commission": ["ORYX_measures", "Patient_Safety_Goals"],
                    "custom_measures": ["infection_rates", "readmission_rates", "mortality_rates"]
                },
                "anonymization_for_research": {
                    "safe_harbor_method": True,
                    "statistical_disclosure_control": True,
                    "k_anonymity": 5,
                    "l_diversity": 3
                },
                "real_time_dashboards": {
                    "clinical_metrics": ["patient_census", "acuity_levels", "resource_utilization"],
                    "quality_metrics": ["infection_rates", "patient_satisfaction", "length_of_stay"],
                    "financial_metrics": ["revenue_cycle", "cost_per_case", "payer_mix"]
                }
            },
            dependencies=["data_model", "compliance"],
            metadata={
                "reporting_standards": ["HL7_CDA", "FHIR_Measure", "QRDA"],
                "visualization_tools": ["clinical_dashboards", "research_analytics"]
            }
        )
        
        # Healthcare UI Components
        self.components[ComponentType.UI_COMPONENTS.value] = DomainComponent(
            component_type=ComponentType.UI_COMPONENTS,
            priority=6,
            config={
                "specialized_components": [
                    "Patient_Summary", "Clinical_Timeline", "Medication_List",
                    "Vital_Signs_Chart", "Lab_Results_Grid", "Imaging_Viewer",
                    "Decision_Support_Alerts", "Clinical_Documentation"
                ],
                "accessibility_requirements": {
                    "wcag_level": "AA",
                    "keyboard_navigation": True,
                    "screen_reader_support": True,
                    "high_contrast_mode": True,
                    "font_size_adjustable": True
                },
                "clinical_workflows_ui": {
                    "admission_forms": "structured_data_entry",
                    "progress_notes": "template_based",
                    "order_entry": "computerized_provider_order_entry",
                    "medication_administration": "barcode_scanning"
                },
                "mobile_optimization": {
                    "responsive_design": True,
                    "offline_capability": True,
                    "touch_friendly": True,
                    "voice_input": "clinical_voice_recognition"
                }
            },
            dependencies=["authentication", "workflow"],
            metadata={
                "usability_standards": ["ISO_9241", "IEC_62304", "FDA_Human_Factors"],
                "clinical_workflow_optimization": True
            }
        )
        
        # Healthcare System Integrations
        self.components[ComponentType.INTEGRATIONS.value] = DomainComponent(
            component_type=ComponentType.INTEGRATIONS,
            priority=7,
            config={
                "standard_protocols": ["HL7_v2", "HL7_FHIR", "DICOM", "IHE_profiles"],
                "integration_types": {
                    "ehr_systems": ["Epic", "Cerner", "Allscripts", "Athenahealth"],
                    "laboratory_systems": ["Cerner_Millennium", "Epic_Beaker", "Sunquest"],
                    "imaging_systems": ["GE_Centricity", "Philips_IntelliSpace", "Agfa_IMPAX"],
                    "pharmacy_systems": ["Epic_Willow", "Cerner_PharmNet", "Omnicell"]
                },
                "data_exchange_formats": {
                    "clinical_data": "HL7_FHIR_R4",
                    "imaging_data": "DICOM_3.0",
                    "laboratory_data": "HL7_v2.5.1",
                    "pharmacy_data": "NCPDP_SCRIPT"
                },
                "real_time_interfaces": {
                    "adt_feed": "HL7_ADT_messages",
                    "lab_results": "HL7_ORU_messages",
                    "medication_orders": "HL7_RDE_messages",
                    "clinical_alerts": "real_time_notifications"
                },
                "batch_processing": {
                    "bulk_data_export": "HL7_FHIR_Bulk_Data",
                    "research_data_sets": "de_identified_exports",
                    "backup_procedures": "incremental_and_full"
                }
            },
            dependencies=["data_model", "compliance"],
            metadata={
                "interoperability_certifications": ["ONC_Health_IT", "DirectTrust"],
                "integration_testing": "comprehensive_hl7_validation"
            }
        )
