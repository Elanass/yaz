"""
Tests for the new medical modules
"""

import pytest

from surge.core.plugins import DomainType, get_plugin_registry
from surge.modules import (
    ChemoFLOTModule,
    FLOTCase,
    GastricSurgeryCase,
    GastricSurgeryModule,
    IntegratedCase,
    PrecisionDecisionEngine,
    analyze_flot_cohort,
    analyze_gastric_surgery_cohort,
    analyze_precision_decisions,
)


class TestGastricSurgeryModule:
    """Test gastric surgery module functionality"""

    def test_gastric_surgery_case_creation(self):
        """Test creation of gastric surgery case"""
        case = GastricSurgeryCase(
            patient_id="P001",
            case_id="GC001",
            tumor_stage="T2",
            node_stage="N0",
            metastasis_stage="M0",
            histology="adenocarcinoma",
            gastrectomy_type="subtotal_gastrectomy",
            surgical_approach="laparoscopic",
        )

        assert case.patient_id == "P001"
        assert case.tumor_stage == "T2"
        assert case.surgical_approach == "laparoscopic"

    def test_gastric_surgery_analysis(self):
        """Test gastric surgery analysis"""
        module = GastricSurgeryModule()

        case = GastricSurgeryCase(
            patient_id="P001",
            case_id="GC001",
            tumor_stage="T2",
            node_stage="N1",
            metastasis_stage="M0",
            histology="adenocarcinoma",
            gastrectomy_type="subtotal_gastrectomy",
            surgical_approach="laparoscopic",
        )

        analysis = module.analyze_case(case)

        assert analysis.case_id == "GC001"
        assert 0 <= analysis.surgical_risk_score <= 100
        assert analysis.confidence_score > 0
        assert analysis.recommended_approach in [
            "open",
            "laparoscopic",
            "robotic",
            "endoscopic",
        ]

    def test_cohort_analysis(self):
        """Test gastric surgery cohort analysis"""
        cases = []

        for i in range(5):
            case = GastricSurgeryCase(
                patient_id=f"P00{i + 1}",
                case_id=f"GC00{i + 1}",
                tumor_stage="T2",
                node_stage="N0",
                metastasis_stage="M0",
                histology="adenocarcinoma",
                gastrectomy_type="subtotal_gastrectomy",
                surgical_approach="laparoscopic",
            )
            cases.append(case)

        analysis = analyze_gastric_surgery_cohort(cases)

        assert analysis["cohort_summary"]["total_cases"] == 5
        assert "staging_distribution" in analysis
        assert "histology_distribution" in analysis


class TestChemoFLOTModule:
    """Test FLOT chemotherapy module functionality"""

    def test_flot_case_creation(self):
        """Test creation of FLOT case"""
        case = FLOTCase(
            patient_id="P001",
            case_id="FLOT001",
            initial_t_stage="T3",
            initial_n_stage="N1",
            initial_m_stage="M0",
            planned_cycles=8,
            completed_cycles=8,
            phase="complete",
        )

        assert case.patient_id == "P001"
        assert case.planned_cycles == 8
        assert case.completed_cycles == 8

    def test_flot_analysis(self):
        """Test FLOT analysis"""
        module = ChemoFLOTModule()

        case = FLOTCase(
            patient_id="P001",
            case_id="FLOT001",
            initial_t_stage="T3",
            initial_n_stage="N1",
            initial_m_stage="M0",
            planned_cycles=8,
            completed_cycles=6,
            phase="interrupted",
        )

        analysis = module.analyze_flot_case(case)

        assert analysis.case_id == "FLOT001"
        assert 0 <= analysis.completion_rate <= 1
        assert 0 <= analysis.adherence_score <= 100
        assert analysis.confidence_score > 0

    def test_flot_cohort_analysis(self):
        """Test FLOT cohort analysis"""
        cases = []

        for i in range(3):
            case = FLOTCase(
                patient_id=f"P00{i + 1}",
                case_id=f"FLOT00{i + 1}",
                initial_t_stage="T2",
                initial_n_stage="N0",
                initial_m_stage="M0",
                planned_cycles=8,
                completed_cycles=8,
                phase="complete",
            )
            cases.append(case)

        analysis = analyze_flot_cohort(cases)

        assert analysis["cohort_summary"]["total_cases"] == 3
        assert "efficacy_metrics" in analysis
        assert "toxicity_profile" in analysis


