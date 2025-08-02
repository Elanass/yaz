#!/usr/bin/env python3
"""
Naming Convention Validator
Validates that the codebase follows consistent naming patterns
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Any

class NamingValidator:
    """Validates naming conventions across the codebase"""
    
    def __init__(self, workspace_path: str = "/workspaces/yaz"):
        self.workspace = Path(workspace_path)
        self.issues = []
        self.stats = {
            "files_checked": 0,
            "naming_issues": 0,
            "unused_files": 0
        }
    
    def check_file_naming(self) -> List[Dict[str, Any]]:
        """Check if files follow snake_case convention"""
        issues = []
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file):
                continue
                
            self.stats["files_checked"] += 1
            filename = py_file.stem
            
            # Skip __init__.py and __main__.py
            if filename.startswith("__") and filename.endswith("__"):
                continue
            
            # Check if filename is snake_case
            if not re.match(r'^[a-z][a-z0-9_]*$', filename):
                issues.append({
                    "type": "file_naming",
                    "file": str(py_file),
                    "issue": f"Filename '{filename}' should be snake_case",
                    "recommendation": f"Rename to {self._to_snake_case(filename)}.py"
                })
                self.stats["naming_issues"] += 1
        
        return issues
    
    def check_class_naming(self) -> List[Dict[str, Any]]:
        """Check if classes follow CamelCase convention"""
        issues = []
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                # Find class definitions
                class_matches = re.finditer(r'^class\s+([A-Za-z_][A-Za-z0-9_]*)', content, re.MULTILINE)
                
                for match in class_matches:
                    class_name = match.group(1)
                    
                    # Check if class name is CamelCase
                    if not re.match(r'^[A-Z][A-Za-z0-9]*$', class_name):
                        issues.append({
                            "type": "class_naming",
                            "file": str(py_file),
                            "line": content[:match.start()].count('\n') + 1,
                            "issue": f"Class '{class_name}' should be CamelCase",
                            "recommendation": f"Rename to {self._to_camel_case(class_name)}"
                        })
                        self.stats["naming_issues"] += 1
                        
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        return issues
    
    def check_function_naming(self) -> List[Dict[str, Any]]:
        """Check if functions follow snake_case convention"""
        issues = []
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                # Find function definitions
                func_matches = re.finditer(r'^def\s+([A-Za-z_][A-Za-z0-9_]*)', content, re.MULTILINE)
                
                for match in func_matches:
                    func_name = match.group(1)
                    
                    # Skip dunder methods
                    if func_name.startswith("__") and func_name.endswith("__"):
                        continue
                    
                    # Check if function name is snake_case
                    if not re.match(r'^[a-z][a-z0-9_]*$', func_name):
                        issues.append({
                            "type": "function_naming",
                            "file": str(py_file),
                            "line": content[:match.start()].count('\n') + 1,
                            "issue": f"Function '{func_name}' should be snake_case",
                            "recommendation": f"Rename to {self._to_snake_case(func_name)}"
                        })
                        self.stats["naming_issues"] += 1
                        
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        return issues
    
    def check_duplicate_classes(self) -> List[Dict[str, Any]]:
        """Check for duplicate class names"""
        issues = []
        classes = {}
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file):
                continue
            
            try:
                content = py_file.read_text()
                class_matches = re.finditer(r'^class\s+([A-Za-z_][A-Za-z0-9_]*)', content, re.MULTILINE)
                
                for match in class_matches:
                    class_name = match.group(1)
                    
                    if class_name in classes:
                        issues.append({
                            "type": "duplicate_class",
                            "class": class_name,
                            "files": [classes[class_name], str(py_file)],
                            "issue": f"Class '{class_name}' is defined in multiple files",
                            "recommendation": "Consolidate or rename one of the classes"
                        })
                        self.stats["naming_issues"] += 1
                    else:
                        classes[class_name] = str(py_file)
                        
            except Exception as e:
                print(f"Error reading {py_file}: {e}")
        
        return issues
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case"""
        # Insert underscores before capitals
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _to_camel_case(self, name: str) -> str:
        """Convert name to CamelCase"""
        components = name.split('_')
        return ''.join(word.capitalize() for word in components)
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks"""
        print("🔍 Validating naming conventions...")
        
        all_issues = []
        all_issues.extend(self.check_file_naming())
        all_issues.extend(self.check_class_naming())
        all_issues.extend(self.check_function_naming())
        all_issues.extend(self.check_duplicate_classes())
        
        return {
            "issues": all_issues,
            "stats": self.stats,
            "summary": {
                "total_issues": len(all_issues),
                "files_checked": self.stats["files_checked"],
                "issues_by_type": self._group_by_type(all_issues)
            }
        }
    
    def _group_by_type(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """Group issues by type"""
        groups = {}
        for issue in issues:
            issue_type = issue["type"]
            groups[issue_type] = groups.get(issue_type, 0) + 1
        return groups

def main():
    validator = NamingValidator()
    results = validator.validate_all()
    
    print(f"\n📊 Validation Results:")
    print(f"   Files checked: {results['stats']['files_checked']}")
    print(f"   Total issues: {results['summary']['total_issues']}")
    
    if results['summary']['issues_by_type']:
        print(f"\n📋 Issues by type:")
        for issue_type, count in results['summary']['issues_by_type'].items():
            print(f"   {issue_type}: {count}")
    
    if results['issues']:
        print(f"\n⚠️  Top Issues:")
        for issue in results['issues'][:10]:  # Show first 10 issues
            print(f"   {issue['type']}: {issue['issue']}")
            if 'file' in issue:
                print(f"      File: {issue['file']}")
            if 'recommendation' in issue:
                print(f"      Fix: {issue['recommendation']}")
            print()
    else:
        print("✅ No naming convention issues found!")

if __name__ == "__main__":
    main()
