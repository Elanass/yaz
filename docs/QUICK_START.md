# Gastric ADCI Platform - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Clinical researcher or practitioner account
- Patient data in CSV, JSON, or FHIR format (optional)
- Modern web browser with JavaScript enabled

---

## Step 1: Access the Platform

1. Navigate to your Gastric ADCI Platform URL
2. Log in with your credentials
3. Click **"Cohort Management"** in the navigation bar

---

## Step 2: Create Your First Cohort

### Option A: Quick Manual Entry (Recommended for testing)

1. Click **"Create New Cohort Study"**
2. Fill in basic information:
   ```
   Study Name: "My First Cohort Test"
   Description: "Testing the cohort management system"
   Decision Engine: "ADCI"
   ```
3. Select **"Manual Entry"** as upload method
4. Add a test patient:
   ```
   Patient ID: TEST001
   Age: 65
   Gender: Male
   Clinical Parameters: 
   {
     "tumor_stage": "T2N1M0",
     "histology": "adenocarcinoma",
     "ecog_score": 1
   }
   ```
5. Click **"Create Cohort Study"**

### Option B: CSV File Upload (For existing data)

1. Prepare a CSV file with this format:
   ```csv
   patient_id,age,gender,clinical_parameters
   PT001,65,male,"{""tumor_stage"":""T2N1M0"",""histology"":""adenocarcinoma""}"
   PT002,72,female,"{""tumor_stage"":""T3N2M0"",""histology"":""signet_ring""}"
   ```
2. Select **"CSV File"** as upload method
3. Upload your file
4. Review the preview and click **"Create Cohort Study"**

---

## Step 3: Process Your Cohort

1. In your new cohort study, click **"Start Processing"**
2. Leave default settings or customize:
   - Session Name: "Initial Analysis"
   - Confidence Threshold: 0.75
3. Click **"Begin Processing"**
4. Watch the real-time progress indicator

⏱️ **Processing Time**: 1-2 minutes per patient typically

---

## Step 4: View Results

Once processing is complete:

1. **Summary Dashboard** shows key metrics:
   - Total patients processed
   - Average confidence scores
   - Risk distribution chart

2. **Patient Results Table** displays:
   - Individual recommendations
   - Confidence levels
   - Risk assessments

3. **Filter and Search**:
   - Filter by confidence level
   - Search specific patient IDs
   - Sort by risk scores

---

## Step 5: Export Your Results

1. Click **"Export Results"**
2. Choose format:
   - **CSV**: For spreadsheet analysis
   - **PDF**: For presentations
   - **FHIR**: For EHR integration
3. Select options and click **"Generate Export"**
4. Download when ready

---

## 🎯 What You've Accomplished

✅ Created your first cohort study  
✅ Processed patients through the ADCI engine  
✅ Analyzed results with confidence scoring  
✅ Exported data for further use  

---

## Next Steps

### Explore Advanced Features
- **Hypothesis Testing**: Create research questions
- **Batch Processing**: Handle larger cohorts (100+ patients)
- **Multiple Engines**: Try Gastrectomy and FLOT engines
- **Offline Mode**: Work without internet connection

### Real Clinical Data
- Import your actual patient cohorts
- Use standardized clinical parameters
- Set up regular processing workflows
- Generate reports for clinical teams

### Integration
- Connect to your EHR system via FHIR
- Set up automated cohort processing
- Configure user permissions for your team

---

## Common First-Time Issues

### ❌ CSV Upload Fails
**Fix**: Ensure clinical_parameters column contains valid JSON strings (wrapped in quotes)

### ❌ Low Confidence Scores
**Fix**: Include more clinical parameters like staging, histology, biomarkers

### ❌ Processing Stuck
**Fix**: Check internet connection; try smaller cohorts first

### ❌ Can't See Results
**Fix**: Wait for processing to complete; check status indicator

---

## Sample Clinical Parameters

### Minimal Required
```json
{
  "tumor_stage": "T2N1M0",
  "histology": "adenocarcinoma"
}
```

### Complete Recommended
```json
{
  "tumor_stage": "T2N1M0",
  "histology": "adenocarcinoma",
  "ecog_score": 1,
  "age": 65,
  "comorbidities": ["diabetes"],
  "biomarkers": {
    "her2": "negative",
    "msi": "stable"
  },
  "prior_treatments": [],
  "performance_status": "good"
}
```

---

## 📞 Need Help?

- **User Guide**: Full documentation available in `/docs/USER_GUIDE.md`
- **Technical Support**: tech-support@gastric-adci.health  
- **Clinical Questions**: clinical-support@gastric-adci.health
- **Video Tutorials**: Available in the platform help section

---

## 🧪 Try Sample Data

Want to test with realistic data? Use these sample patients:

```csv
patient_id,age,gender,clinical_parameters
SAMPLE_001,65,male,"{""tumor_stage"":""T2N1M0"",""histology"":""adenocarcinoma"",""ecog_score"":1}"
SAMPLE_002,72,female,"{""tumor_stage"":""T3N2M0"",""histology"":""signet_ring"",""ecog_score"":0}"
SAMPLE_003,58,male,"{""tumor_stage"":""T1N0M0"",""histology"":""adenocarcinoma"",""ecog_score"":0}"
```

This sample cohort will show you:
- Different risk levels (low, medium, high)
- Varying confidence scores
- Multiple treatment recommendations
- Evidence-based reasoning chains

---

**Ready to make evidence-based clinical decisions with confidence!** 🏥✨
