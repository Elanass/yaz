#!/usr/bin/env python3
"""
Domain Validation Script for Surgify Platform

This script validates all domain adapters and ensures they can perform
basic "hello world" operations to verify the multi-domain architecture.
"""

import sys
import os
from pathlib import Path
import json
import pandas as pd

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from surgify.core.domain_adapter import domain_registry, Domain


def test_hello_world():
    """Test basic hello world functionality for all domains"""
    print("🧪 Testing Domain Hello World Functionality")
    print("=" * 50)
    
    results = domain_registry.validate_all_domains()
    all_passed = True
    
    for domain, result in results.items():
        status = "✅ PASS" if result.get("status") == "operational" else "❌ FAIL"
        print(f"{status} {domain.upper()}: {result.get('message', 'Unknown status')}")
        
        if result.get("status") != "operational":
            all_passed = False
            print(f"   Error details: {result}")
    
    return all_passed


def test_data_processing():
    """Test data processing capabilities for each domain"""
    print("\n🔬 Testing Data Processing Pipeline")
    print("=" * 50)
    
    test_cases = {
        Domain.SURGERY: {
            "csv_data": pd.DataFrame({
                "patient_id": [1, 2, 3],
                "procedure": ["Appendectomy", "Gallbladder", "Hernia Repair"],
                "surgeon": ["Dr. Smith", "Dr. Jones", "Dr. Brown"],
                "outcome": ["Success", "Success", "Complication"],
                "los": [2, 3, 5]
            }),
            "dict_data": {
                "patient_id": "12345",
                "procedure": "Cardiac Surgery",
                "surgeon": "Dr. Heart",
                "outcome": "Success"
            },
            "text_data": "Patient underwent successful cardiac surgery procedure with excellent outcome."
        },
        Domain.LOGISTICS: {
            "csv_data": pd.DataFrame({
                "supplier": ["MedCorp", "HealthSupply", "SurgicalTools"],
                "product": ["Surgical Masks", "Gloves", "Scalpels"],
                "quantity": [1000, 500, 50],
                "cost": [299.99, 149.99, 799.99],
                "lead_time": [7, 14, 21]
            }),
            "dict_data": {
                "supplier": "MedCorp",
                "product": "Surgical Equipment",
                "quantity": 100,
                "cost": 5000.00
            },
            "text_data": "Medical supply shipment from MedCorp containing surgical equipment delivered on time."
        },
        Domain.INSURANCE: {
            "csv_data": pd.DataFrame({
                "member_id": ["M001", "M002", "M003"],
                "claim_amount": [1500.00, 2500.00, 899.99],
                "claim_status": ["Approved", "Pending", "Denied"],
                "policy_type": ["Basic", "Premium", "Basic"],
                "premium": [299.99, 499.99, 299.99]
            }),
            "dict_data": {
                "member_id": "M12345",
                "claim_amount": 3500.00,
                "claim_status": "Approved",
                "policy_type": "Premium"
            },
            "text_data": "Insurance claim for medical procedure has been approved and processed successfully."
        }
    }
    
    all_passed = True
    
    for domain, test_data in test_cases.items():
        print(f"\n🎯 Testing {domain.value.upper()} Domain")
        print("-" * 30)
        
        try:
            adapter = domain_registry.get_adapter(domain)
            
            # Test CSV processing
            csv_result = adapter.process_data(test_data["csv_data"])
            print(f"   ✅ CSV Processing: {csv_result.get('data_type', 'Unknown')}")
            
            # Test dict processing
            dict_result = adapter.process_data(test_data["dict_data"])
            print(f"   ✅ Dict Processing: {dict_result.get('data_type', 'Unknown')}")
            
            # Test text processing
            text_result = adapter.process_data(test_data["text_data"])
            print(f"   ✅ Text Processing: {text_result.get('data_type', 'Unknown')}")
            
            # Test deliverable generation
            deliverable = adapter.generate_deliverable(csv_result)
            print(f"   ✅ Deliverable: {deliverable.get('status', 'Unknown')}")
            
        except Exception as e:
            print(f"   ❌ Error testing {domain.value}: {e}")
            all_passed = False
    
    return all_passed


def test_domain_switching():
    """Test domain switching functionality"""
    print("\n🔄 Testing Domain Switching")
    print("=" * 50)
    
    try:
        # Test switching between domains
        for domain in Domain:
            domain_registry.set_current_domain(domain)
            current_adapter = domain_registry.get_current_adapter()
            
            if current_adapter and current_adapter.domain == domain:
                print(f"   ✅ Successfully switched to {domain.value}")
            else:
                print(f"   ❌ Failed to switch to {domain.value}")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ Error during domain switching: {e}")
        return False


def test_deliverable_generation():
    """Test deliverable generation for all domains"""
    print("\n📄 Testing Deliverable Generation")
    print("=" * 50)
    
    sample_data = {"test": "data", "timestamp": "2025-08-05"}
    all_passed = True
    
    for domain in Domain:
        try:
            adapter = domain_registry.get_adapter(domain)
            deliverable = adapter.generate_deliverable(sample_data, "test_template")
            
            if deliverable.get("status") == "generated":
                print(f"   ✅ {domain.value.upper()}: Deliverable generated successfully")
            else:
                print(f"   ❌ {domain.value.upper()}: Deliverable generation failed")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ {domain.value.upper()}: Error - {e}")
            all_passed = False
    
    return all_passed


def run_comprehensive_test():
    """Run all domain validation tests"""
    print("🧪 SURGIFY DOMAIN VALIDATION SUITE")
    print("=" * 50)
    print("Testing multi-domain architecture functionality\n")
    
    tests = [
        ("Hello World", test_hello_world),
        ("Data Processing", test_data_processing),
        ("Domain Switching", test_domain_switching),
        ("Deliverable Generation", test_deliverable_generation)
    ]
    
    results = {}
    all_passed = True
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            results[test_name] = False
            all_passed = False
    
    # Summary
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    overall_status = "✅ ALL TESTS PASSED" if all_passed else "❌ SOME TESTS FAILED"
    print(f"\n{overall_status}")
    
    if all_passed:
        print("\n🎉 Domain architecture is working correctly!")
        print("Ready for Phase 1.2: Universal CSV ingestion & analysis engine")
    else:
        print("\n⚠️ Please fix failing tests before proceeding to next phase")
    
    return all_passed


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
