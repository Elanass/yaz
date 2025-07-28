# Domain Configuration System

The Gastric ADCI Platform includes a comprehensive domain configuration system that adapts the platform components to different industries and use cases.

## Supported Domains

### 🏥 Healthcare
- **Primary Use Case**: Clinical decision support, patient management, EHR integration
- **Compliance**: HIPAA, GDPR, HITECH, FDA regulations
- **Key Components**: ADCI decision engine, clinical workflows, patient data encryption
- **Integrations**: Epic, Cerner, Allscripts, HL7 FHIR

### 🚛 Logistics
- **Primary Use Case**: Supply chain management, transportation optimization, warehouse operations
- **Compliance**: DOT, OSHA, customs regulations
- **Key Components**: Route optimization, inventory management, tracking systems
- **Integrations**: SAP TM, Oracle OTM, Manhattan WMS, carrier APIs

### 🛡️ Insurance
- **Primary Use Case**: Policy administration, claims processing, underwriting, fraud detection
- **Compliance**: State insurance regulations, SOX, anti-fraud measures
- **Key Components**: Policy lifecycle, claims workflows, risk assessment
- **Integrations**: Guidewire, Duck Creek, ACORD forms, credit bureaus

### 🎓 Education
- **Primary Use Case**: Student information systems, learning analytics, academic planning
- **Compliance**: FERPA, COPPA, accessibility requirements
- **Key Components**: Learning analytics, intervention systems, academic workflows
- **Integrations**: PowerSchool, Canvas, state assessment systems

## Architecture

### Domain Configuration Factory
```python
from core.config.domains.manager import DomainConfigurationFactory, DomainType

# Create domain-specific configuration
healthcare_config = DomainConfigurationFactory.create_domain_config(DomainType.HEALTHCARE)
logistics_config = DomainConfigurationFactory.create_domain_config(DomainType.LOGISTICS)
```

### Domain Manager
```python
from core.config.domains.manager import DomainManager, initialize_domain

# Initialize domain
domain_manager = initialize_domain(DomainType.HEALTHCARE)

# Get domain-specific configurations
auth_config = domain_manager.get_authentication_config()
compliance_config = domain_manager.get_compliance_config()
middleware_stack = domain_manager.adapt_middleware_stack()
```

### Component Types
Each domain configures these component types:
- **Authentication**: Role-based access, MFA requirements, session management
- **Data Model**: Entity definitions, standards compliance, encryption rules
- **Decision Engine**: AI/ML algorithms, confidence thresholds, validation rules
- **Workflow**: Business processes, approval chains, automation rules
- **Compliance**: Regulatory frameworks, audit requirements, data governance
- **Reporting**: KPIs, dashboards, regulatory reports
- **UI Components**: Domain-specific interfaces, accessibility features
- **Integrations**: External systems, data formats, communication protocols

## Closed Source Adapters

### Healthcare Systems
- **Epic EHR**: MyChart, Hyperspace integration with OAuth 2.0 + JWT
- **Cerner**: PowerChart/HealtheLife with FHIR R4 APIs
- **Allscripts**: Sunrise/Professional EHR with proprietary APIs

### Logistics Systems
- **SAP Transportation Management**: RFC/REST integration with NetWeaver
- **Oracle OTM**: Web services and batch processing
- **Manhattan WMS**: Real-time inventory and warehouse operations

### Insurance Systems
- **Guidewire PolicyCenter**: Policy administration and underwriting
- **Guidewire ClaimCenter**: Claims processing and adjudication
- **Duck Creek**: Multi-line insurance platform
- **ACORD Forms**: Standardized insurance form processing

## Configuration Examples

### Healthcare Domain
```python
# Authentication with HIPAA compliance
{
    "require_mfa": True,
    "session_timeout_minutes": 30,
    "audit_all_access": True,
    "roles": ["physician", "nurse", "admin", "researcher"],
    "compliance_features": {
        "hipaa_logging": True,
        "break_glass_access": True,
        "minimum_necessary_rule": True
    }
}

# Data model with clinical standards
{
    "primary_entities": ["Patient", "Case", "Diagnosis", "Treatment"],
    "data_standards": ["HL7_FHIR", "ICD10", "SNOMED_CT"],
    "encryption_fields": ["patient.ssn", "case.notes"],
    "retention_policies": {
        "active_cases": "indefinite",
        "completed_cases": "7_years"
    }
}
```

