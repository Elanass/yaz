"""
Tests for gastric domain entity models and analysis functions
"""

import pytest

from surge.core.models.medical import (
    AnatomicalRegion,
    ExpressionLevel,
    GastricSystem,
    GastricSystemStatus,
    HistologyType,
    IndependentCellEntity,
    MetastasisStage,
    NodeStage,
    TumorGrade,
    TumorStage,
    TumorUnit,
)
from surge.modules.chemo_flot import FLOTCase, analyze_flot_regimen
from surge.modules.gastric_surgery import GastricSurgeryCase, analyze_gastrectomy_case
from surge.modules.precision_engine import (
    IntegratedCase,
    create_gastric_oncology_strategy,
)


class TestGastricSystemEntity:
    """Test gastric system entity model"""

    def test_gastric_system_creation(self):
        """Test creating gastric system entity"""
        gastric_system = GastricSystem(
            system_id="GS001",
            patient_id="P001",
            primary_region=AnatomicalRegion.ANTRUM,
            involved_regions=[AnatomicalRegion.ANTRUM, AnatomicalRegion.BODY],
            functional_status=GastricSystemStatus.NORMAL,
            gastric_emptying_time=90.0,
            wall_thickness_mm=8.5,
            assessed_by="Dr. Test",
        )

        assert gastric_system.system_id == "GS001"
        assert gastric_system.primary_region == AnatomicalRegion.ANTRUM
        assert gastric_system.functional_status == GastricSystemStatus.NORMAL
        assert len(gastric_system.involved_regions) == 2

    def test_gastric_system_validation(self):
        """Test gastric system validation"""
        with pytest.raises(ValueError):
            GastricSystem(
                system_id="",  # Empty system_id should fail
                patient_id="P001",
                primary_region=AnatomicalRegion.ANTRUM,
                functional_status=GastricSystemStatus.NORMAL,
            )


class TestTumorUnitEntity:
    """Test tumor unit entity model"""

    def test_tumor_unit_creation(self):
        """Test creating tumor unit entity"""
        tumor_unit = TumorUnit(
            tumor_id="TU001",
            case_id="C001",
            patient_id="P001",
            t_stage=TumorStage.T3,
            n_stage=NodeStage.N1,
            m_stage=MetastasisStage.M0,
            histology_type=HistologyType.ADENOCARCINOMA,
            tumor_grade=TumorGrade.G2,
            primary_location=AnatomicalRegion.ANTRUM,
            tumor_size_cm=4.2,
            her2_status="negative",
            msi_status="MSS",
            pdl1_expression=15.0,
        )

        assert tumor_unit.tumor_id == "TU001"
        assert tumor_unit.t_stage == TumorStage.T3
        assert tumor_unit.histology_type == HistologyType.ADENOCARCINOMA
        assert tumor_unit.tumor_size_cm == 4.2
        assert tumor_unit.pdl1_expression == 15.0

    def test_tumor_unit_biomarkers(self):
        """Test tumor unit biomarker fields"""
        tumor_unit = TumorUnit(
            tumor_id="TU002",
            case_id="C002",
            patient_id="P002",
            t_stage=TumorStage.T2,
            n_stage=NodeStage.N0,
            m_stage=MetastasisStage.M0,
            histology_type=HistologyType.SIGNET_RING,
            tumor_grade=TumorGrade.G3,
            primary_location=AnatomicalRegion.BODY,
            her2_status="positive",
            her2_score="3+",
            msi_status="MSI-H",
            pdl1_expression=80.0,
            ebv_status="positive",
        )

        assert tumor_unit.her2_status == "positive"
        assert tumor_unit.her2_score == "3+"
        assert tumor_unit.msi_status == "MSI-H"
        assert tumor_unit.pdl1_expression == 80.0


class TestIndependentCellEntity:
    """Test independent cell entity model"""

    def test_cell_entity_creation(self):
        """Test creating independent cell entity"""
        cell_entity = IndependentCellEntity(
            cell_entity_id="ICE001",
            tumor_id="TU001",
            her2_expression=ExpressionLevel.LOW,
            ki67_percentage=18.5,
            mlh1_expression=ExpressionLevel.MODERATE,
            pdl1_expression=15.0,
            p53_expression=ExpressionLevel.HIGH,
            analyzed_by="Dr. Pathologist",
        )

        assert cell_entity.cell_entity_id == "ICE001"
        assert cell_entity.her2_expression == ExpressionLevel.LOW
        assert cell_entity.ki67_percentage == 18.5
        assert cell_entity.pdl1_expression == 15.0

    def test_cell_entity_mmr_proteins(self):
        """Test MMR protein expression fields"""
        cell_entity = IndependentCellEntity(
            cell_entity_id="ICE002",
            tumor_id="TU002",
            mlh1_expression=ExpressionLevel.NEGATIVE,
            msh2_expression=ExpressionLevel.NEGATIVE,
            msh6_expression=ExpressionLevel.MODERATE,
            pms2_expression=ExpressionLevel.MODERATE,
            msi_status="MSI-H",
            analyzed_by="Dr. Molecular",
        )

        assert cell_entity.mlh1_expression == ExpressionLevel.NEGATIVE
        assert cell_entity.msh2_expression == ExpressionLevel.NEGATIVE
        assert cell_entity.msi_status == "MSI-H"


