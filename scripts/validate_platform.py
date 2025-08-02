#!/usr/bin/env python3
"""
Comprehensive Validation Script for Gastric ADCI Platform
Tests all environments: Local, P2P, and Multi-Cloud
"""

import os
import sys
import asyncio
import importlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

class PlatformValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_tests = 0
        
    def log_success(self, message: str):
        self.success_count += 1
        print(f"✅ {message}")
        
    def log_warning(self, message: str):
        self.warnings.append(message)
        print(f"⚠️  {message}")
        
    def log_error(self, message: str):
        self.errors.append(message)
        print(f"❌ {message}")
        
    def test_imports(self) -> bool:
        """Test that all critical imports work"""
        print("\n🔍 Testing Critical Imports...")
        self.total_tests += 6
        
        # Test core imports
        try:
            from core.config.environment import get_environment_config, DeploymentMode
            self.log_success("Core environment configuration imported")
        except ImportError as e:
            self.log_error(f"Failed to import environment config: {e}")
            return False
            
        try:
            from core.operators.specific_purpose.p2p_signaling import P2pSignalingOperator
            self.log_success("P2P signaling operator imported")
        except ImportError as e:
            self.log_error(f"Failed to import P2P operator: {e}")
            
        try:
            from web.components.interface import create_dynamic_layout
            self.log_success("Web interface components imported")
        except ImportError as e:
            self.log_error(f"Failed to import web components: {e}")
            
        try:
            import main
            self.log_success("Main application module imported")
        except ImportError as e:
            self.log_error(f"Failed to import main: {e}")
            
        try:
            from fastapi import FastAPI
            self.log_success("FastAPI imported")
        except ImportError as e:
            self.log_error(f"FastAPI not available: {e}")
            
        try:
            from fasthtml.common import Div, H1
            self.log_success("FastHTML imported")
        except ImportError as e:
            self.log_error(f"FastHTML not available: {e}")
            
        return len(self.errors) == 0
        
    def test_environment_configs(self) -> bool:
        """Test environment configurations"""
        print("\n🌍 Testing Environment Configurations...")
        self.total_tests += 3
        
        try:
            from core.config.environment import get_environment_config, reset_environment_config, DeploymentMode
            
            # Test Local mode
            os.environ['GASTRIC_ADCI_ENV'] = 'local'
            reset_environment_config()  # Reset to pick up new env var
            config = get_environment_config()
            if config.get_mode() == DeploymentMode.LOCAL:
                self.log_success("Local environment configuration works")
            else:
                self.log_error("Local environment configuration failed")
                
            # Test P2P mode
            os.environ['GASTRIC_ADCI_ENV'] = 'p2p'
            reset_environment_config()  # Reset to pick up new env var
            config = get_environment_config()
            if config.get_mode() == DeploymentMode.P2P:
                self.log_success("P2P environment configuration works")
            else:
                self.log_error("P2P environment configuration failed")
                
            # Test Multi-cloud mode
            os.environ['GASTRIC_ADCI_ENV'] = 'multicloud'
            reset_environment_config()  # Reset to pick up new env var
            config = get_environment_config()
            if config.get_mode() == DeploymentMode.MULTICLOUD:
                self.log_success("Multi-cloud environment configuration works")
            else:
                self.log_error("Multi-cloud environment configuration failed")
                
            # Reset to original environment
            os.environ['GASTRIC_ADCI_ENV'] = 'local'  # Default for tests
            reset_environment_config()
                
        except Exception as e:
            self.log_error(f"Environment configuration test failed: {e}")
            # Reset to original environment even on error
            os.environ['GASTRIC_ADCI_ENV'] = 'local'
            reset_environment_config()
            
        return len(self.errors) == 0
        
    async def test_p2p_operator(self) -> bool:
        """Test P2P signaling operator"""
        print("\n🔗 Testing P2P Signaling Operator...")
        self.total_tests += 3
        
        try:
            from core.operators.specific_purpose.p2p_signaling import P2pSignalingOperator
            
            # Create operator instance
            operator = P2pSignalingOperator()
            self.log_success("P2P operator instance created")
            
            # Test initialization
            init_result = await operator.initialize()
            if init_result:
                self.log_success("P2P operator initialized successfully")
            else:
                self.log_warning("P2P operator initialization returned False")
                
            # Test status
            status = operator.get_status()
            if isinstance(status, dict) and 'status' in status:
                self.log_success("P2P operator status check works")
            else:
                self.log_error("P2P operator status check failed")
                
            # Cleanup
            await operator.cleanup()
            
        except Exception as e:
            self.log_error(f"P2P operator test failed: {e}")
            
        return True
        
    def test_web_structure(self) -> bool:
        """Test web component structure"""
        print("\n🌐 Testing Web Structure...")
        self.total_tests += 5
        
        # Check static files
        static_path = Path("web/static")
        if static_path.exists():
            self.log_success("Static files directory exists")
        else:
            self.log_error("Static files directory missing")
            
        # Check templates
        templates_path = Path("web/templates")
        if templates_path.exists():
            self.log_success("Templates directory exists")
        else:
            self.log_error("Templates directory missing")
            
        # Check P2P connector
        p2p_js = Path("web/static/js/p2p_connector.js")
        if p2p_js.exists():
            self.log_success("P2P connector JavaScript exists")
        else:
            self.log_error("P2P connector JavaScript missing")
            
        # Check Gun.js integration
        gun_js = Path("web/static/js/gun-integration.js")
        if gun_js.exists():
            self.log_success("Gun.js integration exists")
        else:
            self.log_error("Gun.js integration missing")
            
        # Check base template
        base_template = Path("web/templates/base.html")
        if base_template.exists():
            self.log_success("Base template exists")
        else:
            self.log_error("Base template missing")
            
        return True
        
    def test_scripts(self) -> bool:
        """Test deployment scripts"""
        print("\n📜 Testing Deployment Scripts...")
        self.total_tests += 3
        
        scripts_path = Path("scripts")
        
        # Check local setup script
        local_script = scripts_path / "setup_local.sh"
        if local_script.exists():
            self.log_success("Local setup script exists")
        else:
            self.log_error("Local setup script missing")
            
        # Check P2P setup script
        p2p_script = scripts_path / "setup_p2p.sh"
        if p2p_script.exists():
            self.log_success("P2P setup script exists")
        else:
            self.log_error("P2P setup script missing")
            
        # Check multi-cloud setup script
        multicloud_script = scripts_path / "setup_multicloud.sh"
        if multicloud_script.exists():
            self.log_success("Multi-cloud setup script exists")
        else:
            self.log_error("Multi-cloud setup script missing")
            
        return True
        
    def check_file_structure(self) -> bool:
        """Check that redundant files were removed"""
        print("\n🧹 Checking for Redundant Files...")
        self.total_tests += 3
        
        # Check that HTML files were removed from components
        html_components = list(Path("web/components").glob("*.html"))
        if not html_components:
            self.log_success("HTML files removed from components directory")
        else:
            self.log_warning(f"Found {len(html_components)} HTML files in components: {html_components}")
            
        # Check that redundant templates were removed
        redundant_templates = [
            Path("web/pages/base.html"),
            Path("web/templates/layout.html")  # If it's redundant with base.html
        ]
        
        removed_count = 0
        for template in redundant_templates:
            if not template.exists():
                removed_count += 1
                
        if removed_count > 0:
            self.log_success(f"Removed {removed_count} redundant template files")
        else:
            self.log_warning("No redundant templates found to remove")
            
        # Check interface.py for static HTML strings
        interface_file = Path("web/components/interface.py")
        if interface_file.exists():
            content = interface_file.read_text()
            if 'return f"""' not in content and 'return """' not in content:
                self.log_success("Interface.py contains only FastHTML components")
            else:
                self.log_warning("Interface.py may still contain static HTML strings")
        
        return True
        
    def generate_report(self):
        """Generate validation report"""
        print("\n" + "="*60)
        print("🏥 GASTRIC ADCI PLATFORM VALIDATION REPORT")
        print("="*60)
        
        print(f"\n📊 Test Results:")
        print(f"   ✅ Successful: {self.success_count}/{self.total_tests}")
        print(f"   ⚠️  Warnings: {len(self.warnings)}")
        print(f"   ❌ Errors: {len(self.errors)}")
        
        if self.warnings:
            print(f"\n⚠️  Warnings:")
            for warning in self.warnings:
                print(f"   • {warning}")
                
        if self.errors:
            print(f"\n❌ Errors:")
            for error in self.errors:
                print(f"   • {error}")
                
        success_rate = (self.success_count / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        print(f"\n🎯 Overall Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("✅ Platform is ready for deployment!")
        elif success_rate >= 70:
            print("⚠️  Platform has some issues but may be functional")
        else:
            print("❌ Platform has significant issues and needs attention")
            
        print("\n🚀 Next Steps:")
        if len(self.errors) == 0:
            print("   1. Run local environment: ./scripts/setup_local.sh")
            print("   2. Test P2P mode: ./scripts/setup_p2p.sh")
            print("   3. Deploy to cloud: ./scripts/setup_multicloud.sh")
        else:
            print("   1. Fix the errors listed above")
            print("   2. Re-run this validation script")
            print("   3. Check the documentation for troubleshooting")

async def main():
    print("🏥 Gastric ADCI Platform - Comprehensive Validation")
    print("="*60)
    
    validator = PlatformValidator()
    
    # Run all tests
    validator.test_imports()
    validator.test_environment_configs()
    await validator.test_p2p_operator()
    validator.test_web_structure()
    validator.test_scripts()
    validator.check_file_structure()
    
    # Generate report
    validator.generate_report()
    
    # Return exit code based on results
    return 0 if len(validator.errors) == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