class TestPrecisionDecisionEngine:
    """Test precision decision engine functionality"""

    def test_integrated_case_creation(self):
        """Test creation of integrated case"""
        gastric_case = GastricSurgeryCase(
            patient_id="P001",
            case_id="GC001",
            tumor_stage="T2",
            node_stage="N0",
            metastasis_stage="M0",
            histology="adenocarcinoma",
            gastrectomy_type="subtotal_gastrectomy",
            surgical_approach="laparoscopic",
        )

        flot_case = FLOTCase(
            patient_id="P001",
            case_id="FLOT001",
            initial_t_stage="T2",
            initial_n_stage="N0",
            initial_m_stage="M0",
            planned_cycles=8,
            completed_cycles=8,
            phase="complete",
        )

        integrated_case = IntegratedCase(
            patient_id="P001",
            case_id="INT001",
            gastric_surgery_case=gastric_case,
            flot_case=flot_case,
            age=65,
            performance_status=0,
        )

        assert integrated_case.patient_id == "P001"
        assert integrated_case.gastric_surgery_case is not None
        assert integrated_case.flot_case is not None

    def test_precision_analysis(self):
        """Test precision decision analysis"""
        engine = PrecisionDecisionEngine()

        integrated_case = IntegratedCase(
            patient_id="P001", case_id="INT001", age=65, performance_status=0
        )

        decision = engine.analyze_integrated_case(integrated_case)

        assert decision.case_id == "INT001"
        assert 0 <= decision.overall_risk_score <= 100
        assert 0 <= decision.confidence_score <= 1
        assert decision.decision_class in [
            "surgical_only",
            "neoadjuvant_surgery",
            "perioperative",
            "palliative",
            "surveillance",
        ]

    def test_precision_cohort_analysis(self):
        """Test precision decision cohort analysis"""
        cases = []

        for i in range(3):
            case = IntegratedCase(
                patient_id=f"P00{i + 1}",
                case_id=f"INT00{i + 1}",
                age=60 + i * 5,
                performance_status=0,
            )
            cases.append(case)

        analysis = analyze_precision_decisions(cases)

        assert analysis["cohort_summary"]["total_cases"] == 3
        assert "decision_distribution" in analysis
        assert "quality_metrics" in analysis


class TestPluginSystem:
    """Test plugin system functionality"""

    def test_plugin_registry(self):
        """Test plugin registry"""
        registry = get_plugin_registry()
        plugins = registry.list_plugins()

        # Should have at least the built-in plugins
        assert len(plugins) >= 3

        # Check for specific plugins
        plugin_names = [p.name for p in plugins]
        assert "gastric_surgery" in plugin_names
        assert "chemo_flot" in plugin_names
        assert "precision_engine" in plugin_names

    def test_plugin_capabilities(self):
        """Test plugin capabilities"""
        registry = get_plugin_registry()

        gastric_plugin = registry.get_plugin("gastric_surgery")
        assert gastric_plugin is not None

        capabilities = gastric_plugin.get_capabilities()
        assert "case_analysis" in capabilities
        assert "risk_assessment" in capabilities

    def test_domain_filtering(self):
        """Test domain-based plugin filtering"""
        registry = get_plugin_registry()

        surgery_plugins = registry.get_plugins_by_domain(DomainType.SURGERY)
        oncology_plugins = registry.get_plugins_by_domain(DomainType.ONCOLOGY)

        assert len(surgery_plugins) >= 1
        assert len(oncology_plugins) >= 1


