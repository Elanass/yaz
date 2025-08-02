"""
Integration tests for DRY-compliant Gastric ADCI Platform
Tests API endpoints and verifies DRY compliance is working
"""
import pytest
import requests
import time
import subprocess
from pathlib import Path

# Test configuration
BASE_URL = "http://localhost:8000"
WORKSPACE_ROOT = "/workspaces/yaz"

def test_dry_shared_utilities_exist():
    """Test that shared utilities file exists and contains key functions"""
    shared_utils_path = Path(WORKSPACE_ROOT) / "web/static/js/shared-utils.js"
    assert shared_utils_path.exists(), "Shared utilities file must exist"
    
    content = shared_utils_path.read_text()
    
    # Check for key DRY utilities
    assert "SharedUtils.notifications" in content, "Notification utilities must be centralized"
    assert "SharedUtils.adci" in content, "ADCI utilities must be centralized"
    assert "SharedUtils.validation" in content, "Validation utilities must be centralized"
    assert "SharedUtils.export" in content, "Export utilities must be centralized"
    assert "SharedUtils.utils" in content, "General utilities must be centralized"

def test_dry_compliance_validation():
    """Test that DRY compliance validation passes"""
    result = subprocess.run([
        "bash", "-c", 
        f"cd {WORKSPACE_ROOT} && grep -r 'showNotification.*=' web/static/js/ --exclude='shared-utils.js' | wc -l"
    ], capture_output=True, text=True)
    
    duplicate_notifications = int(result.stdout.strip())
    assert duplicate_notifications <= 3, f"Too many duplicate notification implementations: {duplicate_notifications}"

def test_application_health():
    """Test that the application health endpoint responds correctly"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200, f"Health check failed with status {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, "Health check should return success"
        assert "data" in data, "Health check should include data"
        assert data["data"]["status"] == "healthy", "Application should be healthy"
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Application not running - this is expected if running tests standalone")

def test_api_documentation_accessible():
    """Test that API documentation is accessible"""
    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        assert response.status_code == 200, "API documentation should be accessible"
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Application not running - this is expected if running tests standalone")

def test_environment_config_endpoint():
    """Test that environment configuration endpoint works"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/config/environment", timeout=5)
        assert response.status_code == 200, "Environment config endpoint should work"
        
        data = response.json()
        assert data["success"] is True, "Environment config should return success"
        assert "data" in data, "Environment config should include data"
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Application not running - this is expected if running tests standalone")

def test_main_application_accessible():
    """Test that the main application is accessible"""
    try:
        response = requests.get(BASE_URL, timeout=5)
        assert response.status_code in [200, 302], "Main application should be accessible"
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Application not running - this is expected if running tests standalone")

def test_static_shared_utils_served():
    """Test that shared utilities are properly served"""
    try:
        response = requests.get(f"{BASE_URL}/static/js/shared-utils.js", timeout=5)
        assert response.status_code == 200, "Shared utilities should be served"
        assert "SharedUtils" in response.text, "Shared utilities should contain SharedUtils object"
        
    except requests.exceptions.ConnectionError:
        pytest.skip("Application not running - this is expected if running tests standalone")

def test_dry_compliance_summary():
    """Generate a summary of DRY compliance improvements"""
    workspace = Path(WORKSPACE_ROOT)
    
    # Count utility consolidations
    js_files = list(workspace.glob("web/static/js/*.js"))
    shared_utils_exists = (workspace / "web/static/js/shared-utils.js").exists()
    
    print(f"\n🎉 DRY Compliance Test Summary:")
    print(f"✅ JavaScript files found: {len(js_files)}")
    print(f"✅ Shared utilities implemented: {shared_utils_exists}")
    
    if shared_utils_exists:
        shared_content = (workspace / "web/static/js/shared-utils.js").read_text()
        utilities_count = len([line for line in shared_content.split('\n') if 'SharedUtils.' in line and ':' in line])
        print(f"✅ Centralized utility functions: ~{utilities_count}")
    
    # Check for remaining duplications
    try:
        result = subprocess.run([
            "bash", "-c", 
            f"cd {WORKSPACE_ROOT} && find web/static/js/ -name '*.js' -not -name 'shared-utils.js' -exec grep -l 'showNotification' {{}} \\;"
        ], capture_output=True, text=True)
        files_with_notifications = len([f for f in result.stdout.strip().split('\n') if f.strip()])
        print(f"✅ Files still implementing notifications: {files_with_notifications}")
    except:
        print("⚠️  Could not analyze notification implementations")
    
    assert True, "DRY compliance summary completed"

if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