class TestGastrectomyAnalysis:
    """Test gastrectomy analysis function"""

    def test_analyze_gastrectomy_case_basic(self):
        """Test basic gastrectomy analysis"""
        case = GastricSurgeryCase(
            patient_id="P001",
            case_id="GC001",
            age=65,
            gender="M",
            tumor_stage="T3",
            node_stage="N1",
            metastasis_stage="M0",
            histology="adenocarcinoma",
            gastrectomy_type="subtotal_gastrectomy",
            surgical_approach="laparoscopic",
            resection_status="R0",
            lymph_nodes_examined=25,
            lymph_nodes_positive=3,
            proximal_margin_cm=6.0,
            distal_margin_cm=3.5,
            asa_score=2,
        )

        analysis = analyze_gastrectomy_case(case)

        assert analysis["case_id"] == "GC001"
        assert "r0_analysis" in analysis
        assert "lymph_node_analysis" in analysis
        assert "length_of_stay" in analysis
        assert "complications" in analysis
        assert "mortality_risk" in analysis
        assert "readmission_risk" in analysis
        assert "quality_metrics" in analysis

        # Check R0 analysis
        assert analysis["r0_analysis"]["r0_achieved"] == True
        assert analysis["r0_analysis"]["margin_assessment"]["adequate_margins"] == True

        # Check lymph node analysis
        assert analysis["lymph_node_analysis"]["adequate_harvest"] == True
        assert analysis["lymph_node_analysis"]["total_nodes_examined"] == 25

        # Check quality metrics
        quality_metrics = analysis["quality_metrics"]
        assert "quality_percentage" in quality_metrics
        assert "quality_grade" in quality_metrics

    def test_analyze_gastrectomy_complications(self):
        """Test gastrectomy analysis with complications"""
        case = GastricSurgeryCase(
            patient_id="P002",
            case_id="GC002",
            age=75,
            gender="F",
            tumor_stage="T4",
            gastrectomy_type="total_gastrectomy",
            surgical_approach="open",
            resection_status="R1",
            lymph_nodes_examined=12,
            lymph_nodes_positive=8,
            asa_score=4,
            postoperative_complications=["anastomotic_leak", "pneumonia"],
        )

        analysis = analyze_gastrectomy_case(case)

        # Should have higher risk due to complications and patient factors
        assert analysis["mortality_risk"]["risk_category"] in ["moderate", "high"]
        assert analysis["complications"]["major_complications"] > 0
        assert analysis["quality_metrics"]["quality_percentage"] < 80


class TestFLOTAnalysis:
    """Test FLOT regimen analysis function"""

    def test_analyze_flot_regimen_basic(self):
        """Test basic FLOT analysis"""
        case = FLOTCase(
            patient_id="P001",
            case_id="FLOT001",
            age=65,
            initial_t_stage=TumorStage.T3,
            initial_n_stage=NodeStage.N1,
            initial_m_stage=MetastasisStage.M0,
            flot_phase="complete",
            cycles_planned=8,
            cycles_completed=8,
            baseline_ecog=1,
            baseline_albumin=3.8,
            baseline_creatinine=1.1,
            max_toxicity_grade="2",
            clinical_response="partial_response",
        )

        analysis = analyze_flot_regimen(case)

        assert analysis["case_id"] == "FLOT001"
        assert "applicability" in analysis
        assert "dose_intensity" in analysis
        assert "toxicity" in analysis
        assert "response" in analysis
        assert "overall_assessment" in analysis
        assert "narrative_summary" in analysis

        # Check applicability
        applicability = analysis["applicability"]
        assert applicability["applicability_score"] > 50  # Should be a good candidate

        # Check dose intensity
        dose_intensity = analysis["dose_intensity"]
        assert dose_intensity["completion_rate"] == 100  # Completed all cycles

        # Check overall assessment
        overall = analysis["overall_assessment"]
        assert "composite_score" in overall
        assert "grade" in overall

    def test_analyze_flot_poor_candidate(self):
        """Test FLOT analysis for poor candidate"""
        case = FLOTCase(
            patient_id="P003",
            case_id="FLOT003",
            age=85,  # High age
            initial_t_stage=TumorStage.T1,  # Low stage
            initial_n_stage=NodeStage.N0,
            initial_m_stage=MetastasisStage.M0,
            baseline_ecog=3,  # Poor performance status
            baseline_albumin=2.2,  # Poor nutrition
            baseline_creatinine=2.5,  # Poor kidney function
            cycles_planned=8,
            cycles_completed=3,  # Poor completion
            max_toxicity_grade="4",  # Severe toxicity
            dose_reductions=["25%", "50%"],
        )

        analysis = analyze_flot_regimen(case)

        # Should show poor candidacy and outcomes
        assert analysis["applicability"]["applicability_score"] < 60
        assert analysis["dose_intensity"]["completion_rate"] < 50
        assert analysis["toxicity"]["tolerability_assessment"] == "Severe"


