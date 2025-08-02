#!/usr/bin/env python3
"""
DRY Compliance Validation Script
Validates that code duplication has been eliminated
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

class DRYValidator:
    """Validates DRY (Don't Repeat Yourself) compliance"""
    
    def __init__(self, workspace_path: str = "/workspaces/yaz"):
        self.workspace = Path(workspace_path)
        self.violations = []
        
    def validate_javascript_dry(self) -> List[Dict]:
        """Check for JavaScript code duplication"""
        print("🔍 Checking JavaScript DRY compliance...")
        
        js_files = list(self.workspace.glob("web/static/js/*.js"))
        violations = []
        
        # Patterns to check for duplication
        patterns = {
            'showNotification': r'showNotification\s*[:=]\s*\(',
            'debounce': r'debounce\s*[:=]\s*\(',
            'formatADCIScore': r'formatADCIScore\s*[:=]\s*\(',
            'copyToClipboard': r'copyToClipboard\s*[:=]\s*\(',
            'validateClinicalData': r'validateClinicalData\s*[:=]\s*\(',
        }
        
        for pattern_name, pattern_regex in patterns.items():
            files_with_pattern = []
            
            for js_file in js_files:
                if js_file.name == 'shared-utils.js':
                    continue  # Skip the shared utilities file
                    
                try:
                    content = js_file.read_text()
                    if re.search(pattern_regex, content):
                        files_with_pattern.append(str(js_file.relative_to(self.workspace)))
                except Exception as e:
                    print(f"Error reading {js_file}: {e}")
            
            if len(files_with_pattern) > 1:
                violations.append({
                    'type': 'duplicate_function',
                    'function': pattern_name,
                    'files': files_with_pattern,
                    'severity': 'high',
                    'recommendation': f'Use SharedUtils.{pattern_name} instead'
                })
        
        return violations
    
    def validate_python_dry(self) -> List[Dict]:
        """Check for Python code duplication"""
        print("🔍 Checking Python DRY compliance...")
        
        py_files = list(self.workspace.glob("**/*.py"))
        violations = []
        
        # Check for duplicate dependency functions
        dependency_patterns = {
            'get_current_user': r'def get_current_user\(',
            'require_auth': r'def require_auth\(',
            'optional_user': r'def optional_user\(',
        }
        
        for pattern_name, pattern_regex in dependency_patterns.items():
            files_with_pattern = []
            
            for py_file in py_files:
                if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                    continue
                    
                try:
                    content = py_file.read_text()
                    if re.search(pattern_regex, content):
                        files_with_pattern.append(str(py_file.relative_to(self.workspace)))
                except Exception as e:
                    continue
            
            if len(files_with_pattern) > 1:
                violations.append({
                    'type': 'duplicate_function',
                    'function': pattern_name,
                    'files': files_with_pattern,
                    'severity': 'medium',
                    'recommendation': f'Use core.dependencies.{pattern_name} instead'
                })
        
        return violations
    
    def validate_css_dry(self) -> List[Dict]:
        """Check for CSS code duplication"""
        print("🔍 Checking CSS DRY compliance...")
        
        css_files = list(self.workspace.glob("web/static/css/*.css"))
        html_files = list(self.workspace.glob("web/templates/**/*.html"))
        violations = []
        
        # Check for repeated style patterns
        style_patterns = {
            'button_styles': r'btn-primary|btn-secondary',
            'color_variables': r'--primary-color|--secondary-color',
            'spacing_classes': r'p-\d+|m-\d+|space-\d+'
        }
        
        # This is a simplified check - in practice, you'd want more sophisticated CSS analysis
        for pattern_name, pattern_regex in style_patterns.items():
            duplicate_count = 0
            
            for css_file in css_files:
                try:
                    content = css_file.read_text()
                    matches = re.findall(pattern_regex, content)
                    if len(matches) > 10:  # Arbitrary threshold
                        duplicate_count += 1
                except Exception:
                    continue
            
            if duplicate_count > 0:
                violations.append({
                    'type': 'potential_css_duplication',
                    'pattern': pattern_name,
                    'severity': 'low',
                    'recommendation': 'Consider CSS utility classes or component extraction'
                })
        
        return violations
    
    def check_shared_utilities_usage(self) -> List[Dict]:
        """Verify that shared utilities are being used"""
        print("🔍 Checking shared utilities usage...")
        
        violations = []
        js_files = list(self.workspace.glob("web/static/js/*.js"))
        
        # Check if files are importing/using SharedUtils
        files_not_using_shared = []
        
        for js_file in js_files:
            if js_file.name in ['shared-utils.js', 'gun-integration.js', 'p2p_connector.js']:
                continue
                
            try:
                content = js_file.read_text()
                
                # Check if file has utility functions but doesn't use SharedUtils
                has_utility_functions = any(pattern in content for pattern in [
                    'showNotification', 'debounce', 'formatADCIScore'
                ])
                
                uses_shared_utils = 'SharedUtils' in content
                
                if has_utility_functions and not uses_shared_utils:
                    files_not_using_shared.append(str(js_file.relative_to(self.workspace)))
                    
            except Exception:
                continue
        
        if files_not_using_shared:
            violations.append({
                'type': 'shared_utils_not_used',
                'files': files_not_using_shared,
                'severity': 'medium',
                'recommendation': 'Update files to use SharedUtils instead of duplicate implementations'
            })
        
        return violations
    
    def validate_all(self) -> Dict:
        """Run all DRY validation checks"""
        print("🧪 Running comprehensive DRY validation...")
        
        all_violations = []
        
        # Run all validation checks
        all_violations.extend(self.validate_javascript_dry())
        all_violations.extend(self.validate_python_dry())
        all_violations.extend(self.validate_css_dry())
        all_violations.extend(self.check_shared_utilities_usage())
        
        # Categorize violations by severity
        high_severity = [v for v in all_violations if v.get('severity') == 'high']
        medium_severity = [v for v in all_violations if v.get('severity') == 'medium']
        low_severity = [v for v in all_violations if v.get('severity') == 'low']
        
        return {
            'total_violations': len(all_violations),
            'high_severity': high_severity,
            'medium_severity': medium_severity,
            'low_severity': low_severity,
            'passed': len(all_violations) == 0
        }
    
    def generate_report(self, results: Dict) -> None:
        """Generate a comprehensive DRY compliance report"""
        print("\n" + "="*60)
        print("🧪 DRY COMPLIANCE VALIDATION REPORT")
        print("="*60)
        
        if results['passed']:
            print("✅ PASSED: No DRY violations found!")
            print("🎉 Code follows DRY principles correctly")
        else:
            print(f"❌ FOUND {results['total_violations']} DRY violations")
            
            if results['high_severity']:
                print(f"\n🔴 HIGH SEVERITY ({len(results['high_severity'])} issues):")
                for violation in results['high_severity']:
                    print(f"   • {violation['type']}: {violation.get('function', violation.get('pattern', 'Unknown'))}")
                    if 'files' in violation:
                        for file in violation['files']:
                            print(f"     - {file}")
                    print(f"     💡 {violation['recommendation']}")
            
            if results['medium_severity']:
                print(f"\n🟡 MEDIUM SEVERITY ({len(results['medium_severity'])} issues):")
                for violation in results['medium_severity']:
                    print(f"   • {violation['type']}: {violation.get('function', violation.get('pattern', 'Unknown'))}")
                    if 'files' in violation:
                        for file in violation['files']:
                            print(f"     - {file}")
                    print(f"     💡 {violation['recommendation']}")
            
            if results['low_severity']:
                print(f"\n🟢 LOW SEVERITY ({len(results['low_severity'])} issues):")
                for violation in results['low_severity']:
                    print(f"   • {violation['type']}: {violation.get('pattern', 'Unknown')}")
                    print(f"     💡 {violation['recommendation']}")
        
        print("\n" + "="*60)
        print("🎯 DRY COMPLIANCE SUMMARY:")
        print(f"   ✅ Shared utilities: {'Implemented' if Path('/workspaces/yaz/web/static/js/shared-utils.js').exists() else 'Missing'}")
        print(f"   📊 Total violations: {results['total_violations']}")
        print(f"   🔴 High severity: {len(results['high_severity'])}")
        print(f"   🟡 Medium severity: {len(results['medium_severity'])}")
        print(f"   🟢 Low severity: {len(results['low_severity'])}")
        print("="*60)

def main():
    """Main validation execution"""
    validator = DRYValidator()
    results = validator.validate_all()
    validator.generate_report(results)
    
    # Return appropriate exit code
    if results['passed'] or len(results['high_severity']) == 0:
        print("\n✅ DRY validation completed successfully!")
        return 0
    else:
        print("\n❌ DRY validation found critical issues")
        return 1

if __name__ == "__main__":
    exit(main())
