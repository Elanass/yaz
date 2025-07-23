# Gastric ADCI Platform - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Cohort Management](#cohort-management)
3. [Decision Engine](#decision-engine)
4. [Results Analysis](#results-analysis)
5. [Export & Reports](#export--reports)
6. [Offline Functionality](#offline-functionality)
7. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Overview
The Gastric ADCI Platform is a comprehensive healthcare decision-support system designed for gastric oncology and surgery. It uses the Adaptive Decision Confidence Index (ADCI) framework to provide evidence-based treatment recommendations.

### Key Features
- **Cohort Management**: Upload and process multiple patients simultaneously
- **Decision Engines**: ADCI, Gastrectomy, and FLOT protocol engines
- **Real-time Processing**: Background processing with live status updates
- **Export Options**: CSV, PDF, FHIR, and Excel export formats
- **Offline Support**: Local data synchronization for uninterrupted workflow
- **Evidence-based**: All recommendations backed by clinical evidence

### User Roles
- **Clinical Researcher**: Full access to cohort management and analysis
- **Practitioner**: Individual patient decisions and limited cohort access
- **Admin**: Platform administration and user management

---

## Cohort Management

### Uploading Patient Cohorts

#### Accessing Cohort Management
1. Navigate to **Cohort Management** from the main navigation
2. Click **"Create New Cohort Study"**
3. Fill in the study information:
   - **Study Name**: Descriptive name for your cohort
   - **Description**: Optional detailed description
   - **Decision Engine**: Choose from ADCI, Gastrectomy, or FLOT
   - **Confidence Threshold**: Set minimum confidence level (0.5-1.0)

#### Upload Methods

##### Manual Entry
1. Select **"Manual Entry"** as the upload method
2. Fill in patient information:
   - **Patient ID**: Unique identifier
   - **Age**: Patient age (0-120)
   - **Gender**: Male, Female, or Other
   - **Clinical Parameters**: JSON format with clinical data

**Example Clinical Parameters:**
```json
{
  "tumor_stage": "T2N1M0",
  "histology": "adenocarcinoma",
  "ecog_score": 1,
  "comorbidities": ["diabetes", "hypertension"],
  "biomarkers": {
    "her2": "negative",
    "msi": "stable"
  }
}
```

3. Click **"+ Add Another Patient"** to add more patients
4. Click **"Create Cohort Study"** when finished

##### CSV File Upload
1. Select **"CSV File"** as the upload method
2. Prepare your CSV file with required columns:
   - `patient_id`: Unique patient identifier
   - `age`: Patient age
   - `gender`: male/female/other
   - `clinical_parameters`: JSON string with clinical data

**CSV Example:**
```csv
patient_id,age,gender,clinical_parameters
PT001,65,male,"{""tumor_stage"":""T2N1M0"",""histology"":""adenocarcinoma""}"
PT002,72,female,"{""tumor_stage"":""T3N2M0"",""histology"":""signet_ring""}"
```

3. Click **"Choose File"** and select your CSV
4. Review the file preview for validation
5. Click **"Create Cohort Study"**

##### JSON File Upload
1. Select **"JSON File"** as the upload method
2. Prepare a JSON array of patient objects:

```json
[
  {
    "patient_id": "PT001",
    "age": 65,
    "gender": "male",
    "clinical_parameters": {
      "tumor_stage": "T2N1M0",
      "histology": "adenocarcinoma",
      "ecog_score": 1
    }
  },
  {
    "patient_id": "PT002",
    "age": 72,
    "gender": "female",
    "clinical_parameters": {
      "tumor_stage": "T3N2M0",
      "histology": "signet_ring",
      "ecog_score": 0
    }
  }
]
```

##### FHIR Bundle Upload
1. Select **"FHIR Bundle"** as the upload method
2. Prepare a FHIR Bundle with Patient resources:

```json
{
  "resourceType": "Bundle",
  "type": "collection",
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "PT001",
        "birthDate": "1958-01-01",
        "gender": "male",
        "extension": [
          {
            "url": "clinical-parameters",
            "valueString": "{\"tumor_stage\":\"T2N1M0\"}"
          }
        ]
      }
    }
  ]
}
```

### Managing Cohort Studies

#### Viewing Cohorts
- Access **"My Cohorts"** from the navigation
- Use filters to find specific studies:
  - Status (Draft, Processing, Completed, Failed)
  - Date range
  - Engine type

#### Cohort Status Indicators
- 🟡 **Draft**: Study created but not yet processed
- 🔵 **Processing**: Currently running through decision engine
- 🟢 **Completed**: Processing finished successfully
- 🔴 **Failed**: Processing encountered errors

---

## Decision Engine

### Batch Processing

#### Starting Batch Processing
1. Open your cohort study
2. Click **"Start Processing"**
3. Optional: Customize processing settings:
   - **Session Name**: Descriptive name for this processing run
   - **Engine Parameters**: Adjust confidence thresholds
4. Click **"Begin Processing"**

#### Monitoring Progress
- **Real-time Status**: Processing status updates automatically
- **Progress Bar**: Shows percentage completion
- **Patient Count**: Tracks processed vs. total patients
- **Processing Time**: Estimated completion time

#### Decision Engine Types

##### ADCI Engine
- **Purpose**: Adaptive Decision Confidence Index for treatment recommendations
- **Input Parameters**:
  - Tumor staging (TNM classification)
  - Histological type
  - Patient performance status (ECOG)
  - Biomarker status
  - Comorbidities
- **Output**: Treatment recommendation with confidence score

##### Gastrectomy Engine
- **Purpose**: Surgical approach and technique recommendations
- **Input Parameters**:
  - Tumor location and size
  - Depth of invasion
  - Nodal status
  - Surgical risk assessment
- **Output**: Surgical approach with risk assessment

##### FLOT Engine
- **Purpose**: Perioperative chemotherapy optimization
- **Input Parameters**:
  - Disease staging
  - Operability assessment
  - Molecular markers
  - Organ function status
- **Output**: Chemotherapy protocol with timing recommendations

---

## Results Analysis

### Viewing Results

#### Results Dashboard
After processing completion, access results through:
1. **Cohort Overview**: High-level statistics and charts
2. **Patient Results Table**: Detailed per-patient outcomes
3. **Summary Statistics**: Aggregate analysis across the cohort

#### Key Metrics
- **Total Patients**: Number of patients processed
- **High Confidence Results**: Percentage with confidence > 0.8
- **Average Risk Score**: Mean risk assessment across cohort
- **Processing Time**: Total time for batch processing

#### Risk Distribution
Visual breakdown of patient risk levels:
- **Low Risk** (Green): Risk score < 0.3
- **Medium Risk** (Yellow): Risk score 0.3-0.7
- **High Risk** (Red): Risk score > 0.7

### Filtering and Searching

#### Filter Options
- **Risk Threshold**: Show only patients above/below risk level
- **Confidence Filter**: Filter by confidence level (High/Medium/Low)
- **Protocol Type**: Filter by recommended treatment protocol
- **Patient Demographics**: Filter by age, gender, staging

#### Search Functionality
- **Patient ID Search**: Find specific patients
- **Recommendation Search**: Search by treatment type
- **Clinical Parameter Search**: Find patients with specific characteristics

### Hypothesis Testing

#### Creating Hypotheses
1. Navigate to **"Hypothesis Explorer"** in results view
2. Click **"Create New Hypothesis"**
3. Define your hypothesis:
   - **Hypothesis Name**: Descriptive title
   - **Question**: Research question to investigate
   - **Parameters**: Variables to analyze
   - **Comparison Groups**: Patient subsets to compare

#### Example Hypotheses
- "How does ECOG score affect FLOT recommendation confidence?"
- "Which tumor types show resistance to surgery protocols?"
- "Does age impact treatment recommendation patterns?"

#### Statistical Analysis
- **P-values**: Statistical significance testing
- **Confidence Intervals**: Range estimates for findings
- **Effect Sizes**: Magnitude of observed differences

---

## Export & Reports

### Export Formats

#### CSV Export
- **Content**: Raw patient data and results
- **Use Case**: Further analysis in spreadsheet software
- **Includes**: Patient demographics, clinical parameters, recommendations, confidence scores

#### PDF Report
- **Content**: Executive summary with charts and analysis
- **Use Case**: Presentation to clinical teams or regulatory bodies
- **Includes**: Summary statistics, risk distribution charts, key findings

#### FHIR Bundle
- **Content**: Standardized healthcare data format
- **Use Case**: Integration with Electronic Health Records (EHR)
- **Includes**: Patient resources, observations, diagnostic reports

#### Excel Workbook
- **Content**: Multi-sheet analysis with pivot tables
- **Use Case**: Detailed statistical analysis
- **Includes**: Raw data, summary statistics, charts, pivot tables

### Creating Exports

#### Export Process
1. Go to cohort results page
2. Click **"Export Results"**
3. Select export format
4. Choose included options:
   - Summary statistics
   - Evidence citations
   - Alternative recommendations
5. Click **"Generate Export"**
6. Monitor export progress
7. Download when ready

#### Export Status
- **Processing**: Export being generated
- **Completed**: Ready for download
- **Failed**: Error occurred during export

### Deliverables Management

#### Audit Trail
- All exports are logged with:
  - User who requested export
  - Timestamp of request
  - Format and options selected
  - Download history

#### Access Control
- Export permissions based on user role
- Data filtering based on patient access rights
- Secure download links with expiration

---

## Offline Functionality

### GunDB Synchronization

#### Automatic Sync
- **Local Storage**: All cohort data stored locally using GunDB
- **Real-time Sync**: Changes synchronized when online
- **Conflict Resolution**: Automatic merging of concurrent changes

#### Offline Capabilities
- **Data Entry**: Add patients and create cohorts offline
- **View Results**: Access previously loaded results
- **Export**: Generate reports from cached data

#### Going Online/Offline
- **Offline Indicator**: Status shown in interface
- **Sync Progress**: Visual indicator of synchronization
- **Conflict Notifications**: Alert when manual resolution needed

### Local Data Management

#### Data Backup
- **Auto-backup**: Regular local data backups
- **Manual Export**: Export local data for external backup
- **Import**: Restore from backup files

#### Storage Limits
- **Local Capacity**: ~50MB typical storage per user
- **Cleanup**: Automatic removal of old cached data
- **Priority**: Recent and frequently accessed data prioritized

---

## Troubleshooting

### Common Issues

#### Upload Problems

**Issue**: CSV file validation errors
**Solution**: 
1. Check required columns are present: `patient_id`, `age`, `gender`, `clinical_parameters`
2. Ensure clinical_parameters contain valid JSON
3. Verify patient_id values are unique
4. Check file encoding is UTF-8

**Issue**: JSON format errors
**Solution**:
1. Validate JSON syntax using online JSON validator
2. Ensure all required fields are present
3. Check data types match expected format
4. Verify patient array structure

#### Processing Issues

**Issue**: Processing stuck or failed
**Solution**:
1. Check internet connection for cloud processing
2. Verify patient data completeness
3. Review clinical parameters for missing required fields
4. Contact support if issue persists

**Issue**: Low confidence scores
**Solution**:
1. Review patient clinical parameters completeness
2. Check if staging information is accurate
3. Ensure biomarker data is included where available
4. Consider adjusting confidence threshold

#### Export Problems

**Issue**: Export generation fails
**Solution**:
1. Check selected options are compatible
2. Verify sufficient processing has completed
3. Try smaller data subsets
4. Clear browser cache and retry

#### Sync Issues

**Issue**: Offline data not syncing
**Solution**:
1. Check internet connectivity
2. Refresh the page to trigger sync
3. Clear browser data and re-login
4. Contact support for manual sync

### Performance Optimization

#### Large Cohorts
- **Batch Size**: Upload in smaller batches (< 100 patients)
- **Processing**: Allow adequate time for large cohorts
- **Memory**: Close other browser tabs during processing

#### Network Issues
- **Slow Connections**: Use manual entry for small cohorts
- **Intermittent Connectivity**: Enable offline mode
- **Firewall**: Ensure websocket connections allowed

### Getting Help

#### Support Channels
- **Technical Support**: tech-support@gastric-adci.health
- **Clinical Support**: clinical-support@gastric-adci.health
- **Documentation**: Check online help center
- **Community**: User forum for peer support

#### Error Reporting
When reporting issues, include:
1. User ID and timestamp of issue
2. Browser and version information
3. Steps to reproduce the problem
4. Error messages or screenshots
5. Cohort size and processing details

---

## Best Practices

### Data Quality
- **Standardization**: Use consistent terminology and staging systems
- **Completeness**: Include all available clinical parameters
- **Validation**: Review data before processing
- **Documentation**: Maintain clear study descriptions

### Security
- **Access Control**: Use appropriate user roles
- **Data Handling**: Follow institutional data policies
- **Export Security**: Secure handling of exported data
- **Patient Privacy**: Ensure proper de-identification

### Workflow Efficiency
- **Batch Processing**: Group similar studies together
- **Template Use**: Create templates for common cohort types
- **Regular Sync**: Maintain good internet connectivity
- **Planning**: Allow adequate time for large cohort processing

---

For additional support or questions not covered in this guide, please contact our support team or consult the API documentation for advanced integration scenarios.