class TestModuleIntegration:
    """Test integration between modules"""

    def test_end_to_end_analysis(self):
        """Test end-to-end analysis workflow"""
        # Create sample case
        gastric_case = GastricSurgeryCase(
            patient_id="P001",
            case_id="GC001",
            tumor_stage="T3",
            node_stage="N1",
            metastasis_stage="M0",
            histology="signet_ring",
            gastrectomy_type="total_gastrectomy",
            surgical_approach="laparoscopic",
        )

        flot_case = FLOTCase(
            patient_id="P001",
            case_id="FLOT001",
            initial_t_stage="T3",
            initial_n_stage="N1",
            initial_m_stage="M0",
            planned_cycles=8,
            completed_cycles=8,
            phase="complete",
        )

        # Analyze with individual modules
        gastric_module = GastricSurgeryModule()
        gastric_analysis = gastric_module.analyze_case(gastric_case)

        flot_module = ChemoFLOTModule()
        flot_analysis = flot_module.analyze_flot_case(flot_case)

        # Create integrated case and analyze
        integrated_case = IntegratedCase(
            patient_id="P001",
            case_id="INT001",
            gastric_surgery_case=gastric_case,
            flot_case=flot_case,
            age=65,
            performance_status=1,
        )

        precision_engine = PrecisionDecisionEngine()
        precision_decision = precision_engine.analyze_integrated_case(integrated_case)

        # Verify all analyses completed successfully
        assert gastric_analysis.case_id == "GC001"
        assert flot_analysis.case_id == "FLOT001"
        assert precision_decision.case_id == "INT001"

        # Verify integration worked
        assert precision_decision.surgical_risk > 0
        assert precision_decision.chemotherapy_risk > 0
        assert precision_decision.overall_risk_score > 0


# Test fixtures and data
@pytest.fixture
def sample_gastric_cases():
    """Sample gastric surgery cases for testing"""
    cases = []
    for i in range(5):
        case = GastricSurgeryCase(
            patient_id=f"P{i:03d}",
            case_id=f"GC{i:03d}",
            tumor_stage=["T1", "T2", "T3", "T4"][i % 4],
            node_stage=["N0", "N1", "N2"][i % 3],
            metastasis_stage="M0",
            histology=["adenocarcinoma", "signet_ring"][i % 2],
            gastrectomy_type=["subtotal_gastrectomy", "total_gastrectomy"][i % 2],
            surgical_approach=["laparoscopic", "open", "robotic"][i % 3],
        )
        cases.append(case)
    return cases


@pytest.fixture
def sample_flot_cases():
    """Sample FLOT cases for testing"""
    cases = []
    for i in range(3):
        case = FLOTCase(
            patient_id=f"P{i:03d}",
            case_id=f"FLOT{i:03d}",
            initial_t_stage=["T2", "T3", "T4"][i],
            initial_n_stage=["N0", "N1", "N2"][i],
            initial_m_stage="M0",
            planned_cycles=8,
            completed_cycles=[8, 6, 8][i],
            phase=["complete", "interrupted", "complete"][i],
        )
        cases.append(case)
    return cases


def test_module_performance(sample_gastric_cases, sample_flot_cases):
    """Test module performance with sample data"""
    import time

    # Test gastric surgery module performance
    start_time = time.time()
    gastric_analysis = analyze_gastric_surgery_cohort(sample_gastric_cases)
    gastric_time = time.time() - start_time

    # Test FLOT module performance
    start_time = time.time()
    flot_analysis = analyze_flot_cohort(sample_flot_cases)
    flot_time = time.time() - start_time

    # Verify reasonable performance (should complete in < 1 second)
    assert gastric_time < 1.0
    assert flot_time < 1.0

    # Verify results
    assert gastric_analysis["cohort_summary"]["total_cases"] == 5
    assert flot_analysis["cohort_summary"]["total_cases"] == 3