class TestPrecisionDecisionEngine:
    """Test precision decision engine integration"""

    def test_gastric_oncology_strategy_creation(self):
        """Test creating gastric oncology strategy"""
        strategy = create_gastric_oncology_strategy()

        assert strategy["strategy_id"] == "gastric-oncology"
        assert "version" in strategy
        assert "biomarker_panel" in strategy
        assert "analyze_function" in strategy
        assert callable(strategy["analyze_function"])

    def test_integrated_gastric_analysis(self):
        """Test integrated analysis with all entities"""
        # Create integrated case
        integrated_case = IntegratedCase(
            patient_id="P001",
            case_id="INT001",
            age=65,
            performance_status=1,
            comorbidities=["hypertension"],
            her2_status="negative",
            msi_status="MSS",
        )

        # Create gastric system
        gastric_system = GastricSystem(
            system_id="GS001",
            patient_id="P001",
            primary_region=AnatomicalRegion.ANTRUM,
            functional_status=GastricSystemStatus.NORMAL,
        )

        # Create tumor unit
        tumor_unit = TumorUnit(
            tumor_id="TU001",
            case_id="INT001",
            patient_id="P001",
            t_stage=TumorStage.T3,
            n_stage=NodeStage.N1,
            m_stage=MetastasisStage.M0,
            histology_type=HistologyType.ADENOCARCINOMA,
            tumor_grade=TumorGrade.G2,
            primary_location=AnatomicalRegion.ANTRUM,
        )

        # Create cell entity
        cell_entity = IndependentCellEntity(
            cell_entity_id="ICE001",
            tumor_id="TU001",
            her2_expression=ExpressionLevel.LOW,
            ki67_percentage=18.5,
            analyzed_by="Dr. Test",
        )

        # Run integrated analysis
        strategy = create_gastric_oncology_strategy()
        analysis = strategy["analyze_function"](
            case=integrated_case,
            gastric_system=gastric_system,
            tumor_unit=tumor_unit,
            cell_entity=cell_entity,
        )

        assert analysis["case_id"] == "INT001"
        assert analysis["strategy"] == "gastric-oncology"
        assert "entity_analysis" in analysis
        assert "precision_scores" in analysis
        assert "risk_assessment" in analysis
        assert "recommendations" in analysis
        assert "outcome_projections" in analysis
        assert "confidence_metrics" in analysis

        # Check entity analysis
        entity_analysis = analysis["entity_analysis"]
        assert "gastric_system" in entity_analysis
        assert "tumor_unit" in entity_analysis
        assert "cellular_analysis" in entity_analysis

        # Check recommendations
        recommendations = analysis["recommendations"]
        assert "primary_treatment" in recommendations
        assert "targeted_therapy" in recommendations
        assert "monitoring" in recommendations

    def test_precision_scores_calculation(self):
        """Test precision scores are calculated correctly"""
        strategy = create_gastric_oncology_strategy()

        # Create minimal case for testing
        case = IntegratedCase(patient_id="P001", case_id="TEST001", age=65)

        gastric_system = GastricSystem(
            system_id="GS001",
            patient_id="P001",
            primary_region=AnatomicalRegion.ANTRUM,
            functional_status=GastricSystemStatus.NORMAL,
        )

        analysis = strategy["analyze_function"](
            case=case, gastric_system=gastric_system
        )

        precision_scores = analysis["precision_scores"]
        assert "overall_precision_score" in precision_scores
        assert "personalization_index" in precision_scores
        assert "evidence_strength" in precision_scores
        assert "actionability_score" in precision_scores

        # Scores should be numeric and within reasonable ranges
        assert 0 <= precision_scores["overall_precision_score"] <= 100
        assert 0 <= precision_scores["personalization_index"] <= 100


class TestEntityMappers:
    """Test entity mapper functions"""

    def test_gastric_system_to_dict(self):
        """Test converting gastric system to dictionary"""
        gastric_system = GastricSystem(
            system_id="GS001",
            patient_id="P001",
            primary_region=AnatomicalRegion.ANTRUM,
            functional_status=GastricSystemStatus.NORMAL,
            gastric_emptying_time=90.0,
        )

        data = gastric_system.model_dump()

        assert data["system_id"] == "GS001"
        assert data["primary_region"] == "antrum"
        assert data["functional_status"] == "normal"
        assert data["gastric_emptying_time"] == 90.0

    def test_tumor_unit_json_serialization(self):
        """Test tumor unit JSON serialization"""
        tumor_unit = TumorUnit(
            tumor_id="TU001",
            case_id="C001",
            patient_id="P001",
            t_stage=TumorStage.T3,
            n_stage=NodeStage.N1,
            m_stage=MetastasisStage.M0,
            histology_type=HistologyType.ADENOCARCINOMA,
            tumor_grade=TumorGrade.G2,
            primary_location=AnatomicalRegion.ANTRUM,
        )

        json_str = tumor_unit.model_dump_json()
        assert "tumor_id" in json_str
        assert "T3" in json_str
        assert "adenocarcinoma" in json_str


if __name__ == "__main__":
    pytest.main([__file__])
