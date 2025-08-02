#!/usr/bin/env python3
"""
Data Pipeline Validation for Gastric ADCI Platform
Validates the complete data-to-insights pipeline readiness
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import asyncio
from datetime import datetime

class DataPipelineValidator:
    """Comprehensive validation of data pipeline capabilities"""
    
    def __init__(self, workspace_path: str = "/workspaces/yaz"):
        self.workspace = Path(workspace_path)
        self.results = {"passed": [], "failed": [], "warnings": []}
        self.base_url = "http://localhost:8000"
        
    def log_result(self, category: str, test: str, status: str = "passed"):
        """Log test result"""
        self.results[category].append(test)
        icon = "✅" if status == "passed" else "❌" if status == "failed" else "⚠️"
        print(f"{icon} {test}")
        
    def validate_data_input_capabilities(self) -> bool:
        """Validate data input mechanisms"""
        print("\n📥 Validating Data Input Capabilities...")
        
        # Check upload endpoints
        api_file = self.workspace / "api/v1/analysis.py"
        if api_file.exists():
            content = api_file.read_text()
            if "upload_cohort_dataset" in content:
                self.log_result("passed", "Cohort upload endpoint exists")
            else:
                self.log_result("failed", "Missing cohort upload endpoint", "failed")
                
        # Check file format support
        supported_formats = [".csv", ".xlsx", ".json"]
        if api_file.exists():
            content = api_file.read_text()
            for fmt in supported_formats:
                if fmt in content:
                    self.log_result("passed", f"Support for {fmt} format detected")
                else:
                    self.log_result("failed", f"Missing {fmt} format support", "failed")
                    
        # Check upload directory structure
        upload_dir = self.workspace / "data/uploads"
        if upload_dir.exists():
            self.log_result("passed", "Upload directory structure exists")
        else:
            self.log_result("failed", "Missing upload directory structure", "failed")
            
        # Check web upload interface
        upload_template = self.workspace / "web/templates/dashboard/cohort_upload.html"
        if upload_template.exists():
            self.log_result("passed", "Web upload interface exists")
        else:
            self.log_result("failed", "Missing web upload interface", "failed")
            
        return len(self.results["failed"]) == 0
        
    def validate_data_processing_capabilities(self) -> bool:
        """Validate data processing and preparation"""
        print("\n⚙️ Validating Data Processing Capabilities...")
        
        # Check analysis engines
        analysis_engine = self.workspace / "features/analysis/analysis_engine.py"
        if analysis_engine.exists():
            self.log_result("passed", "Analysis engine exists")
        else:
            self.log_result("failed", "Missing analysis engine", "failed")
            
        # Check ADCI engine
        adci_engine = self.workspace / "features/decisions/adci_engine.py"
        if adci_engine.exists():
            self.log_result("passed", "ADCI decision engine exists")
        else:
            self.log_result("failed", "Missing ADCI engine", "failed")
            
        # Check FLOT analyzer
        flot_analyzer = self.workspace / "features/protocols/flot_analyzer.py"
        if flot_analyzer.exists():
            self.log_result("passed", "FLOT protocol analyzer exists")
        else:
            self.log_result("failed", "Missing FLOT analyzer", "failed")
            
        # Check data validation utilities
        helpers = self.workspace / "core/utils/helpers.py"
        if helpers.exists():
            content = helpers.read_text()
            if "load_csv" in content:
                self.log_result("passed", "CSV processing utilities exist")
            else:
                self.log_result("failed", "Missing CSV processing utilities", "failed")
                
        return len(self.results["failed"]) == 0
        
    def validate_algorithm_capabilities(self) -> bool:
        """Validate algorithm and ML capabilities"""
        print("\n🧠 Validating Algorithm Capabilities...")
        
        # Check statistical analysis
        surgery_analyzer = self.workspace / "features/analysis/surgery_analyzer.py"
        if surgery_analyzer.exists():
            content = surgery_analyzer.read_text()
            algorithms = [
                ("Cox Regression", "cox"),
                ("Random Forest", "RandomForest"),
                ("Logistic Regression", "LogisticRegression"),
                ("Survival Analysis", "survival")
            ]
            
            for name, keyword in algorithms:
                if keyword.lower() in content.lower():
                    self.log_result("passed", f"{name} algorithm available")
                else:
                    self.log_result("warnings", f"{name} algorithm not detected", "warning")
        else:
            self.log_result("failed", "Missing surgery analyzer", "failed")
            
        # Check MCDA capabilities
        precision_engine = self.workspace / "features/decisions/precision_engine.py"
        if precision_engine.exists():
            content = precision_engine.read_text()
            if "mcda" in content.lower() or "multiple criteria" in content.lower():
                self.log_result("passed", "MCDA decision support available")
            else:
                self.log_result("warnings", "MCDA capabilities not clearly detected", "warning")
        else:
            self.log_result("failed", "Missing precision engine", "failed")
            
        return len(self.results["failed"]) == 0
        
    def validate_output_capabilities(self) -> bool:
        """Validate output and deliverables generation"""
        print("\n📤 Validating Output Capabilities...")
        
        # Check report generation
        reports_dir = self.workspace / "web/templates/reports"
        if reports_dir.exists():
            self.log_result("passed", "Report templates directory exists")
            
            # Check for specific report types
            report_files = list(reports_dir.glob("*.html"))
            if report_files:
                self.log_result("passed", f"Found {len(report_files)} report templates")
            else:
                self.log_result("warnings", "No report templates found", "warning")
        else:
            self.log_result("failed", "Missing report templates", "failed")
            
        # Check publication preparation
        api_file = self.workspace / "api/v1/analysis.py"
        if api_file.exists():
            content = api_file.read_text()
            if "publication" in content.lower():
                self.log_result("passed", "Publication preparation endpoints exist")
            else:
                self.log_result("warnings", "Publication preparation not detected", "warning")
                
        # Check results storage
        results_dir = self.workspace / "data/results"
        if not results_dir.exists():
            results_dir.mkdir(parents=True, exist_ok=True)
            self.log_result("passed", "Results storage directory created")
        else:
            self.log_result("passed", "Results storage directory exists")
            
        # Check reproducibility
        repro_manager = self.workspace / "core/reproducibility/manager.py"
        if repro_manager.exists():
            self.log_result("passed", "Reproducibility manager exists")
        else:
            self.log_result("failed", "Missing reproducibility manager", "failed")
            
        return len(self.results["failed"]) == 0
        
    async def validate_api_endpoints(self) -> bool:
        """Validate API endpoints for data pipeline"""
        print("\n🌐 Validating API Endpoints...")
        
        # Note: This would require the server to be running
        # For now, we'll check the endpoint definitions
        
        api_file = self.workspace / "api/v1/analysis.py"
        if api_file.exists():
            content = api_file.read_text()
            
            endpoints = [
                ("/cohort/upload", "Data upload"),
                ("/cohort/{cohort_id}/analyze", "Data analysis"),
                ("/insights/generate", "Insight generation"),
                ("/results/{analysis_id}", "Results retrieval")
            ]
            
            for endpoint, description in endpoints:
                if endpoint.replace("{", "").replace("}", "") in content:
                    self.log_result("passed", f"{description} endpoint defined")
                else:
                    self.log_result("failed", f"Missing {description} endpoint", "failed")
        else:
            self.log_result("failed", "Missing API analysis module", "failed")
            
        return len(self.results["failed"]) == 0
        
    def create_sample_data(self) -> bool:
        """Create sample data for testing"""
        print("\n📊 Creating Sample Test Data...")
        
        # Create sample CSV data
        sample_data = {
            'patient_id': [f'P{i:03d}' for i in range(1, 51)],
            'age': [45 + (i % 30) for i in range(50)],
            'gender': ['M' if i % 2 == 0 else 'F' for i in range(50)],
            'tumor_stage': [f'T{(i % 4) + 1}' for i in range(50)],
            'histology': ['Adenocarcinoma' if i % 3 == 0 else 'Signet Ring' for i in range(50)],
            'flot_cycles': [4 + (i % 4) for i in range(50)],
            'surgical_outcome': ['Complete' if i % 3 != 0 else 'Partial' for i in range(50)],
            'survival_months': [12 + (i % 36) for i in range(50)]
        }
        
        df = pd.DataFrame(sample_data)
        
        # Save to test data directory
        test_dir = self.workspace / "data/test_samples"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        csv_file = test_dir / "sample_gastric_cohort.csv"
        df.to_csv(csv_file, index=False)
        self.log_result("passed", f"Sample CSV data created: {csv_file}")
        
        # Create Excel version
        excel_file = test_dir / "sample_gastric_cohort.xlsx"
        df.to_excel(excel_file, index=False)
        self.log_result("passed", f"Sample Excel data created: {excel_file}")
        
        # Create JSON version
        json_file = test_dir / "sample_gastric_cohort.json"
        with open(json_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
        self.log_result("passed", f"Sample JSON data created: {json_file}")
        
        return True
        
    def generate_pipeline_guideline(self) -> str:
        """Generate comprehensive data pipeline guideline"""
        
        guideline = """
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
curl -X POST "http://localhost:8000/api/v1/analysis/cohort/upload" \\
     -H "Content-Type: multipart/form-data" \\
     -F "file=@your_data.csv" \\
     -F "cohort_name=My Research Cohort" \\
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
"""
        return guideline.strip()
        
    def run_validation(self) -> Dict[str, Any]:
        """Run complete data pipeline validation"""
        print("🏥 Gastric ADCI Platform - Data Pipeline Validation")
        print("=" * 60)
        
        # Run all validation checks
        input_ok = self.validate_data_input_capabilities()
        processing_ok = self.validate_data_processing_capabilities()
        algorithms_ok = self.validate_algorithm_capabilities()
        output_ok = self.validate_output_capabilities()
        
        # Create sample data
        sample_ok = self.create_sample_data()
        
        # Generate summary
        total_tests = len(self.results["passed"]) + len(self.results["failed"]) + len(self.results["warnings"])
        success_rate = (len(self.results["passed"]) / total_tests * 100) if total_tests > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"🎯 Success Rate: {success_rate:.1f}%")
        
        if len(self.results["failed"]) == 0:
            print("\n✅ PLATFORM READY FOR DATA PROCESSING!")
            print("🚀 You can now upload data and generate insights")
        else:
            print("\n❌ PLATFORM NEEDS ATTENTION")
            print("🔧 Please address the failed checks above")
            
        return {
            "success": len(self.results["failed"]) == 0,
            "summary": self.results,
            "success_rate": success_rate
        }

def main():
    validator = DataPipelineValidator()
    
    # Run validation
    results = validator.run_validation()
    
    # Generate and save guideline
    guideline = validator.generate_pipeline_guideline()
    
    docs_dir = Path("/workspaces/yaz/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    guideline_file = docs_dir / "DATA_PIPELINE_GUIDE.md"
    with open(guideline_file, 'w') as f:
        f.write(guideline)
    
    print(f"\n📚 Data pipeline guide created: {guideline_file}")
    
    return results

if __name__ == "__main__":
    results = main()
    exit_code = 0 if results["success"] else 1
    sys.exit(exit_code)
