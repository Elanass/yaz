import pytest
import datetime
from features.protocols.flot_analyzer import FLOTAnalyzer, PatientCharacteristics, TumorCharacteristics, FLOTEligibility, FLOTPhase

@pytest.fixture
def sample_patient_and_tumor():
    patient = PatientCharacteristics(
        age=65,
        performance_status=1,
        creatinine_clearance=60.0,
        bilirubin=1.0,
        cardiac_function="normal",
        hearing_function="normal",
        neuropathy_grade=0,
        previous_chemotherapy=False,
        allergies=[]
    )
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="moderately_differentiated",
        clinical_stage="T2N0M0",
        her2_status="negative",
        msi_status="stable",
        resectable=True,
        locally_advanced=False
    )
    return patient, tumor

@pytest.mark.asyncio
async def test_flot_eligibility_basic(sample_patient_and_tumor):
    patient, tumor = sample_patient_and_tumor
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor, treatment_intent="curative")
    # Check result fields
    assert result.eligibility in list(FLOTEligibility)
    assert 0 <= result.eligibility_score <= 100
    assert isinstance(result.eligibility_reasons, list)
    assert isinstance(result.predicted_benefit, float)
    assert isinstance(result.toxicity_risk, float)
    assert result.recommended_phase in list(FLOTPhase)
    assert isinstance(result.confidence_level, float)
    # Ensure monitoring_plan and alternatives are lists
    assert isinstance(result.monitoring_plan, list)
    assert isinstance(result.alternatives, list)

@pytest.mark.asyncio
async def test_flot_requires_modification_for_low_clearance():
    # Patient with severe renal impairment
    patient = PatientCharacteristics(
        age=75,
        performance_status=2,
        creatinine_clearance=10.0,
        bilirubin=2.0,
        cardiac_function="normal",
        hearing_function="normal",
        neuropathy_grade=1,
        previous_chemotherapy=False,
        allergies=[]
    )
    tumor = PatientCharacteristics(
        histology="adenocarcinoma",
        grade="poorly_differentiated",
        clinical_stage="T3N1M0",
        her2_status="positive",
        msi_status="high",
        resectable=True,
        locally_advanced=True
    )
    # Note: clinical characteristics passed incorrectly for tumor fields in test; adjust
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="poorly_differentiated",
        clinical_stage="T3N1M0",
        her2_status="positive",
        msi_status="high",
        resectable=True,
        locally_advanced=True
    )
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor)
    # Expect dose modifications for low clearance
    assert result.dose_modifications is not None
    assert result.dose_modifications.reduction_percentage > 0

@pytest.mark.asyncio
async def test_elderly_patient_eligibility():
    """Test elderly patient eligibility with comorbidities"""
    # Elderly patient with comorbidities
    patient = PatientCharacteristics(
        age=78,
        performance_status=2,
        creatinine_clearance=45.0,
        bilirubin=1.8,
        cardiac_function="mild_impairment",
        hearing_function="mild_loss",
        neuropathy_grade=1,
        previous_chemotherapy=False,
        allergies=[]
    )
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="moderately_differentiated",
        clinical_stage="T3N1M0",
        her2_status="negative",
        msi_status="stable",
        resectable=True,
        locally_advanced=True
    )
    
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor)
    
    # Elderly patients should not be automatically excluded, but should have
    # dose modifications and careful monitoring
    assert result.eligibility in [FLOTEligibility.RELATIVE_CONTRAINDICATION, 
                                 FLOTEligibility.REQUIRES_MODIFICATION]
    assert result.dose_modifications is not None
    assert result.dose_modifications.reduction_percentage >= 25
    assert len(result.monitoring_plan) >= 3  # Should have comprehensive monitoring


