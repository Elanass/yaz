"""
Minimal Test Suite for Core Surgify Functionality
"""

import sys
from pathlib import Path

import pandas as pd
import pytest


# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from surge.core.cache import cache_manager
from surge.core.domains import domain_registry


def test_domain_registry():
    """Test domain plugin system basics"""
    domains = domain_registry.list_domains()
    assert len(domains) > 0, "No domains loaded"

    # Test surgery domain exists
    surgery = domain_registry.get_domain("surgery")
    assert surgery is not None, "Surgery domain not found"


def test_surgery_domain_detection():
    """Test surgery domain detection"""
    surgery = domain_registry.get_domain("surgery")

    # Medical columns should have high confidence
    medical_cols = ["patient_id", "tnm_stage", "survival_months", "procedure_type"]
    confidence = surgery.schema_detect(medical_cols)
    assert confidence > 0.3, f"Low confidence for medical data: {confidence}"

    # Non-medical columns should have low confidence
    random_cols = ["random_field", "unrelated_data"]
    confidence = surgery.schema_detect(random_cols)
    assert confidence < 0.5, f"High confidence for non-medical data: {confidence}"


def test_data_processing():
    """Test basic data processing"""
    # Create minimal test data
    test_data = pd.DataFrame(
        {
            "patient_id": ["P001", "P002", "P003"],
            "age": [65, 70, 58],
            "tnm_stage": ["T2N0M0", "T3N1M0", "T1N0M0"],
            "survival_months": [36, 24, 48],
        }
    )

    surgery = domain_registry.get_domain("surgery")

    # Test parsing
    parsed = surgery.parse(test_data)
    assert "total_cases" in parsed
    assert parsed["total_cases"] == 3

    # Test stats
    stats = surgery.stats(test_data)
    assert "case_count" in stats
    assert stats["case_count"] == 3

    # Test insights
    insights = surgery.insights(test_data)
    assert isinstance(insights, list)
    assert len(insights) > 0


def test_cache_manager():
    """Test cache functionality"""
    # Test basic operations
    cache_manager.set("test_key", {"data": "test"})
    result = cache_manager.get("test_key")
    assert result == {"data": "test"}

    # Test status
    status = cache_manager.get_status()
    assert "connected" in status
    assert "metrics" in status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
