# Analysis Feature

## Overview
The Analysis feature provides statistical modeling and decision support capabilities for surgical procedures, particularly focusing on gastric cancer treatment analysis.

## Components

### AnalysisEngine (`analysis.py`)
Core analysis engine that processes medical data and generates insights.

**Key Methods**:
- `analyze_cohort()` - Analyzes patient cohorts
- `generate_insights()` - Creates analysis insights
- `calculate_outcomes()` - Computes outcome predictions

### Analysis Engine (`analysis_engine.py`)
Advanced analysis processing with machine learning capabilities.

**Key Features**:
- Survival analysis using Cox regression
- Random Forest prediction models
- Statistical significance testing

### Impact Metrics (`impact_metrics.py`)
Utilities for calculating treatment impact and effectiveness metrics.

**Metrics Supported**:
- Survival rates
- Treatment effectiveness
- Risk assessment scores
- Confidence intervals

### Surgery Analyzer (`surgery_analyzer.py`)
Surgery-specific analysis focusing on gastric procedures.

**Analysis Types**:
- Pre-operative assessment
- Post-operative outcomes
- Surgical technique effectiveness

## Usage Examples

```python
from feature.analysis import AnalysisEngine

# Initialize engine
engine = AnalysisEngine()

# Analyze patient cohort
results = await engine.analyze_cohort(cohort_data)

# Generate insights
insights = await engine.generate_insights(analysis_type="prospective")
```

## API Endpoints

- `POST /api/v1/analysis/insights/generate` - Generate analysis insights
- `GET /api/v1/analysis/cohort/{cohort_id}` - Get cohort analysis
- `POST /api/v1/analysis/outcomes/predict` - Predict outcomes

## Testing
Tests located in `test/unit/analysis/` and `test/integration/`

## Dependencies
- pandas, numpy, scipy
- scikit-learn
- lifelines (survival analysis)
- plotly (visualization)
