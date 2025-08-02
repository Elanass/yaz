# Decisions Feature

## Overview
The Decisions feature implements decision engines for surgical recommendations, particularly focusing on the ADCI (Adaptive Decision Confidence Index) framework for gastric cancer treatment.

## Components

### DecisionService (`service.py`)
Core decision service that orchestrates different decision engines.

**Key Methods**:
- `make_decision()` - Generates treatment recommendations
- `calculate_confidence()` - Computes decision confidence scores
- `get_decision_history()` - Retrieves historical decisions

### Base Decision Engine (`base_decision_engine.py`)
Abstract base class for all decision engines, providing common functionality.

**Base Features**:
- Input validation
- Result formatting
- Logging and auditing
- Error handling

### ADCI Engine (`adci_engine.py`)
Implements the Adaptive Decision Confidence Index framework for surgical decision support.

**Key Features**:
- Multi-factor decision analysis
- Confidence scoring algorithm
- Risk stratification
- Evidence-based recommendations

### Precision Engine (`precision_engine.py`)
High-precision decision engine for complex surgical scenarios.

**Capabilities**:
- Advanced statistical modeling
- Machine learning predictions
- Uncertainty quantification
- Sensitivity analysis

## Decision Framework

### ADCI Methodology
1. **Data Collection**: Patient demographics, medical history, imaging
2. **Risk Assessment**: Stratification based on multiple factors
3. **Confidence Calculation**: Statistical confidence in recommendations
4. **Decision Output**: Structured recommendation with supporting evidence

### Decision Factors
- Patient age and comorbidities
- Tumor characteristics (stage, grade, location)
- Surgical feasibility assessment
- Expected outcomes and risks

## Usage Examples

```python
from feature.decisions import DecisionService
from feature.decisions.adci_engine import ADCIEngine

# Initialize services
decision_service = DecisionService()
adci_engine = ADCIEngine()

# Make a decision
patient_data = {...}
decision = await decision_service.make_decision(
    patient_data, 
    engine_type="adci"
)

# Get confidence score
confidence = decision.confidence_score
recommendation = decision.recommendation
```

## API Endpoints

- `POST /api/v1/decisions/recommend` - Get treatment recommendation
- `GET /api/v1/decisions/confidence/{decision_id}` - Get confidence score
- `GET /api/v1/decisions/history/{patient_id}` - Get decision history
- `POST /api/v1/decisions/validate` - Validate decision parameters

## Configuration

```python
# Decision engine settings
ADCI_CONFIDENCE_THRESHOLD=0.8
DECISION_HISTORY_RETENTION_DAYS=365
ENABLE_MACHINE_LEARNING=True
```

## Testing
Tests located in `test/unit/decisions/`

## Dependencies
- scikit-learn (machine learning)
- numpy, scipy (statistical computing)
- pandas (data processing)