### Logistics Domain
```python
# Route optimization configuration
{
    "optimization_algorithms": ["Route_Optimization", "Load_Planning"],
    "routing_parameters": {
        "distance_optimization": True,
        "traffic_consideration": True,
        "vehicle_capacity_constraints": True
    },
    "performance_kpis": {
        "on_time_delivery": 0.95,
        "cost_per_mile": "minimize"
    }
}
```

## Environment Configuration

Set the domain type using environment variables:

```bash
# Healthcare (default)
DOMAIN_TYPE=healthcare

# Logistics
DOMAIN_TYPE=logistics

# Insurance  
DOMAIN_TYPE=insurance

# Education
DOMAIN_TYPE=education
```

### Closed Source System Configuration

```bash
# Epic EHR
EPIC_BASE_URL=https://fhir.epic.com/interconnect-fhir-oauth
EPIC_CLIENT_ID=your_client_id
EPIC_PRIVATE_KEY=path/to/private_key.pem

# SAP Transportation Management
SAP_TM_HOST=sap-tm-server.company.com
SAP_TM_CLIENT=100
SAP_TM_USERNAME=integration_user
SAP_TM_PASSWORD=secure_password

# Guidewire PolicyCenter
GUIDEWIRE_PC_URL=https://pc.company.com/pc
GUIDEWIRE_PC_USERNAME=api_user
GUIDEWIRE_PC_PASSWORD=secure_password
```

## Usage Examples

### Initialize Platform for Healthcare
```python
from core.config.domains.manager import initialize_domain, DomainType

# Initialize healthcare domain
domain_manager = initialize_domain(DomainType.HEALTHCARE)

# Validate configuration
issues = domain_manager.validate_configuration()
if not issues:
    print("Healthcare domain ready for HIPAA-compliant operations")
```

### Connect to Epic EHR
```python
from adapters.closed_source import get_closed_source_adapter

# Get Epic adapter
epic_adapter = get_closed_source_adapter("epic")

# Authenticate
await epic_adapter.authenticate({
    "client_id": "your_client_id",
    "private_key": "path/to/key.pem"
})

# Retrieve patient data
patient_data = await epic_adapter.get_patient_data("patient_123")
```

### Switch to Logistics Domain
```python
# Initialize logistics domain
domain_manager = initialize_domain(DomainType.LOGISTICS)

# Get SAP TM adapter
sap_adapter = get_logistics_adapter("sap_tm")

# Create shipment
shipment_id = await sap_adapter.create_case({
    "origin": "Warehouse A",
    "destination": "Customer B",
    "weight": 1500.0
})
```

## Testing

Run the domain system tests:

```bash
python test_domain_system.py
```

This will test:
- Domain configuration creation
- Component validation
- Closed source adapter connectivity
- Middleware stack adaptation
- Configuration export/import

## Security Considerations

1. **Encryption**: All sensitive data is encrypted using domain-appropriate algorithms
2. **Access Control**: Role-based permissions adapted to domain requirements
3. **Audit Logging**: Comprehensive audit trails for compliance
4. **Data Retention**: Domain-specific retention policies
5. **API Security**: Secure integration with closed source systems

## Extending the System

### Adding New Domains
1. Create domain configuration class inheriting from `DomainConfiguration`
2. Implement `_initialize_components()` method
3. Register with `DomainConfigurationFactory`
4. Add validation rules to `DomainManager`

### Adding New Adapters
1. Create adapter class inheriting from `ClosedSourceAdapter`
2. Implement authentication and data exchange methods
3. Add configuration parameters to `platform_config.py`
4. Register in appropriate adapter registry

### Custom Components
1. Define component in domain configuration
2. Add component type to `ComponentType` enum
3. Implement component-specific logic
4. Add to middleware stack if needed
