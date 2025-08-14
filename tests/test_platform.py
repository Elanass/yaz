#!/usr/bin/env python3
"""
Test Platform - Simple test for YAZ refactored platform
"""

import sys
import pytest
from pathlib import Path

# Add the workspace root to Python path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

def test_shared_components():
    """Test shared components work"""
    try:
        from shared.config import get_shared_config
        from shared.logging import get_logger
        from shared.database import init_database
        from shared.models import BaseResponse
        
        # Test configuration
        config = get_shared_config()
        assert config.app_name == "YAZ Healthcare Platform"
        
        # Test logging
        logger = get_logger("test")
        logger.info("Test logging works")
        
        # Test models
        response = BaseResponse(message="Test response")
        assert response.success is True
        
        print("✅ Shared components test passed")
        return True
        
    except Exception as e:
        print(f"❌ Shared components test failed: {e}")
        return False


def test_apps():
    """Test apps can be imported"""
    try:
        import sys
        sys.path.append('/workspaces/yaz')
        
        from apps.base_app import create_standard_app
        from config import get_enabled_apps
        
        # Test enabled apps
        apps = get_enabled_apps()
        assert len(apps) > 0
        print(f"✅ Found {len(apps)} enabled apps: {apps}")
        
        # Test app creation
        test_app = create_standard_app(
            "test", 
            "Test App", 
            "Test description",
            ["test_feature"]
        )
        assert test_app is not None
        print("✅ App creation test passed")
        
        # Test surge app specifically
        from apps.surge.app import create_app as create_surge_app
        surge_app = create_surge_app()
        assert surge_app is not None
        print("✅ Surge app creation test passed")
        
        return True
        
    except Exception as e:
        print(f"❌ Apps test failed: {e}")
        return False


def test_data_layer():
    """Test data layer works"""
    try:
        import sys
        sys.path.append('/workspaces/yaz')
        
        from data.models import User, Case
        from shared.database import Base
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Test model creation
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create test user
        user = User(email="test@example.com", name="Test User")
        session.add(user)
        session.commit()
        
        # Create test case
        case = Case(title="Test Case", user_id=user.id)
        session.add(case)
        session.commit()
        
        # Verify
        assert session.query(User).count() == 1
        assert session.query(Case).count() == 1
        
        session.close()
        print("✅ Data layer test passed")
        return True
        
    except Exception as e:
        print(f"❌ Data layer test failed: {e}")
        return False


def run_all_tests():
    """Run all platform tests"""
    print("🧪 Testing YAZ Refactored Platform")
    print("=" * 40)
    
    tests = [
        test_shared_components,
        test_apps,
        test_data_layer
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            failed += 1
        print()
    
    print("=" * 40)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Platform refactoring successful.")
        return True
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
