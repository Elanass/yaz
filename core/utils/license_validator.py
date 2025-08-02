"""
License validation utility for dependency scanning and compliance checking.
"""
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re

from core.services.logger import get_logger

logger = get_logger(__name__)


class LicenseValidator:
    """Validates licenses of project dependencies and internal modules."""
    
    # Known compatible licenses for our project
    COMPATIBLE_LICENSES = {
        'MIT',
        'Apache-2.0', 'Apache 2.0',
        'BSD-3-Clause', 'BSD-2-Clause', 'BSD',
        'Mozilla Public License 2.0', 'MPL-2.0',
        'GNU LGPL v2.1', 'LGPL-2.1',
        'ISC',
        'Python Software Foundation License'
    }
    
    # Licenses that require special attention
    ATTENTION_LICENSES = {
        'GPL-3.0', 'GPL-2.0',  # Copyleft licenses
        'AGPL-3.0',            # Network copyleft
        'Commercial',          # Proprietary
        'Proprietary'
    }
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.requirements_file = self.project_root / "config" / "requirements.txt"
        
    def scan_requirements(self) -> Dict[str, Dict]:
        """Scan requirements.txt and get license information for each package."""
        
        if not self.requirements_file.exists():
            logger.warning(f"Requirements file not found: {self.requirements_file}")
            return {}
        
        packages = self._parse_requirements()
        license_info = {}
        
        logger.info(f"Scanning {len(packages)} packages for license information...")
        
        for package in packages:
            try:
                license_data = self._get_package_license(package)
                license_info[package] = license_data
            except Exception as e:
                logger.warning(f"Could not get license info for {package}: {e}")
                license_info[package] = {
                    'license': 'Unknown',
                    'compatible': False,
                    'requires_attention': True,
                    'error': str(e)
                }
        
        return license_info
    
    def _parse_requirements(self) -> List[str]:
        """Parse requirements.txt file and extract package names."""
        packages = []
        
        with open(self.requirements_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract package name (remove version constraints)
                    package = re.split(r'[>=<!]', line)[0].strip()
                    if package:
                        packages.append(package)
        
        return packages
    
    def _get_package_license(self, package_name: str) -> Dict:
        """Get license information for a specific package."""
        try:
            # Try to get license info using pip show
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                license_line = None
                for line in result.stdout.split('\n'):
                    if line.startswith('License:'):
                        license_line = line.split('License:', 1)[1].strip()
                        break
                
                license_name = license_line or 'Unknown'
                
                return {
                    'license': license_name,
                    'compatible': self._is_compatible_license(license_name),
                    'requires_attention': self._requires_attention(license_name),
                    'source': 'pip_show'
                }
            else:
                # Fallback: try to get from PyPI API
                return self._get_license_from_pypi(package_name)
                
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout getting license for {package_name}")
            return {
                'license': 'Unknown (Timeout)',
                'compatible': False,
                'requires_attention': True,
                'error': 'Timeout'
            }
        except Exception as e:
            logger.warning(f"Error getting license for {package_name}: {e}")
            raise
    
    def _get_license_from_pypi(self, package_name: str) -> Dict:
        """Fallback method to get license from PyPI API."""
        try:
            import requests
            
            response = requests.get(
                f"https://pypi.org/pypi/{package_name}/json",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                license_name = data.get('info', {}).get('license', 'Unknown')
                
                return {
                    'license': license_name,
                    'compatible': self._is_compatible_license(license_name),
                    'requires_attention': self._requires_attention(license_name),
                    'source': 'pypi_api'
                }
        except Exception as e:
            logger.warning(f"Could not get license from PyPI for {package_name}: {e}")
        
        return {
            'license': 'Unknown',
            'compatible': False,
            'requires_attention': True,
            'error': 'Could not determine license'
        }
    
    def _is_compatible_license(self, license_name: str) -> bool:
        """Check if a license is compatible with our project."""
        if not license_name or license_name == 'Unknown':
            return False
        
        # Normalize license name for comparison
        normalized = license_name.strip().replace('License', '').strip()
        
        for compatible in self.COMPATIBLE_LICENSES:
            if compatible.lower() in normalized.lower():
                return True
        
        return False
    
    def _requires_attention(self, license_name: str) -> bool:
        """Check if a license requires special attention."""
        if not license_name or license_name == 'Unknown':
            return True
        
        normalized = license_name.strip().replace('License', '').strip()
        
        for attention in self.ATTENTION_LICENSES:
            if attention.lower() in normalized.lower():
                return True
        
        return False
    
    def validate_internal_modules(self) -> Dict[str, Dict]:
        """Scan internal modules for license metadata."""
        
        module_licenses = {}
        
        # Scan core modules
        core_dir = self.project_root / "core"
        for module_file in core_dir.rglob("*.py"):
            if module_file.name != "__init__.py":
                license_info = self._extract_module_license(module_file)
                relative_path = module_file.relative_to(self.project_root)
                module_licenses[str(relative_path)] = license_info
        
        # Scan features modules
        features_dir = self.project_root / "features"
        if features_dir.exists():
            for module_file in features_dir.rglob("*.py"):
                if module_file.name != "__init__.py":
                    license_info = self._extract_module_license(module_file)
                    relative_path = module_file.relative_to(self.project_root)
                    module_licenses[str(relative_path)] = license_info
        
        return module_licenses
    
    def _extract_module_license(self, module_path: Path) -> Dict:
        """Extract license information from module docstrings or comments."""
        
        try:
            with open(module_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for license in docstrings or comments
            license_patterns = [
                r'(?i)license[:\s]+([^\n]+)',
                r'(?i)copyright[:\s]+([^\n]+)',
                r'(?i)licensed under[:\s]+([^\n]+)'
            ]
            
            license_info = 'Not specified'
            
            for pattern in license_patterns:
                match = re.search(pattern, content)
                if match:
                    license_info = match.group(1).strip()
                    break
            
            # Default assumption for internal modules
            if license_info == 'Not specified':
                license_info = 'Apache-2.0 (Internal)'
            
            return {
                'license': license_info,
                'compatible': True,  # Assume internal modules are compatible
                'requires_attention': 'Proprietary' in license_info or 'Commercial' in license_info,
                'type': 'internal'
            }
            
        except Exception as e:
            logger.warning(f"Could not scan module {module_path}: {e}")
            return {
                'license': 'Unknown',
                'compatible': False,
                'requires_attention': True,
                'error': str(e),
                'type': 'internal'
            }
    
    def generate_license_report(self) -> Dict:
        """Generate comprehensive license compliance report."""
        
        logger.info("Generating license compliance report...")
        
        # Scan dependencies
        dependencies = self.scan_requirements()
        
        # Scan internal modules
        internal_modules = self.validate_internal_modules()
        
        # Generate summary
        total_deps = len(dependencies)
        compatible_deps = sum(1 for d in dependencies.values() if d.get('compatible', False))
        attention_deps = sum(1 for d in dependencies.values() if d.get('requires_attention', False))
        
        total_modules = len(internal_modules)
        compatible_modules = sum(1 for m in internal_modules.values() if m.get('compatible', False))
        attention_modules = sum(1 for m in internal_modules.values() if m.get('requires_attention', False))
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': {
                'total_dependencies': total_deps,
                'compatible_dependencies': compatible_deps,
                'attention_dependencies': attention_deps,
                'total_internal_modules': total_modules,
                'compatible_internal_modules': compatible_modules,
                'attention_internal_modules': attention_modules,
                'overall_compliance': (compatible_deps + compatible_modules) / (total_deps + total_modules) if (total_deps + total_modules) > 0 else 0
            },
            'dependencies': dependencies,
            'internal_modules': internal_modules,
            'recommendations': self._generate_recommendations(dependencies, internal_modules)
        }
        
        return report
    
    def _generate_recommendations(self, dependencies: Dict, internal_modules: Dict) -> List[str]:
        """Generate actionable recommendations for license compliance."""
        
        recommendations = []
        
        # Check for incompatible dependencies
        incompatible_deps = [name for name, info in dependencies.items() 
                           if not info.get('compatible', False)]
        
        if incompatible_deps:
            recommendations.append(
                f"Review {len(incompatible_deps)} dependencies with incompatible or unknown licenses: {', '.join(incompatible_deps[:5])}"
            )
        
        # Check for attention-required licenses
        attention_deps = [name for name, info in dependencies.items() 
                        if info.get('requires_attention', False)]
        
        if attention_deps:
            recommendations.append(
                f"Legal review required for {len(attention_deps)} dependencies with restrictive licenses"
            )
        
        # Check internal modules without proper license headers
        unlicensed_modules = [name for name, info in internal_modules.items() 
                            if info.get('license') == 'Not specified']
        
        if unlicensed_modules:
            recommendations.append(
                f"Add license headers to {len(unlicensed_modules)} internal modules"
            )
        
        # General recommendations
        recommendations.extend([
            "Update ATTRIBUTIONS.md with new dependencies",
            "Schedule quarterly license compliance reviews",
            "Consider using automated license scanning in CI/CD"
        ])
        
        return recommendations
    
    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """Generate and save license compliance report."""
        
        if output_path is None:
            output_path = self.project_root / "docs" / "legal" / "license_scan_report.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        report = self.generate_license_report()
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"License compliance report saved to: {output_path}")
        
        return output_path


def main():
    """CLI entry point for license validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate project license compliance")
    parser.add_argument("--output", "-o", help="Output file path for report")
    parser.add_argument("--format", choices=["json", "summary"], default="summary", 
                       help="Output format")
    
    args = parser.parse_args()
    
    validator = LicenseValidator()
    
    if args.format == "json":
        output_path = Path(args.output) if args.output else None
        report_path = validator.save_report(output_path)
        print(f"License report saved to: {report_path}")
    else:
        report = validator.generate_license_report()
        
        print("=== License Compliance Summary ===")
        print(f"Dependencies: {report['summary']['compatible_dependencies']}/{report['summary']['total_dependencies']} compatible")
        print(f"Internal Modules: {report['summary']['compatible_internal_modules']}/{report['summary']['total_internal_modules']} compliant")
        print(f"Overall Compliance: {report['summary']['overall_compliance']:.1%}")
        
        if report['recommendations']:
            print("\n=== Recommendations ===")
            for i, rec in enumerate(report['recommendations'], 1):
                print(f"{i}. {rec}")


if __name__ == "__main__":
    main()
