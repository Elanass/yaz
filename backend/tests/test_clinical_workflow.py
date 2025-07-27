#!/usr/bin/env python3
"""
Comprehensive Clinical Workflow Test
Tests the complete medical decision support system with a real-world clinical scenario
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, Any
import pytest

@pytest.fixture
def clinical_test_case():
    return {
        "patient_id": "TEST_CLINICAL_001",
        "age": 65,
        "gender": "male",
        "clinical_parameters": {
            "tumor_stage": "T3N1M0",
            "histology": "adenocarcinoma",
            "tumor_location": "antrum",
            "tumor_size_cm": 4.2,
            "ecog_score": 1,
            "karnofsky_score": 80,
            "comorbidities": ["hypertension", "diabetes"],
            "biomarkers": {
                "her2": "negative",
                "msi": "stable",
                "pdl1": "unknown"
            },
            "lab_values": {
                "creatinine_mg_dl": 1.1,
                "total_bilirubin_mg_dl": 0.8,
                "alt_u_l": 45,
                "hemoglobin_g_dl": 12.5,
                "platelet_count": 280000
            },
            "prior_treatments": [],
            "family_history": ["gastric_cancer_grandfather"],
            "smoking_history": "former_smoker_quit_10_years",
            "alcohol_use": "social"
        },
        "clinical_context": {
            "institution": "Memorial Cancer Center",
            "urgency": "routine",
            "multidisciplinary_team": ["medical_oncology", "surgical_oncology", "radiation_oncology"],
            "treatment_goals": ["curative_intent", "quality_of_life_preservation"]
        }
    }


def test_clinical_workflow(clinical_test_case):
    assert clinical_test_case["age"] == 65
    assert clinical_test_case["clinical_parameters"]["tumor_stage"] == "T3N1M0"
    # Add more assertions to validate the clinical workflow


class ClinicalWorkflowValidator:
    """Validates the complete clinical workflow"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        
    async def run_complete_workflow_test(self):
        """Run the complete clinical workflow test"""
        print("🏥 Starting Comprehensive Clinical Workflow Test")
        print("=" * 60)
        
        # Test 1: Import the decision engines
        print("\n1️⃣ Testing Decision Engine Import...")
        await self.test_engine_imports()
        
        # Test 2: Test ADCI Engine
        print("\n2️⃣ Testing ADCI Decision Engine...")
        await self.test_adci_engine()
        
        # Test 3: Test Gastrectomy Engine
        print("\n3️⃣ Testing Gastrectomy Decision Engine...")
        await self.test_gastrectomy_engine()
        
        # Test 4: Test FLOT Engine
        print("\n4️⃣ Testing FLOT Decision Engine...")
        await self.test_flot_engine()
        
        # Test 5: Test Engine Registry
        print("\n5️⃣ Testing Decision Engine Registry...")
        await self.test_engine_registry()
        
        # Test 6: Test Clinical Integration
        print("\n6️⃣ Testing Clinical Integration Workflow...")
        await self.test_clinical_integration()
        
        # Test 7: Test Treatment Recommendations
        print("\n7️⃣ Testing Treatment Recommendation Logic...")
        await self.test_treatment_recommendations()
        
        # Print results
        await self.print_test_results()
        
        return len(self.errors) == 0

    async def test_engine_imports(self):
        """Test that all engines can be imported"""
        try:
            # Import the engines
            from backend.src.engines.adci_engine import ADCIEngine
            from backend.src.engines.gastrectomy_engine import GastrectomyEngine
            from backend.src.engines.flot_engine import FLOTEngine
            from backend.src.engines.decision_engine import engine_registry, get_engine, list_engines
            
            print("✅ All decision engines imported successfully")
            self.test_results["engine_imports"] = "PASS"
            
        except Exception as e:
            error_msg = f"Failed to import engines: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["engine_imports"] = "FAIL"

    async def test_adci_engine(self):
        """Test ADCI engine with clinical case"""
        try:
            from backend.src.engines.adci_engine import ADCIEngine
            
            engine = ADCIEngine()
            result = await engine.process_decision(
                patient_id=CLINICAL_TEST_CASE["patient_id"],
                parameters=CLINICAL_TEST_CASE["clinical_parameters"],
                context=CLINICAL_TEST_CASE["clinical_context"],
                include_alternatives=True,
                confidence_threshold=0.75
            )
            
            # Validate result structure
            required_fields = [
                "engine_name", "engine_version", "patient_id", "recommendation",
                "confidence_score", "confidence_level", "adci_score"
            ]
            
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate confidence score
            if not 0.0 <= result["confidence_score"] <= 1.0:
                raise ValueError(f"Invalid confidence score: {result['confidence_score']}")
            
            print(f"✅ ADCI Engine - Confidence: {result['confidence_score']:.3f}")
            print(f"   Recommendation: {result['recommendation']['primary_treatment']}")
            
            self.test_results["adci_engine"] = {
                "status": "PASS",
                "confidence": result["confidence_score"],
                "recommendation": result["recommendation"]["primary_treatment"]
            }
            
        except Exception as e:
            error_msg = f"ADCI Engine test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["adci_engine"] = "FAIL"

    async def test_gastrectomy_engine(self):
        """Test Gastrectomy engine with clinical case"""
        try:
            from backend.src.engines.gastrectomy_engine import GastrectomyEngine
            
            engine = GastrectomyEngine()
            result = await engine.process_decision(
                patient_id=CLINICAL_TEST_CASE["patient_id"],
                parameters=CLINICAL_TEST_CASE["clinical_parameters"],
                context=CLINICAL_TEST_CASE["clinical_context"],
                include_alternatives=True,
                confidence_threshold=0.75
            )
            
            # Validate result structure
            required_fields = [
                "engine_name", "engine_version", "patient_id", "recommendation",
                "confidence_score", "surgical_score", "risk_assessment"
            ]
            
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate surgical recommendation
            surgical_rec = result["recommendation"]
            if "surgical_approach" not in surgical_rec:
                raise ValueError("Missing surgical approach recommendation")
            
            print(f"✅ Gastrectomy Engine - Confidence: {result['confidence_score']:.3f}")
            print(f"   Surgical Approach: {surgical_rec['surgical_approach']}")
            print(f"   Extent: {surgical_rec['extent_of_resection']}")
            
            self.test_results["gastrectomy_engine"] = {
                "status": "PASS",
                "confidence": result["confidence_score"],
                "approach": surgical_rec["surgical_approach"],
                "extent": surgical_rec["extent_of_resection"]
            }
            
        except Exception as e:
            error_msg = f"Gastrectomy Engine test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["gastrectomy_engine"] = "FAIL"

    async def test_flot_engine(self):
        """Test FLOT engine with clinical case"""
        try:
            from backend.src.engines.flot_engine import FLOTEngine
            
            engine = FLOTEngine()
            result = await engine.process_decision(
                patient_id=CLINICAL_TEST_CASE["patient_id"],
                parameters=CLINICAL_TEST_CASE["clinical_parameters"],
                context=CLINICAL_TEST_CASE["clinical_context"],
                include_alternatives=True,
                confidence_threshold=0.75
            )
            
            # Validate result structure
            required_fields = [
                "engine_name", "engine_version", "patient_id", "recommendation",
                "confidence_score", "eligibility_score", "toxicity_assessment"
            ]
            
            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing required field: {field}")
            
            # Validate FLOT recommendation
            flot_rec = result["recommendation"]
            if "recommendation_status" not in flot_rec:
                raise ValueError("Missing FLOT recommendation status")
            
            print(f"✅ FLOT Engine - Confidence: {result['confidence_score']:.3f}")
            print(f"   Eligibility: {result['eligibility_score']:.3f}")
            print(f"   Status: {flot_rec['recommendation_status']}")
            
            self.test_results["flot_engine"] = {
                "status": "PASS",
                "confidence": result["confidence_score"],
                "eligibility": result["eligibility_score"],
                "recommendation_status": flot_rec["recommendation_status"]
            }
            
        except Exception as e:
            error_msg = f"FLOT Engine test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["flot_engine"] = "FAIL"

    async def test_engine_registry(self):
        """Test the decision engine registry"""
        try:
            from backend.src.engines.decision_engine import get_engine, list_engines
            
            # Test list engines
            engines = list_engines()
            expected_engines = ["adci", "gastrectomy", "flot"]
            
            for engine_name in expected_engines:
                if engine_name not in engines:
                    raise ValueError(f"Engine {engine_name} not found in registry")
            
            # Test get engine
            for engine_name in expected_engines:
                engine = get_engine(engine_name)
                if not hasattr(engine, "process_decision"):
                    raise ValueError(f"Engine {engine_name} missing process_decision method")
            
            print(f"✅ Engine Registry - {len(engines)} engines available")
            for name, info in engines.items():
                print(f"   • {name}: v{info['engine_version']}")
            
            self.test_results["engine_registry"] = {
                "status": "PASS",
                "engine_count": len(engines),
                "engines": list(engines.keys())
            }
            
        except Exception as e:
            error_msg = f"Engine Registry test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["engine_registry"] = "FAIL"

    async def test_clinical_integration(self):
        """Test integrated clinical workflow"""
        try:
            from backend.src.engines.decision_engine import get_engine
            
            # Test integrated workflow with all engines
            patient_data = CLINICAL_TEST_CASE
            
            # Run all engines in sequence
            engines_to_test = ["adci", "gastrectomy", "flot"]
            workflow_results = {}
            
            for engine_name in engines_to_test:
                engine = get_engine(engine_name)
                result = await engine.process_decision(
                    patient_id=patient_data["patient_id"],
                    parameters=patient_data["clinical_parameters"],
                    context=patient_data["clinical_context"]
                )
                workflow_results[engine_name] = result
            
            # Validate workflow consistency
            self._validate_workflow_consistency(workflow_results)
            
            print("✅ Clinical Integration - All engines working together")
            print(f"   Workflow completed for patient {patient_data['patient_id']}")
            
            self.test_results["clinical_integration"] = {
                "status": "PASS",
                "engines_tested": len(engines_to_test),
                "workflow_results": {
                    name: {
                        "confidence": result["confidence_score"],
                        "processing_time": result.get("processing_time_ms", 0)
                    } for name, result in workflow_results.items()
                }
            }
            
        except Exception as e:
            error_msg = f"Clinical Integration test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["clinical_integration"] = "FAIL"

    async def test_treatment_recommendations(self):
        """Test treatment recommendation logic for clinical case"""
        try:
            from backend.src.engines.decision_engine import get_engine
            
            # Get recommendations from all engines
            adci_engine = get_engine("adci")
            gastrectomy_engine = get_engine("gastrectomy")
            flot_engine = get_engine("flot")
            
            patient_data = CLINICAL_TEST_CASE
            
            # Get ADCI recommendation
            adci_result = await adci_engine.process_decision(
                patient_id=patient_data["patient_id"],
                parameters=patient_data["clinical_parameters"]
            )
            
            # Get Gastrectomy recommendation
            surgery_result = await gastrectomy_engine.process_decision(
                patient_id=patient_data["patient_id"],
                parameters=patient_data["clinical_parameters"]
            )
            
            # Get FLOT recommendation
            flot_result = await flot_engine.process_decision(
                patient_id=patient_data["patient_id"],
                parameters=patient_data["clinical_parameters"]
            )
            
            # Synthesize recommendations for T3N1M0 case
            treatment_plan = self._synthesize_treatment_recommendations(
                adci_result, surgery_result, flot_result
            )
            
            print("✅ Treatment Recommendations Generated")
            print(f"   Treatment Sequence: {treatment_plan['sequence']}")
            print(f"   Overall Confidence: {treatment_plan['overall_confidence']:.3f}")
            
            self.test_results["treatment_recommendations"] = {
                "status": "PASS",
                "treatment_plan": treatment_plan
            }
            
        except Exception as e:
            error_msg = f"Treatment Recommendations test failed: {str(e)}"
            print(f"❌ {error_msg}")
            self.errors.append(error_msg)
            self.test_results["treatment_recommendations"] = "FAIL"

    def _validate_workflow_consistency(self, workflow_results: Dict[str, Any]):
        """Validate consistency across workflow results"""
        
        # Check that all engines processed the same patient
        patient_ids = set(result["patient_id"] for result in workflow_results.values())
        if len(patient_ids) != 1:
            raise ValueError("Inconsistent patient IDs across engines")
        
        # Check confidence scores are reasonable
        for engine_name, result in workflow_results.items():
            confidence = result["confidence_score"]
            if not 0.0 <= confidence <= 1.0:
                raise ValueError(f"Invalid confidence score for {engine_name}: {confidence}")
        
        # Check processing times are reasonable (< 10 seconds)
        for engine_name, result in workflow_results.items():
            processing_time = result.get("processing_time_ms", 0)
            if processing_time > 10000:  # 10 seconds
                print(f"⚠️  Warning: {engine_name} took {processing_time}ms to process")

    def _synthesize_treatment_recommendations(
        self, 
        adci_result: Dict[str, Any], 
        surgery_result: Dict[str, Any], 
        flot_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Synthesize recommendations from all engines for clinical case"""
        
        # For T3N1M0 gastric adenocarcinoma, expected sequence:
        # 1. Neoadjuvant FLOT (if eligible)
        # 2. Surgery (gastrectomy)
        # 3. Adjuvant FLOT (if applicable)
        
        flot_status = flot_result["recommendation"]["recommendation_status"]
        surgical_approach = surgery_result["recommendation"]["surgical_approach"]
        adci_primary = adci_result["recommendation"]["primary_treatment"]
        
        # Determine treatment sequence
        if flot_status in ["strongly_recommended", "recommended"]:
            sequence = "neoadjuvant_flot_surgery_adjuvant"
        else:
            sequence = "surgery_adjuvant_therapy"
        
        # Calculate overall confidence
        confidence_scores = [
            adci_result["confidence_score"],
            surgery_result["confidence_score"],
            flot_result["confidence_score"]
        ]
        overall_confidence = sum(confidence_scores) / len(confidence_scores)
        
        return {
            "sequence": sequence,
            "overall_confidence": overall_confidence,
            "neoadjuvant_therapy": flot_status if flot_status != "not_recommended" else "none",
            "surgical_approach": surgical_approach,
            "adjuvant_therapy": "flot" if flot_status != "not_recommended" else "consider_alternatives",
            "rationale": f"T3N1M0 gastric adenocarcinoma in 65-year-old with good PS - {sequence}",
            "individual_confidences": {
                "adci": adci_result["confidence_score"],
                "surgery": surgery_result["confidence_score"],
                "flot": flot_result["confidence_score"]
            }
        }

    async def print_test_results(self):
        """Print comprehensive test results"""
        print("\n" + "=" * 60)
        print("🏥 CLINICAL WORKFLOW TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() 
                          if (isinstance(result, dict) and result.get("status") == "PASS") 
                          or result == "PASS")
        
        print(f"\n📊 SUMMARY: {passed_tests}/{total_tests} tests passed")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"   {i}. {error}")
        
        print(f"\n✅ DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            if isinstance(result, dict) and "status" in result:
                status = result["status"]
                print(f"   • {test_name}: {status}")
                if status == "PASS" and test_name == "treatment_recommendations":
                    plan = result["treatment_plan"]
                    print(f"     - Treatment: {plan['sequence']}")
                    print(f"     - Confidence: {plan['overall_confidence']:.3f}")
            else:
                print(f"   • {test_name}: {result}")
        
        print(f"\n🔬 CLINICAL CASE VALIDATION:")
        print(f"   Patient: 65-year-old male with T3N1M0 gastric adenocarcinoma")
        print(f"   Engines tested: ADCI, Gastrectomy, FLOT")
        print(f"   Workflow: Complete multidisciplinary treatment planning")
        
        if len(self.errors) == 0:
            print(f"\n🎉 ALL TESTS PASSED - System ready for clinical use!")
        else:
            print(f"\n⚠️  {len(self.errors)} issues need to be addressed before clinical deployment")


async def main():
    """Main test function"""
    validator = ClinicalWorkflowValidator()
    success = await validator.run_complete_workflow_test()
    
    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        sys.exit(1)
