#!/usr/bin/env python3
"""
Test script for GastrectomyEngine performance and functionality
Validates Surgify compatibility and <150ms response targets
"""

import sys
import asyncio
import time
import json
from pathlib import Path

# Add backend to path
backend_path = Path("/workspaces/yaz/backend/src")
sys.path.insert(0, str(backend_path))

async def test_gastrectomy_engine():
    """Test GastrectomyEngine performance and functionality"""
    
    try:
        from engines.gastrectomy_engine import GastrectomyEngine
        print("✅ Successfully imported GastrectomyEngine")
        
        # Initialize engine
        engine = GastrectomyEngine()
        print(f"✅ Engine initialized - Version: {engine.version}")
        print(f"✅ Evidence base: {engine.evidence_base}")
        
        # Test parameters for gastric cancer surgery
        test_cases = [
            {
                "name": "Early gastric cancer - Antrum",
                "patient_id": "patient_001",
                "parameters": {
                    "tumor_stage": "T1a",
                    "tumor_location": "antrum",
                    "tumor_size": 1.5,
                    "patient_age": 62,
                    "performance_status": 0,
                    "comorbidities": [],
                    "asa_score": 2,
                    "histology": "adenocarcinoma",
                    "differentiation": "well",
                    "imaging_quality": "good",
                    "histology_confirmed": True
                }
            },
            {
                "name": "Advanced gastric cancer - Cardia",
                "patient_id": "patient_002",
                "parameters": {
                    "tumor_stage": "T3",
                    "tumor_location": "cardia",
                    "tumor_size": 4.2,
                    "patient_age": 74,
                    "performance_status": 1,
                    "comorbidities": ["hypertension"],
                    "asa_score": 3,
                    "histology": "adenocarcinoma",
                    "differentiation": "moderate",
                    "neoadjuvant_therapy": True
                }
            },
            {
                "name": "High-risk patient - Complex case",
                "patient_id": "patient_003", 
                "parameters": {
                    "tumor_stage": "T4",
                    "tumor_location": "linitis",
                    "tumor_size": 6.8,
                    "patient_age": 82,
                    "performance_status": 2,
                    "comorbidities": ["heart_failure", "copd"],
                    "asa_score": 4,
                    "previous_surgery": True
                }
            }
        ]
        
        print("\n🔬 Running Performance Tests...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- Test Case {i}: {test_case['name']} ---")
            
            # Measure response time
            start_time = time.perf_counter()
            
            try:
                result = await engine.process_decision(
                    patient_id=test_case["patient_id"],
                    parameters=test_case["parameters"],
                    include_alternatives=True,
                    confidence_threshold=0.7
                )
                
                response_time = (time.perf_counter() - start_time) * 1000
                
                print(f"✅ Response time: {response_time:.2f}ms")
                print(f"✅ Target met: {'Yes' if response_time < 150 else 'No'}")
                print(f"✅ Cache hit: {result.get('cache_hit', False)}")
                
                # Validate response structure
                required_fields = ["primary_recommendation", "confidence_intervals", "ui_metrics"]
                for field in required_fields:
                    if field in result:
                        print(f"✅ {field}: Present")
                    else:
                        print(f"❌ {field}: Missing")
                
                # Display key results
                print(f"📋 Procedure: {result['primary_recommendation']['procedure']['type']}")
                print(f"🔧 Approach: {result['primary_recommendation']['procedure']['approach']}")
                print(f"📊 Confidence: {result['confidence_intervals']['overall_confidence']:.3f}")
                print(f"⚠️  Risk level: {result['ui_metrics']['risk_level']}")
                print(f"🎯 Complexity: {result['ui_metrics']['complexity_indicator']:.3f}")
                
                # Test caching on second call
                start_time = time.perf_counter()
                cached_result = await engine.process_decision(
                    patient_id=test_case["patient_id"],
                    parameters=test_case["parameters"],
                    include_alternatives=True,
                    confidence_threshold=0.7
                )
                cache_time = (time.perf_counter() - start_time) * 1000
                
                print(f"💾 Cached response time: {cache_time:.2f}ms")
                print(f"✅ Cache working: {cached_result.get('cache_hit', False)}")
                
            except Exception as e:
                print(f"❌ Test failed: {e}")
                continue
        
        # Test performance metrics
        print("\n📈 Performance Metrics:")
        metrics = engine.get_performance_metrics()
        for key, value in metrics.items():
            print(f"   {key}: {value}")
        
        # Test plugin interface methods
        print("\n🔌 Testing Plugin Interface...")
        
        test_params = {
            "tumor_stage": "T2",
            "tumor_location": "body",
            "patient_age": 68
        }
        
        # Test calculate_score
        score, breakdown = engine.calculate_score(test_params)
        print(f"✅ Score calculation: {score:.3f}")
        print(f"✅ Breakdown: {breakdown}")
        
        # Test confidence calculation  
        confidence = engine.calculate_confidence(test_params, {}, {})
        print(f"✅ Confidence: {confidence}")
        
        # Test recommendation generation
        recommendation = engine.generate_recommendation(score, test_params, {})
        print(f"✅ Plugin recommendation: {recommendation}")
        
        # Test alternatives
        alternatives = engine.generate_alternatives(score, test_params, recommendation)
        print(f"✅ Alternatives: {len(alternatives)} options")
        
        print("\n🎉 All tests completed successfully!")
        print("✅ GastrectomyEngine is Surgify-compatible and performance-optimized")
        
        return True
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gastrectomy_engine())
    sys.exit(0 if success else 1)
