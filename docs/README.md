# 🏥 Gastric ADCI Platform - Complete Documentation Index

## 🚀 Quick Start
1. **Setup**: `./scripts/setup_local.sh`
2. **Upload Data**: Navigate to `/dashboard/upload`
3. **Run Analysis**: Use the dashboard or API
4. **Get Insights**: View results and generate reports

## 📚 Documentation

### Essential Guides
- **[Data Pipeline Guide](DATA_PIPELINE_GUIDE.md)** - Complete workflow from data input to insights
- **[API Documentation](http://localhost:8000/docs)** - Interactive API documentation (when server is running)

### Platform Architecture
- **Multi-Environment Support**: Local, P2P, Multi-cloud deployment
- **Data Input**: CSV, Excel, JSON files via web or API
- **Analysis Engines**: ADCI, FLOT, Statistical algorithms
- **Output**: Scientific publications, enterprise reports, data exports

## 🔧 Development

### Validation Scripts
- `python scripts/validate_platform.py` - Platform readiness check  
- `python scripts/validate_data_pipeline.py` - Data pipeline validation

### Environment Setup
```bash
export GASTRIC_ADCI_ENV=local     # Local development
export GASTRIC_ADCI_ENV=p2p       # P2P collaboration  
export GASTRIC_ADCI_ENV=multicloud # Cloud deployment
```

## 📊 Data Requirements

### Required Columns
- `patient_id`, `age`, `gender`
- `tumor_stage`, `histology`
- `flot_cycles`, `surgical_outcome`
- `survival_months`

### Supported Formats
- CSV (`.csv`)
- Excel (`.xlsx`) 
- JSON (`.json`)

## 🎯 Key Features

✅ **Data Processing**: Automated validation, cleaning, standardization  
✅ **Analysis Algorithms**: Cox regression, Random Forest, MCDA  
✅ **Decision Support**: ADCI framework, FLOT optimization  
✅ **Reproducibility**: Full audit trail and version control  
✅ **Export Options**: Multiple formats for different audiences  

## 📞 Support

- **Health Check**: `http://localhost:8000/health`
- **Validation**: `python scripts/validate_data_pipeline.py`
- **Sample Data**: `data/test_samples/`

---
*Platform validated and ready for data processing*
