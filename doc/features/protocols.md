# Protocols Feature

## Overview
The Protocols feature manages clinical protocols, compliance tracking, and deviation reporting for surgical procedures, with specific support for FLOT protocol analysis.

## Components

### ProtocolService (`service.py`)
Core protocol management service that handles protocol versioning, compliance, and reporting.

**Key Methods**:
- `create_protocol()` - Creates new clinical protocols
- `validate_compliance()` - Checks protocol compliance
- `track_deviations()` - Monitors protocol deviations
- `generate_reports()` - Creates compliance reports

### FLOT Analyzer (`flot_analyzer.py`)
Specialized analyzer for FLOT (Fluorouracil, Leucovorin, Oxaliplatin, Docetaxel) protocol compliance and effectiveness.

**Key Features**:
- FLOT protocol validation
- Compliance scoring
- Deviation detection
- Outcome correlation

## Protocol Management

### Protocol Types
- **ADCI**: Adaptive Decision Confidence Index protocols
- **Gastrectomy**: Surgical procedure protocols
- **FLOT**: Perioperative chemotherapy protocols
- **Custom**: User-defined protocols

### Protocol Lifecycle
1. **Draft**: Initial protocol creation
2. **Review**: Peer review and validation
3. **Approved**: Approved for clinical use
4. **Active**: Currently in use
5. **Deprecated**: No longer recommended
6. **Archived**: Historical record

### Compliance Tracking
- Real-time deviation monitoring
- Automated compliance scoring
- Alert generation for critical deviations
- Trend analysis and reporting

## Usage Examples

```python
from feature.protocols import ProtocolService, FLOTAnalyzer

# Initialize services
protocol_service = ProtocolService()
flot_analyzer = FLOTAnalyzer()

# Create a new protocol
protocol = await protocol_service.create_protocol(
    name="FLOT-4 Modified",
    type="flot",
    version="1.0"
)

# Check compliance
compliance = await protocol_service.validate_compliance(
    protocol_id=protocol.id,
    patient_data=patient_data
)

# Analyze FLOT adherence
analysis = await flot_analyzer.analyze_adherence(patient_data)
```

## FLOT Protocol Specifics

### Protocol Components
- **Fluorouracil**: 2600 mg/m² continuous infusion
- **Leucovorin**: 200 mg/m² before fluorouracil
- **Oxaliplatin**: 85 mg/m² day 1
- **Docetaxel**: 50 mg/m² day 1

### Monitoring Parameters
- Dosage compliance
- Timing adherence
- Cycle completion rates
- Toxicity management
- Response assessment

## API Endpoints

- `POST /api/v1/protocols/create` - Create new protocol
- `GET /api/v1/protocols/{protocol_id}` - Get protocol details
- `POST /api/v1/protocols/{protocol_id}/validate` - Validate compliance
- `GET /api/v1/protocols/deviations` - Get deviation reports
- `POST /api/v1/protocols/flot/analyze` - FLOT-specific analysis

## Configuration

```python
# Protocol settings
COMPLIANCE_THRESHOLD=0.95
DEVIATION_ALERT_LEVEL="major"
PROTOCOL_VERSION_RETENTION=5
FLOT_CYCLE_DURATION_DAYS=14
```

## Testing
Tests located in `test/unit/protocols/`

## Dependencies
- pandas (data analysis)
- numpy (numerical computing)
- datetime (temporal operations)
