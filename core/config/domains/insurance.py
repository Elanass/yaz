"""
Insurance Domain Configuration

Specialized configuration for insurance applications including claims processing,
underwriting, and regulatory compliance.
"""

from typing import Dict, Any
from core.config.domains import DomainConfiguration, DomainComponent, DomainType, ComponentType


class InsuranceDomainConfig(DomainConfiguration):
    """Insurance-specific platform configuration"""
    
    def __init__(self):
        super().__init__(DomainType.INSURANCE)
    
    def _initialize_components(self):
        """Initialize insurance-specific components"""
        
        # Authentication for insurance operations
        self.components[ComponentType.AUTHENTICATION.value] = DomainComponent(
            component_type=ComponentType.AUTHENTICATION,
            priority=1,
            config={
                "require_mfa": True,
                "session_timeout_minutes": 60,
                "password_complexity": "high",
                "audit_all_access": True,
                "role_based_access": True,
                "roles": ["underwriter", "claims_adjuster", "agent", "actuary", "admin", "customer"],
                "permissions": {
                    "underwriter": ["read:applications", "write:underwriting_decisions", "access:risk_models"],
                    "claims_adjuster": ["read:claims", "write:claim_decisions", "access:investigation_tools"],
                    "agent": ["read:customer_data", "write:applications", "view:commission_reports"],
                    "actuary": ["read:all_data", "access:statistical_models", "export:actuarial_data"],
                    "admin": ["admin:users", "admin:system", "read:audit_logs"],
                    "customer": ["read:own_policies", "submit:claims", "view:claim_status"]
                },
                "regulatory_compliance": {
                    "know_your_customer": True,
                    "anti_money_laundering": True,
                    "data_privacy": True,
                    "audit_logging": True
                }
            },
            dependencies=["encryption", "audit_logging"],
            metadata={
                "regulatory_requirements": ["SOX", "GDPR", "CCPA", "State_Insurance_Regulations"],
                "fraud_prevention": "multi_layer_security"
            }
        )
        
        # Insurance Data Models
        self.components[ComponentType.DATA_MODEL.value] = DomainComponent(
            component_type=ComponentType.DATA_MODEL,
            priority=2,
            config={
                "primary_entities": [
                    "Policy", "Claim", "Customer", "Application", "Premium", "Agent",
                    "Underwriting_Decision", "Risk_Assessment", "Actuarial_Data", "Reinsurance"
                ],
                "insurance_standards": ["ACORD", "ISO", "NAIC", "EIOPA_Solvency_II"],
                "data_classification": {
                    "public": ["product_information", "company_information"],
                    "internal": ["agent_performance", "operational_metrics"],
                    "confidential": ["customer_pii", "financial_data", "medical_information"],
                    "restricted": ["underwriting_models", "pricing_algorithms", "fraud_patterns"]
                },
                "encryption_requirements": {
                    "customer_pii": "AES_256",
                    "financial_data": "AES_256",
                    "medical_information": "AES_256_with_additional_controls",
                    "payment_information": "PCI_DSS_compliant"
                },
                "retention_policies": {
                    "active_policies": "policy_term_plus_statute_of_limitations",
                    "claims_data": "7_years_after_settlement",
                    "underwriting_data": "regulatory_requirement_based",
                    "financial_records": "7_years",
                    "audit_logs": "regulatory_requirement_based"
                }
            },
            dependencies=["encryption", "compliance"],
            metadata={
                "data_standards": ["ACORD_XML", "ISO_20022", "XBRL"],
                "interoperability": "cross_carrier_data_exchange"
            }
        )
        
        # Insurance Decision Engine
        self.components[ComponentType.DECISION_ENGINE.value] = DomainComponent(
            component_type=ComponentType.DECISION_ENGINE,
            priority=3,
            config={
                "decision_types": [
                    "Underwriting_Automation", "Claims_Processing", "Fraud_Detection",
                    "Pricing_Optimization", "Risk_Assessment", "Reinsurance_Decisions"
                ],
                "underwriting_rules": {
                    "auto_approve_criteria": "low_risk_standard_products",
                    "auto_decline_criteria": "high_risk_exclusions",
                    "referral_criteria": "manual_underwriter_review",
                    "medical_requirements": "age_and_coverage_based",
                    "financial_requirements": "income_verification_thresholds"
                },
                "claims_processing": {
                    "auto_adjudication": "simple_claims_within_parameters",
                    "fraud_scoring": "ml_based_fraud_detection",
                    "settlement_authority": "dollar_amount_based_approval_levels",
                    "investigation_triggers": "suspicious_pattern_detection"
                },
                "risk_models": {
                    "actuarial_models": "statistical_life_tables_and_morbidity",
                    "catastrophe_models": "natural_disaster_risk_assessment",
                    "credit_models": "financial_stability_assessment",
                    "behavioral_models": "customer_interaction_patterns"
                },
                "regulatory_constraints": {
                    "fair_lending": "anti_discrimination_controls",
                    "rate_approval": "state_regulatory_compliance",
                    "reserve_requirements": "actuarial_reserve_calculations",
                    "solvency_requirements": "capital_adequacy_monitoring"
                }
            },
            dependencies=["data_model", "compliance"],
            metadata={
                "model_validation": "independent_validation_required",
                "explainable_ai": "regulatory_transparency_requirements"
            }
        )
        
        # Insurance Workflow Management
        self.components[ComponentType.WORKFLOW.value] = DomainComponent(
            component_type=ComponentType.WORKFLOW,
            priority=4,
            config={
                "workflow_types": [
                    "Application_Processing", "Underwriting_Workflow", "Claims_Lifecycle",
                    "Policy_Administration", "Premium_Billing", "Customer_Service"
                ],
                "application_workflow": {
                    "data_collection": "progressive_application_forms",
                    "verification": "third_party_data_validation",
                    "underwriting": "automated_and_manual_review",
                    "approval": "multi_level_approval_process",
                    "policy_issuance": "automated_policy_generation"
                },
                "claims_workflow": {
                    "first_notice_of_loss": "24_7_claim_reporting",
                    "claim_assignment": "automated_adjuster_assignment",
                    "investigation": "fraud_and_liability_investigation",
                    "evaluation": "damage_assessment_and_valuation",
                    "settlement": "payment_processing_and_closure"
                },
                "escalation_procedures": {
                    "high_value_claims": "senior_adjuster_review",
                    "fraud_suspicion": "special_investigation_unit",
                    "customer_complaints": "ombudsman_escalation",
                    "regulatory_issues": "compliance_team_notification"
                },
                "automation_rules": {
                    "premium_calculation": "rating_engine_automation",
                    "policy_renewals": "automated_renewal_processing",
                    "claim_payments": "automated_payment_processing",
                    "regulatory_reporting": "automated_report_generation"
                }
            },
            dependencies=["authentication", "data_model", "decision_engine"],
            metadata={
                "process_optimization": "lean_six_sigma_principles",
                "customer_experience": "omnichannel_service_delivery"
            }
        )
        
        # Insurance Compliance and Audit
        self.components[ComponentType.COMPLIANCE.value] = DomainComponent(
            component_type=ComponentType.COMPLIANCE,
            priority=1,  # Critical for insurance
            config={
                "regulatory_frameworks": [
                    "State_Insurance_Codes", "NAIC_Model_Laws", "SOX", "GDPR", 
                    "CCPA", "HIPAA", "Fair_Credit_Reporting_Act"
                ],
                "financial_reporting": {
                    "statutory_accounting": "SAP_principles",
                    "gaap_reporting": "US_GAAP_standards",
                    "solvency_reporting": "risk_based_capital_requirements",
                    "regulatory_filings": "quarterly_and_annual_statements"
                },
                "consumer_protection": {
                    "fair_dealing": "treating_customers_fairly",
                    "transparency": "clear_policy_terms_and_conditions",
                    "privacy": "customer_data_protection",
                    "complaints_handling": "regulatory_complaint_procedures"
                },
                "market_conduct": {
                    "sales_practices": "agent_licensing_and_training",
                    "advertising": "truthful_and_non_misleading",
                    "underwriting": "fair_and_non_discriminatory",
                    "claims_handling": "prompt_and_fair_settlement"
                },
                "anti_fraud_measures": {
                    "fraud_detection": "advanced_analytics_and_investigation",
                    "fraud_reporting": "regulatory_and_law_enforcement_coordination",
                    "fraud_prevention": "customer_education_and_system_controls",
                    "recovery_efforts": "subrogation_and_restitution"
                }
            },
            dependencies=["audit_logging", "encryption"],
            metadata={
                "compliance_monitoring": "continuous_compliance_assessment",
                "regulatory_relationships": "proactive_regulator_engagement"
            }
        )
        
        # Insurance Reporting and Analytics
        self.components[ComponentType.REPORTING.value] = DomainComponent(
            component_type=ComponentType.REPORTING,
            priority=5,
            config={
                "report_types": [
                    "Financial_Statements", "Regulatory_Reports", "Actuarial_Reports",
                    "Claims_Analytics", "Underwriting_Performance", "Customer_Analytics"
                ],
                "financial_metrics": {
                    "profitability": ["loss_ratio", "expense_ratio", "combined_ratio", "roe"],
                    "growth": ["premium_growth", "policy_count_growth", "market_share"],
                    "efficiency": ["cost_per_policy", "claims_processing_time", "customer_acquisition_cost"],
                    "risk": ["risk_based_capital_ratio", "concentration_risk", "catastrophe_exposure"]
                },
                "operational_kpis": {
                    "underwriting": ["application_processing_time", "auto_approval_rate", "decline_rate"],
                    "claims": ["claim_processing_time", "first_call_resolution", "customer_satisfaction"],
                    "customer_service": ["response_time", "issue_resolution_rate", "nps_score"],
                    "sales": ["conversion_rate", "policy_retention", "cross_sell_success"]
                },
                "regulatory_reporting": {
                    "statutory_filings": "quarterly_and_annual_statements",
                    "market_conduct_reports": "examination_and_surveillance_reports",
                    "financial_condition_reports": "own_risk_and_solvency_assessment",
                    "consumer_complaint_reports": "complaint_ratio_and_resolution_metrics"
                },
                "predictive_analytics": {
                    "customer_lifetime_value": "retention_and_profitability_modeling",
                    "churn_prediction": "early_warning_indicators",
                    "cross_sell_opportunities": "propensity_modeling",
                    "catastrophe_modeling": "natural_disaster_impact_assessment"
                }
            },
            dependencies=["data_model", "compliance"],
            metadata={
                "reporting_standards": ["GAAP", "SAP", "IFRS", "Solvency_II"],
                "data_quality": "regulatory_grade_accuracy"
            }
        )
        
        # Insurance UI Components
        self.components[ComponentType.UI_COMPONENTS.value] = DomainComponent(
            component_type=ComponentType.UI_COMPONENTS,
            priority=6,
            config={
                "specialized_components": [
                    "Policy_Management", "Claims_Dashboard", "Underwriting_Workbench",
                    "Customer_Portal", "Agent_Desktop", "Actuarial_Workspace",
                    "Risk_Assessment_Tools", "Fraud_Investigation_Console"
                ],
                "customer_interfaces": {
                    "self_service_portal": ["policy_information", "claim_submission", "payment_management"],
                    "mobile_app": ["policy_access", "claim_photos", "agent_contact"],
                    "web_application": ["quote_and_buy", "policy_changes", "document_access"],
                    "chatbot_integration": ["customer_support", "faq_assistance", "claim_reporting"]
                },
                "agent_tools": {
                    "sales_workbench": ["lead_management", "quote_generation", "application_submission"],
                    "customer_management": ["policy_portfolio", "renewal_management", "cross_sell_opportunities"],
                    "commission_tracking": ["sales_performance", "commission_statements", "goal_tracking"],
                    "training_materials": ["product_information", "sales_tools", "compliance_updates"]
                },
                "internal_applications": {
                    "underwriting_desktop": ["application_review", "risk_assessment", "decision_support"],
                    "claims_adjuster_tools": ["claim_details", "investigation_notes", "settlement_calculator"],
                    "actuarial_workstation": ["data_analysis", "model_development", "pricing_tools"],
                    "compliance_dashboard": ["regulatory_calendar", "filing_status", "audit_findings"]
                }
            },
            dependencies=["authentication", "workflow"],
            metadata={
                "user_experience": "role_based_optimization",
                "accessibility": "ada_compliance_required"
            }
        )
        
        # Insurance System Integrations
        self.components[ComponentType.INTEGRATIONS.value] = DomainComponent(
            component_type=ComponentType.INTEGRATIONS,
            priority=7,
            config={
                "core_systems": {
                    "policy_administration": ["Guidewire_PolicyCenter", "Duck_Creek_Policy", "VPAS"],
                    "claims_management": ["Guidewire_ClaimCenter", "Duck_Creek_Claims", "Mitchell"],
                    "billing_systems": ["Guidewire_BillingCenter", "Duck_Creek_Billing", "Instec"],
                    "rating_engines": ["Earnix", "Towers_Watson", "Custom_Rating_Systems"]
                },
                "external_data_sources": {
                    "credit_bureaus": ["Experian", "Equifax", "TransUnion"],
                    "motor_vehicle_records": ["LexisNexis", "Verisk", "State_DMV_Systems"],
                    "medical_information": ["MIB", "Milliman_IntelliScript", "Rx_History"],
                    "property_data": ["CoreLogic", "RealtyTrac", "Zillow_API"]
                },
                "regulatory_systems": {
                    "filing_systems": ["SERFF", "State_Filing_Systems", "NAIC_Systems"],
                    "licensing_verification": ["NIPR", "State_Licensing_Systems"],
                    "fraud_databases": ["NICB", "ISO_ClaimSearch", "State_Fraud_Bureaus"],
                    "compliance_monitoring": ["Thomson_Reuters", "Compliance_Software"]
                },
                "financial_systems": {
                    "accounting_systems": ["SAP", "Oracle_Financials", "QuickBooks_Enterprise"],
                    "investment_management": ["BlackRock_Aladdin", "State_Street", "BNY_Mellon"],
                    "reinsurance_systems": ["RMS", "AIR_Worldwide", "Guy_Carpenter_Systems"],
                    "payment_processing": ["ACH_Networks", "Wire_Transfer_Systems", "Payment_Gateways"]
                }
            },
            dependencies=["data_model", "compliance"],
            metadata={
                "integration_standards": ["ACORD", "ISO_20022", "HL7_for_medical"],
                "data_security": "end_to_end_encryption_required"
            }
        )
