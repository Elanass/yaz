# YAZ Operators - Reorganized Architecture

## Overview

The YAZ Surgery Analytics Platform operators have been reorganized into a clean, modular architecture that separates **general-purpose** functionality from **specific-purpose** domain logic. This reorganization improves maintainability, testability, and extensibility.

## Architecture

```
core/operators/
├── general_purpose/           # Cross-domain functionality
│   ├── core_operations.py     # Core business operations
│   ├── financial_operations.py # Financial transactions & billing
│   ├── communication_operations.py # Messaging & notifications
│   ├── infrastructure_operations.py # System health & monitoring
│   ├── security_operations.py # Access control & threat detection
│   ├── monitoring_operations.py # Metrics & alerting
│   ├── integration_operations.py # External API integrations
│   └── data_sync_operations.py # Data synchronization
│
└── specific_purpose/          # Domain-specific functionality
    ├── healthcare_operations.py # Healthcare workflows
    ├── surgery_operations.py   # Surgical procedures
    ├── patient_management_operations.py # Patient registration & care
    ├── education_operations.py # Medical education & training
    ├── hospitality_operations.py # Patient experience & accommodation
    ├── insurance_operations.py # Insurance claims & coverage
    └── logistics_operations.py # Supply chain & equipment
```

## General Purpose Operators

These operators provide cross-domain functionality that can be used across different business domains:

### CoreOperationsOperator
- Operation logging and tracking
- Audit trail management
- Performance metrics collection
- Data validation utilities
- ID generation

### FinancialOperationsOperator
- Transaction management
- Invoice generation
- Payment processing
- Revenue analytics
- Financial reporting

### CommunicationOperationsOperator
- Multi-channel messaging (email, SMS, push notifications)
- Template-based communications
- Delivery tracking and statistics
- Communication history management

### InfrastructureOperationsOperator
- System metrics collection
- Health checks and monitoring
- Alert management
- Infrastructure health scoring

### SecurityOperationsOperator
- Security event logging
- Access control validation
- Threat detection
- Brute force protection
- Secure token generation

### MonitoringOperationsOperator
- Custom metric definitions
- Alert rule management
- Dashboard creation
- Performance monitoring
- Custom monitors

### IntegrationOperationsOperator
- External API management
- Rate limiting
- Webhook handling
- Integration statistics

### DataSyncOperationsOperator
- Data synchronization between systems
- Conflict detection and resolution
- Sync job management
- Data integrity checking

## Specific Purpose Operators

These operators handle domain-specific business logic:

### HealthcareOperationsOperator
- Surgical case creation
- Surgery scheduling
- Case status management
- Clinical workflows

### SurgeryOperationsOperator
- Surgery scheduling and management
- Operating room allocation
- Surgical team coordination
- Complication tracking
- Surgical metrics and analytics

### PatientManagementOperationsOperator
- Patient registration and demographics
- Visit management
- Care plan creation
- Patient alerts and notifications
- Patient search and summary

### EducationOperationsOperator
- Training program management
- Certification tracking
- Skill assessment
- Educational resource coordination

### HospitalityOperationsOperator
- Patient experience management
- Accommodation coordination
- Family support services
- Satisfaction tracking

### InsuranceOperationsOperator
- Claims processing
- Coverage verification
- Insurance billing

### LogisticsOperationsOperator
- Equipment management
- Supply chain coordination
- Resource scheduling

## Usage Examples

### Using General Purpose Operators

```python
from core.operators.general_purpose.core_operations import CoreOperationsOperator
from core.operators.general_purpose.financial_operations import FinancialOperationsOperator

# Core operations
core_ops = CoreOperationsOperator()
operation_id = core_ops.generate_operation_id("PAYMENT")

# Financial operations
financial_ops = FinancialOperationsOperator()
transaction = financial_ops.create_transaction({
    "amount": 1500.00,
    "transaction_type": "credit",
    "currency": "USD",
    "description": "Surgery payment",
    "user_id": "user123"
})
```

### Using Specific Purpose Operators

