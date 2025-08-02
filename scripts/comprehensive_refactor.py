#!/usr/bin/env python3
"""
Comprehensive Codebase Refactoring Script
Addresses architecture, naming, and dependency issues
"""
import os
import shutil
from pathlib import Path
import re

class CodebaseRefactor:
    """Comprehensive refactoring for the Gastric ADCI Platform"""
    
    def __init__(self, workspace_path: str = "/workspaces/yaz"):
        self.workspace = Path(workspace_path)
        self.changes_made = []
        
    def fix_duplicate_dependencies(self):
        """Consolidate duplicate dependency functions"""
        print("🔧 Fixing duplicate dependencies...")
        
        # Update imports in web pages to use core dependencies
        pages_to_fix = [
            "web/pages/home.py",
            "web/pages/auth.py", 
            "web/pages/reports.py",
            "web/pages/education.py",
            "web/pages/hospitality.py"
        ]
        
        for page in pages_to_fix:
            page_path = self.workspace / page
            if page_path.exists():
                content = page_path.read_text()
                
                # Replace auth service imports with core dependencies
                updated_content = content.replace(
                    "from features.auth.service import get_current_user, optional_user",
                    "from core.dependencies import get_current_user\nfrom features.auth.service import optional_user"
                )
                
                if updated_content != content:
                    page_path.write_text(updated_content)
                    self.changes_made.append(f"Updated imports in {page}")
    
    def create_optional_user_dependency(self):
        """Create optional_user dependency in core"""
        print("🔧 Creating optional_user dependency...")
        
        deps_file = self.workspace / "core/dependencies.py"
        content = deps_file.read_text()
        
        # Add optional_user function if not exists
        if "optional_user" not in content:
            optional_user_code = '''

async def optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any] | None:
    """Get current user from token (optional)"""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
'''
            
            updated_content = content + optional_user_code
            deps_file.write_text(updated_content)
            self.changes_made.append("Added optional_user dependency")
    
    def fix_naming_issues(self):
        """Fix common naming convention issues"""
        print("🔧 Fixing naming conventions...")
        
        # Fix function names in web islands (convert CamelCase to snake_case)
        islands_dir = self.workspace / "web/islands"
        if islands_dir.exists():
            for island_file in islands_dir.glob("*.py"):
                content = island_file.read_text()
                
                # Convert CamelCase function names to snake_case
                def to_snake_case(name):
                    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
                    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
                
                # Find and replace CamelCase function definitions
                def replace_func(match):
                    func_name = match.group(1)
                    if func_name[0].isupper():  # CamelCase
                        snake_name = to_snake_case(func_name)
                        return f"def {snake_name}("
                    return match.group(0)
                
                updated_content = re.sub(r'def ([A-Za-z_][A-Za-z0-9_]*)\(', replace_func, content)
                
                if updated_content != content:
                    island_file.write_text(updated_content)
                    self.changes_made.append(f"Fixed function naming in {island_file.name}")
    
    def consolidate_duplicate_classes(self):
        """Address duplicate class issues"""
        print("🔧 Consolidating duplicate classes...")
        
        # Mark analysis.py as deprecated (already done)
        analysis_file = self.workspace / "features/analysis/analysis.py"
        if analysis_file.exists():
            content = analysis_file.read_text()
            if "DEPRECATED" not in content:
                deprecated_content = '''"""
DEPRECATED: Use AnalysisEngine from analysis_engine.py instead
This module will be removed in a future version.
"""
from features.analysis.analysis_engine import AnalysisEngine

# Re-export for backward compatibility
__all__ = ['AnalysisEngine']
'''
                analysis_file.write_text(deprecated_content)
                self.changes_made.append("Marked analysis.py as deprecated")
    
    def organize_imports(self):
        """Organize and clean up imports"""
        print("🔧 Organizing imports...")
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file) or "scripts/" in str(py_file):
                continue
                
            try:
                content = py_file.read_text()
                lines = content.split('\n')
                
                # Find import section
                import_start = -1
                import_end = -1
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if (stripped.startswith('import ') or stripped.startswith('from ')) and import_start == -1:
                        import_start = i
                    elif import_start != -1 and stripped and not (stripped.startswith('import ') or stripped.startswith('from ') or stripped.startswith('#')):
                        import_end = i
                        break
                
                if import_start != -1:
                    # Simple organization: move from imports after regular imports
                    import_lines = lines[import_start:import_end if import_end != -1 else len(lines)]
                    regular_imports = [line for line in import_lines if line.strip().startswith('import ')]
                    from_imports = [line for line in import_lines if line.strip().startswith('from ')]
                    
                    # Only update if there's a meaningful change
                    organized_imports = regular_imports + [''] + from_imports if regular_imports and from_imports else import_lines
                    
                    if organized_imports != import_lines:
                        new_lines = lines[:import_start] + organized_imports + lines[import_end if import_end != -1 else len(lines):]
                        py_file.write_text('\n'.join(new_lines))
                        self.changes_made.append(f"Organized imports in {py_file.relative_to(self.workspace)}")
                        
            except Exception as e:
                print(f"Error organizing imports in {py_file}: {e}")
    
    def create_tests(self):
        """Create missing test files"""
        print("🔧 Creating missing test files...")
        
        # Create test for main functionality
        test_main = self.workspace / "tests/unit/test_main.py"
        test_main.parent.mkdir(parents=True, exist_ok=True)
        
        if not test_main.exists():
            test_content = '''"""
Test suite for main application functionality
"""
import pytest
from fastapi.testclient import TestClient

# Skip tests that require fasthtml for now
pytest.importorskip("fasthtml")

from main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_api_root(client):
    """Test API root redirect"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
'''
            test_main.write_text(test_content)
            self.changes_made.append("Created test_main.py")
        
        # Create test for core dependencies
        test_deps = self.workspace / "tests/unit/test_dependencies.py"
        if not test_deps.exists():
            test_content = '''"""
Test suite for core dependencies
"""
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from core.dependencies import get_current_user, require_role

@pytest.mark.asyncio
async def test_get_current_user():
    """Test get_current_user function"""
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token")
    user = await get_current_user(credentials)
    
    assert user["id"] == "test_user"
    assert user["role"] == "clinician"

def test_require_role():
    """Test role requirement function"""
    role_checker = require_role("admin")
    assert callable(role_checker)
'''
            test_deps.write_text(test_content)
            self.changes_made.append("Created test_dependencies.py")
    
    def update_requirements(self):
        """Update requirements.txt with correct dependencies"""
        print("🔧 Updating requirements...")
        
        req_file = self.workspace / "config/requirements.txt"
        content = req_file.read_text()
        
        # Fix FastHTML package name
        updated_content = content.replace("python-fasthtml==1.0.11", "fasthtml==0.12.22")
        
        if updated_content != content:
            req_file.write_text(updated_content)
            self.changes_made.append("Updated requirements.txt")
    
    def create_validation_script(self):
        """Create a script to validate the fixes"""
        print("🔧 Creating validation script...")
        
        validation_script = self.workspace / "scripts/validate_fixes.py"
        validation_content = '''#!/usr/bin/env python3
"""
Validation script to check if refactoring fixes are working
"""
import sys
from pathlib import Path

def validate_imports():
    """Validate that core modules can be imported"""
    try:
        from core.dependencies import get_current_user, require_role, optional_user
        print("✅ Core dependencies import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def validate_no_legacy_files():
    """Validate that legacy files are removed"""
    workspace = Path.cwd()
    legacy_files = list(workspace.glob("**/legacy_*.py"))
    
    # Filter out .venv files
    legacy_files = [f for f in legacy_files if ".venv" not in str(f)]
    
    if legacy_files:
        print(f"❌ Found {len(legacy_files)} legacy files still present")
        return False
    else:
        print("✅ No legacy files found")
        return True

def validate_naming():
    """Basic validation of naming conventions"""
    issues = 0
    workspace = Path.cwd()
    
    for py_file in workspace.glob("**/*.py"):
        if ".venv" in str(py_file):
            continue
            
        filename = py_file.stem
        if filename.startswith("__") and filename.endswith("__"):
            continue
            
        # Check filename is snake_case
        if not filename.islower() or " " in filename:
            print(f"❌ File naming issue: {py_file}")
            issues += 1
    
    if issues == 0:
        print("✅ Basic filename validation passed")
        return True
    else:
        print(f"❌ Found {issues} naming issues")
        return False

def main():
    print("🧪 Validating refactoring fixes...")
    
    all_passed = True
    all_passed &= validate_imports()
    all_passed &= validate_no_legacy_files()
    all_passed &= validate_naming()
    
    if all_passed:
        print("\\n🎉 All validations passed!")
        return 0
    else:
        print("\\n⚠️  Some validations failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
        validation_script.write_text(validation_content)
        validation_script.chmod(0o755)
        self.changes_made.append("Created validation script")
    
    def run_refactoring(self):
        """Run all refactoring steps"""
        print("🚀 Starting comprehensive refactoring...")
        
        self.fix_duplicate_dependencies()
        self.create_optional_user_dependency()
        self.fix_naming_issues()
        self.consolidate_duplicate_classes()
        self.create_tests()
        self.update_requirements()
        self.create_validation_script()
        
        print(f"\n✨ Refactoring completed!")
        print(f"   Changes made: {len(self.changes_made)}")
        
        if self.changes_made:
            print(f"\n📋 Summary of changes:")
            for change in self.changes_made:
                print(f"   • {change}")
        
        print(f"\n🧪 Run 'python scripts/validate_fixes.py' to validate the changes")

def main():
    refactor = CodebaseRefactor()
    refactor.run_refactoring()

if __name__ == "__main__":
    main()