@pytest.mark.asyncio
async def test_allergic_patient_flot_eligibility():
    """Test patient with allergy to one of the FLOT drugs"""
    patient = PatientCharacteristics(
        age=65,
        performance_status=1,
        creatinine_clearance=70.0,
        bilirubin=0.8,
        cardiac_function="normal",
        hearing_function="normal",
        neuropathy_grade=0,
        previous_chemotherapy=False,
        allergies=["docetaxel"]  # Allergy to one of the FLOT components
    )
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="moderately_differentiated",
        clinical_stage="T3N0M0",
        her2_status="negative",
        msi_status="stable",
        resectable=True,
        locally_advanced=False
    )
    
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor)
    
    # Should not be eligible for standard FLOT
    assert result.eligibility != FLOTEligibility.ELIGIBLE
    # Should list allergy as a contraindication
    assert any("allergy" in reason.lower() or "docetaxel" in reason.lower() 
              for reason in result.contraindications)
    # Should provide alternatives
    assert len(result.alternatives) > 0


@pytest.mark.asyncio
async def test_advanced_metastatic_cancer_flot_eligibility():
    """Test patient with advanced metastatic disease"""
    patient = PatientCharacteristics(
        age=60,
        performance_status=1,
        creatinine_clearance=80.0,
        bilirubin=0.9,
        cardiac_function="normal",
        hearing_function="normal",
        neuropathy_grade=0,
        previous_chemotherapy=False,
        allergies=[]
    )
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="poorly_differentiated",
        clinical_stage="T4N2M1",  # Metastatic disease
        her2_status="negative",
        msi_status="stable",
        resectable=False,
        locally_advanced=True
    )
    
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor, treatment_intent="palliative")
    
    # Check that palliative intent is reflected in recommendations
    assert "palliative" in str(result.eligibility_reasons).lower()
    # Metastatic disease should affect the recommended phase
    assert result.recommended_phase != FLOTPhase.PREOPERATIVE


@pytest.mark.asyncio
async def test_her2_positive_tumor_impact():
    """Test the impact of HER2 positive status on recommendations"""
    patient = PatientCharacteristics(
        age=55,
        performance_status=0,
        creatinine_clearance=90.0,
        bilirubin=0.7,
        cardiac_function="normal",
        hearing_function="normal",
        neuropathy_grade=0,
        previous_chemotherapy=False,
        allergies=[]
    )
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="moderately_differentiated",
        clinical_stage="T3N1M0",
        her2_status="positive",  # HER2 positive
        msi_status="stable",
        resectable=True,
        locally_advanced=True
    )
    
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor)
    
    # HER2 positive status should be mentioned in recommendations
    assert any("her2" in str(reason).lower() for reason in result.eligibility_reasons) or \
           any("her2" in str(alt).lower() for alt in result.alternatives)
    
    # Should recommend trastuzumab-containing regimen as an alternative
    assert any("trastuzumab" in str(alt).lower() for alt in result.alternatives)


@pytest.mark.asyncio
async def test_comprehensive_monitoring_plan():
    """Test that monitoring plan is comprehensive for high-risk patients"""
    # Patient with multiple risk factors
    patient = PatientCharacteristics(
        age=72,
        performance_status=2,
        creatinine_clearance=40.0,
        bilirubin=1.7,
        cardiac_function="mild_impairment",
        hearing_function="mild_loss",
        neuropathy_grade=1,
        previous_chemotherapy=True,
        allergies=[]
    )
    tumor = TumorCharacteristics(
        histology="adenocarcinoma",
        grade="poorly_differentiated",
        clinical_stage="T3N2M0",
        her2_status="negative",
        msi_status="stable",
        resectable=True,
        locally_advanced=True
    )
    
    analyzer = FLOTAnalyzer()
    result = await analyzer.analyze_flot_eligibility(patient, tumor)
    
    # Ensure comprehensive monitoring plan for high-risk patient
    assert len(result.monitoring_plan) >= 5
    
    # Check for specific monitoring elements
    monitoring_str = ' '.join(result.monitoring_plan).lower()
    assert "renal" in monitoring_str  # Renal function monitoring
    assert "liver" in monitoring_str or "hepatic" in monitoring_str  # Liver function
    assert "neuro" in monitoring_str  # Neurological monitoring
    assert "cardiac" in monitoring_str or "heart" in monitoring_str  # Cardiac monitoring