```python
from core.operators.specific_purpose.surgery_operations import SurgeryOperationsOperator
from core.operators.specific_purpose.patient_management_operations import PatientManagementOperationsOperator

# Surgery operations
surgery_ops = SurgeryOperationsOperator()
surgery = surgery_ops.schedule_surgery({
    "patient_id": "PAT-123",
    "procedure_name": "Laparoscopic Gastric Bypass",
    "surgeon_id": "DR-456",
    "scheduled_date": "2024-02-15T09:00:00Z"
})

# Patient management
patient_ops = PatientManagementOperationsOperator()
patient = patient_ops.register_patient({
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1980-05-15",
    "email": "john.doe@email.com"
})
```

## Benefits of the New Architecture

### 1. **Separation of Concerns**
- General-purpose operations are reusable across domains
- Domain-specific logic is isolated and focused
- Clear boundaries between different types of functionality

### 2. **Improved Maintainability**
- Smaller, focused modules are easier to understand and modify
- Changes to general functionality don't affect domain-specific code
- Better code organization and navigation

### 3. **Enhanced Testability**
- Each operator can be tested independently
- Mock dependencies more easily
- Better unit test coverage

### 4. **Better Scalability**
- Add new domains without modifying existing code
- Scale different components independently
- Easier to optimize specific functionality

### 5. **Cleaner Dependencies**
- General-purpose operators have minimal dependencies
- Domain-specific operators can depend on general-purpose ones
- Avoid circular dependencies

## Migration from Legacy Operators

The legacy operators have been moved to preserve functionality:

- `general.py` → `general_purpose/legacy_general.py`
- `financial.py` → `general_purpose/legacy_financial.py`
- `equity.py` → `general_purpose/legacy_equity.py`
- `branding.py` → `general_purpose/legacy_branding.py`
- `internals.py` → `general_purpose/legacy_internals.py`
- `externals.py` → `general_purpose/legacy_externals.py`

Domain-specific operators were renamed and enhanced:

- `healthcare.py` → `specific_purpose/healthcare_operations.py`
- `education.py` → `specific_purpose/education_operations.py`
- `hospitality.py` → `specific_purpose/hospitality_operations.py`
- `insurance.py` → `specific_purpose/insurance_operations.py`
- `logistics.py` → `specific_purpose/logistics_operations.py`

## Integration Points

### With API Layer
```python
# In API endpoints
from core.operators import (
    CoreOperationsOperator,
    SurgeryOperationsOperator,
    FinancialOperationsOperator
)

@app.post("/api/v1/surgery/schedule")
async def schedule_surgery(surgery_data: SurgeryRequest):
    surgery_ops = SurgeryOperationsOperator()
    financial_ops = FinancialOperationsOperator()
    
    # Schedule surgery
    surgery = surgery_ops.schedule_surgery(surgery_data.dict())
    
    # Create billing record
    invoice = financial_ops.create_invoice({
        "customer_id": surgery["patient_id"],
        "reference_id": surgery["surgery_id"],
        "reference_type": "surgery",
        "line_items": [{"description": "Surgery", "amount": 5000.00}]
    })
    
    return {"surgery": surgery, "invoice": invoice}
```

### With Background Tasks
```python
from core.operators.general_purpose.monitoring_operations import MonitoringOperationsOperator

# Monitor system metrics
monitoring_ops = MonitoringOperationsOperator()
monitoring_ops.record_metric("surgery_completion_rate", 95.5)
```

## Future Enhancements

### Planned Additions
1. **Data Analytics Operators** - Advanced analytics and reporting
2. **AI/ML Operations** - Machine learning model management
3. **Compliance Operations** - Regulatory compliance tracking
4. **Quality Assurance Operations** - Quality metrics and improvement

### Plugin Architecture
Consider implementing a plugin system for:
- Custom domain-specific operators
- Third-party integrations
- Custom business logic extensions

## Contributing

When adding new operators:

1. **Determine Category**: Is it general-purpose or specific-purpose?
2. **Follow Naming Convention**: `*OperationsOperator` for classes
3. **Include Comprehensive Logging**: Use the logger from `core.services.logger`
4. **Write Unit Tests**: Test each operator independently
5. **Document Public Methods**: Include docstrings with examples
6. **Handle Errors Gracefully**: Proper exception handling and logging

## Support

For questions or issues with the operator architecture:
- Review the operator documentation
- Check existing unit tests for usage examples
- Refer to the API integration patterns
