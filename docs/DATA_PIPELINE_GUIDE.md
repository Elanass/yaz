# 🏥 Gastric ADCI Platform - Data Pipeline Guide

## Overview
The Gastric ADCI Platform provides a complete data-to-insights pipeline for surgical decision support and research deliverables.

## 📥 Data Input Methods

### 1. Web Interface Upload
- Navigate to `/dashboard/upload`
- Drag & drop or browse files
- Supported formats: CSV, Excel (.xlsx), JSON
- Maximum file size: 100MB
- Maximum records: 10,000 per cohort

### 2. API Upload
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/cohort/upload" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_data.csv" \
     -F "cohort_name=My Research Cohort" \
     -F "description=Gastric cancer surgical outcomes"
```

### 3. Required Data Columns
- `patient_id`: Unique patient identifier
- `age`: Patient age (numeric)
- `gender`: M/F
- `tumor_stage`: TNM staging (T1-T4)
- `histology`: Tumor histology type
- `flot_cycles`: Number of FLOT therapy cycles
- `surgical_outcome`: Complete/Partial/None
- `survival_months`: Survival time (numeric)

## ⚙️ Data Processing Pipeline

1. **Upload Validation**: File format, size, and schema validation
2. **Data Cleaning**: Missing value handling, outlier detection
3. **Standardization**: Column mapping, data type conversion
4. **Quality Checks**: Consistency validation, range checks
5. **Storage**: Secure storage with metadata tracking

## 🧠 Analysis Algorithms

### Statistical Analysis
- **Cox Proportional Hazards**: Survival analysis with risk factors
- **Random Forest**: Outcome prediction and feature importance
- **Logistic Regression**: Binary outcome classification
- **Kaplan-Meier**: Survival curve estimation

### Decision Support
- **ADCI Framework**: Adaptive Decision Confidence Index
- **MCDA**: Multiple Criteria Decision Analysis
- **FLOT Optimization**: Perioperative therapy optimization

## 📊 Insight Generation

### Automated Insights
- Survival predictor identification
- Treatment response patterns
- Risk stratification models
- Outcome optimization recommendations

### Interactive Analysis
- Real-time dashboard visualization
- Custom cohort comparisons
- Statistical significance testing
- Confidence interval estimation

## 📤 Output Deliverables

### Scientific Publications
- Methodology documentation
- Results visualization
- Statistical analysis reports
- Reproducibility packages

### Enterprise Reports
- Executive summaries
- Performance metrics
- Quality indicators
- Treatment recommendations

### Data Exports
- Processed datasets (CSV, Excel, JSON)
- Analysis results (JSON, PDF)
- Visualization assets (PNG, SVG)
- Reproducibility artifacts

## 🔄 API Workflow Example

```python
import requests
import json

# 1. Upload cohort data
files = {'file': open('gastric_cohort.csv', 'rb')}
data = {
    'cohort_name': 'Q1 2025 Gastric Patients',
    'description': 'Prospective gastric cancer cohort'
}
response = requests.post(
    'http://localhost:8000/api/v1/analysis/cohort/upload',
    files=files,
    data=data
)
cohort_id = response.json()['cohort_id']

# 2. Run analysis
analysis_config = {
    'analysis_type': 'prospective',
    'algorithms': ['cox_regression', 'random_forest'],
    'confidence_level': 0.95
}
response = requests.post(
    f'http://localhost:8000/api/v1/analysis/cohort/{cohort_id}/analyze',
    json=analysis_config
)
analysis_id = response.json()['analysis_id']

# 3. Get results
response = requests.get(
    f'http://localhost:8000/api/v1/analysis/results/{analysis_id}'
)
results = response.json()

# 4. Generate insights
insights_response = requests.post(
    'http://localhost:8000/api/v1/analysis/insights/generate',
    json={'data': results['results'], 'analysis_type': 'prospective'}
)
insights = insights_response.json()
```

## 🎯 Quick Start Checklist

- [ ] Platform running (`python main.py`)
- [ ] Upload test data (`data/test_samples/`)
- [ ] Verify processing (`/dashboard/upload`)
- [ ] Run analysis (`/dashboard`)
- [ ] Generate insights (`/api/v1/analysis/insights/generate`)
- [ ] Export results (`/dashboard/results/{analysis_id}`)

## 🔒 Data Security & Compliance

- HIPAA-compliant data handling
- Encryption at rest and in transit
- Audit logging for all operations
- Role-based access controls
- Data anonymization options

## 📞 Support & Documentation

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`
- Validation Script: `python scripts/validate_data_pipeline.py`
- GitHub Issues: [Report problems](https://github.com/your-repo/issues)

---
*Last updated: {datetime.now().strftime('%Y-%m-%d')}*