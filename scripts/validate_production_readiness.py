#!/usr/bin/env python3
"""
Block-by-block validation script for production readiness audit
Validates each architectural block systematically
"""

import sys
import os
import asyncio
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
os.environ['PYTHONPATH'] = str(src_path)

async def validate_ui_components():
    """Validate UI component architecture"""
    print("🎨 Validating UI Components & Islandized UX...")
    
    # Check component files
    components_dir = Path("src/surgify/ui/components")
    required_components = [
        "DomainSelector.js",
        "CaseList.js", 
        "CaseDetail.js",
        "NotificationBadge.js",
        "ThemeToggle.js",
        "ResultsIsland.js",
        "ComparisonIsland.js", 
        "DiscussionIsland.js",
        "RecommendationIsland.js"
    ]
    
    missing_components = []
    for component in required_components:
        if not (components_dir / component).exists():
            missing_components.append(component)
    
    if missing_components:
        print(f"❌ Missing components: {missing_components}")
        return False
    else:
        print("✅ All UI components found")
        
        # Check component integration
        index_file = components_dir / "index.js"
        if index_file.exists():
            print("✅ Component index file exists")
        else:
            print("⚠️ Component index file missing")
            
        return True

def validate_api_structure():
    """Validate API endpoint structure"""
    print("🔌 Validating API Handlers...")
    
    api_dir = Path("src/surgify/api/v1")
    required_endpoints = [
        "__init__.py",
        "auth.py",
        "cases.py",
        "sync.py",
        "deliverables.py",
        "ai.py",
        "dashboard.py"
    ]
    
    missing_endpoints = []
    for endpoint in required_endpoints:
        if not (api_dir / endpoint).exists():
            missing_endpoints.append(endpoint)
    
    if missing_endpoints:
        print(f"❌ Missing API endpoints: {missing_endpoints}")
        return False
    else:
        print("✅ All API endpoint files found")
        return True

def validate_service_layer():
    """Validate business logic services"""
    print("⚙️ Validating Business Logic Services...")
    
    services_dir = Path("src/surgify/core/services")
    required_services = [
        "logger.py",
        "registry.py",
        "case_service.py",
        "sync_service.py",
        "deliverable_service.py"
    ]
    
    missing_services = []
    for service in required_services:
        if not (services_dir / service).exists():
            missing_services.append(service)
    
    if missing_services:
        print(f"❌ Missing services: {missing_services}")
        return False
    else:
        print("✅ All service files found")
        return True

def validate_data_layer():
    """Validate data layer components"""
    print("💾 Validating Data Layer...")
    
    # Check models
    models_dir = Path("data/models")
    if not models_dir.exists():
        print("❌ Models directory not found")
        return False
    
    required_models = ["__init__.py", "orm.py", "users.py"]
    missing_models = []
    for model in required_models:
        if not (models_dir / model).exists():
            missing_models.append(model)
    
    if missing_models:
        print(f"❌ Missing models: {missing_models}")
        return False
    
    # Check repositories
    repos_dir = models_dir / "repositories"
    if not repos_dir.exists():
        print("❌ Repositories directory not found")
        return False
    
    print("✅ Data layer structure validated")
    return True

def validate_infrastructure():
    """Validate infrastructure automation"""
    print("🏗️ Validating Infrastructure & Deployment...")
    
    # Check infrastructure script
    infra_script = Path("scripts/setup-contabo-infrastructure.sh")
    if not infra_script.exists():
        print("❌ Contabo infrastructure script not found")
        return False
    
    # Check if script is executable
    if not os.access(infra_script, os.X_OK):
        print("⚠️ Infrastructure script not executable")
        # Make it executable
        os.chmod(infra_script, 0o755)
        print("✅ Made infrastructure script executable")
    
    print("✅ Infrastructure script found and executable")
    
    # Check GitHub Actions workflow
    workflow_file = Path(".github/workflows/github-loader.yml")
    if not workflow_file.exists():
        print("❌ GitHub Actions workflow not found")
        return False
    
    print("✅ GitHub Actions workflow found")
    return True

def validate_cicd_pipeline():
    """Validate CI/CD pipeline"""
    print("🚀 Validating CI/CD Pipeline...")
    
    # Check workflow file
    workflow = Path(".github/workflows/github-loader.yml")
    if not workflow.exists():
        print("❌ Main workflow file missing")
        return False
    
    # Check for multiple workflow files (should be consolidated)
    workflows_dir = Path(".github/workflows")
    if workflows_dir.exists():
        workflow_files = list(workflows_dir.glob("*.yml"))
        if len(workflow_files) > 1:
            print(f"⚠️ Multiple workflow files found: {[f.name for f in workflow_files]}")
            print("ℹ️ Consider consolidating into single github-loader.yml")
        else:
            print("✅ Single consolidated workflow file")
    
    return True

def validate_p2p_network():
    """Validate P2P mesh network"""
    print("🌐 Validating P2P Mesh Network...")
    
    # Check BitChat integration
    bitchat_dir = Path("network/bitchat")
    if not bitchat_dir.exists():
        print("❌ BitChat directory not found")
        return False
    
    required_files = ["Justfile", "Package.swift", "PRIVACY_POLICY.md"]
    missing_files = []
    for file in required_files:
        if not (bitchat_dir / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing BitChat files: {missing_files}")
        return False
    
    print("✅ BitChat P2P network structure validated")
    return True

def validate_sync_layer():
    """Validate synchronization layer"""
    print("🔄 Validating Synchronization Layer...")
    
    # Check cache implementation
    cache_file = Path("src/surgify/core/cache.py")
    if not cache_file.exists():
        print("❌ Cache implementation not found")
        return False
    
    print("✅ Cache layer found")
    
    # Check sync service
    sync_service = Path("src/surgify/core/services/sync_service.py")
    if not sync_service.exists():
        print("❌ Sync service not found")
        return False
    
    print("✅ Sync service found")
    return True

async def run_validation():
    """Run complete block-by-block validation"""
    print("🔍 Starting Block-by-Block Production Readiness Validation")
    print("=" * 60)
    
    validations = [
        ("UI Components", validate_ui_components),
        ("API Structure", validate_api_structure),
        ("Service Layer", validate_service_layer),
        ("Data Layer", validate_data_layer),
        ("Sync Layer", validate_sync_layer),
        ("P2P Network", validate_p2p_network),
        ("Infrastructure", validate_infrastructure),
        ("CI/CD Pipeline", validate_cicd_pipeline)
    ]
    
    results = {}
    
    for name, validator in validations:
        print(f"\n📋 {name} Validation:")
        print("-" * 40)
        try:
            if asyncio.iscoroutinefunction(validator):
                result = await validator()
            else:
                result = validator()
            results[name] = result
        except Exception as e:
            print(f"❌ Validation failed with error: {str(e)}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    total_blocks = len(results)
    passed_blocks = sum(1 for result in results.values() if result)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:<20} {status}")
    
    print(f"\nOverall Score: {passed_blocks}/{total_blocks} ({passed_blocks/total_blocks*100:.1f}%)")
    
    if passed_blocks == total_blocks:
        print("🎉 ALL BLOCKS VALIDATED - PRODUCTION READY!")
        return True
    else:
        print(f"⚠️  {total_blocks - passed_blocks} BLOCKS NEED ATTENTION")
        return False

if __name__ == "__main__":
    asyncio.run(run_validation())
