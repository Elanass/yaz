#!/usr/bin/env python3
"""
Import Dependency Analyzer
Analyzes import dependencies and identifies issues
"""
import ast
import os
from pathlib import Path
from typing import Set, Dict, List, Any

class ImportAnalyzer:
    """Analyzes import patterns and dependencies"""
    
    def __init__(self, workspace_path: str = "/workspaces/yaz"):
        self.workspace = Path(workspace_path)
        self.imports = {}
        self.unused_files = set()
        
    def analyze_imports(self) -> Dict[str, Any]:
        """Analyze all imports in the codebase"""
        all_files = set()
        imported_modules = set()
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file):
                continue
                
            rel_path = py_file.relative_to(self.workspace)
            module_name = str(rel_path).replace("/", ".").replace(".py", "")
            all_files.add(module_name)
            
            # Parse file for imports
            try:
                with open(py_file, 'r') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imported_modules.add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imported_modules.add(node.module)
                            
            except Exception as e:
                print(f"Error parsing {py_file}: {e}")
        
        # Find potentially unused files
        unused = all_files - imported_modules
        
        # Filter out obvious exceptions
        filtered_unused = {
            f for f in unused 
            if not (
                f.endswith("__init__") or 
                f.endswith("main") or
                f.startswith("scripts.") or
                f.startswith("tests.")
            )
        }
        
        return {
            "total_files": len(all_files),
            "imported_modules": len(imported_modules),
            "potentially_unused": list(filtered_unused),
            "usage_percentage": (len(imported_modules) / len(all_files)) * 100
        }
    
    def find_circular_imports(self) -> List[List[str]]:
        """Find potential circular import issues"""
        # This is a simplified version - full implementation would need more sophisticated analysis
        circular_patterns = []
        
        for py_file in self.workspace.glob("**/*.py"):
            if ".venv" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                # Look for imports from sibling modules in features
                if "features/" in str(py_file):
                    if "from features." in content:
                        # Potential feature-to-feature dependency
                        rel_path = py_file.relative_to(self.workspace)
                        circular_patterns.append([str(rel_path), "cross-feature import"])
                        
            except Exception as e:
                print(f"Error analyzing {py_file}: {e}")
        
        return circular_patterns

def main():
    analyzer = ImportAnalyzer()
    
    print("🔍 Analyzing import dependencies...")
    results = analyzer.analyze_imports()
    
    print(f"\n📊 Import Analysis Results:")
    print(f"   Total Python files: {results['total_files']}")
    print(f"   Imported modules: {results['imported_modules']}")
    print(f"   Usage percentage: {results['usage_percentage']:.1f}%")
    
    if results['potentially_unused']:
        print(f"\n⚠️  Potentially unused files ({len(results['potentially_unused'])}):")
        for unused in results['potentially_unused'][:10]:  # Show first 10
            print(f"   {unused}")
        if len(results['potentially_unused']) > 10:
            print(f"   ... and {len(results['potentially_unused']) - 10} more")
    
    print("\n🔄 Checking for circular imports...")
    circular = analyzer.find_circular_imports()
    if circular:
        print(f"   Found {len(circular)} potential circular import patterns")
        for pattern in circular[:5]:
            print(f"   {pattern[0]}: {pattern[1]}")
    else:
        print("   No obvious circular import patterns found")

if __name__ == "__main__":
    main()
