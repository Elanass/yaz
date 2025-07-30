#!/usr/bin/env python3
"""
License Validator for Gastric ADCI Platform
Scans dependencies and validates license compatibility at build time
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
import re
import requests
from dataclasses import dataclass
from enum import Enum

class LicenseType(Enum):
    """License categorization"""
    OPEN_FOUNDATION = "open_foundation"  # MIT, Apache, BSD, etc.
    COPYLEFT = "copyleft"  # GPL, LGPL, etc.
    PROPRIETARY = "proprietary"
    UNKNOWN = "unknown"

@dataclass
class LicenseInfo:
    """License information for a package"""
    package: str
    version: str
    license: str
    license_type: LicenseType
    compatible: bool
    url: Optional[str] = None
    notes: Optional[str] = None

class LicenseValidator:
    """Validates licenses of project dependencies"""
    
    # Compatible open source licenses
    OPEN_LICENSES = {
        'MIT', 'Apache 2.0', 'Apache-2.0', 'Apache Software License',
        'BSD', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC',
        'Python Software Foundation License', 'PSF-2.0',
        'Mozilla Public License 2.0', 'MPL-2.0'
    }
    
    # LGPL licenses (compatible with restrictions)
    LGPL_LICENSES = {
        'GNU LGPL', 'LGPL', 'LGPL-2.1', 'LGPL-3.0',
        'GNU Lesser General Public License v2.1',
        'GNU Lesser General Public License v3.0'
    }
    
    # GPL licenses (copyleft - may require special handling)
    GPL_LICENSES = {
        'GPL', 'GPL-2.0', 'GPL-3.0', 'GNU GPL',
        'GNU General Public License v2.0',
        'GNU General Public License v3.0'
    }
    
    # Known proprietary or problematic licenses
    PROPRIETARY_LICENSES = {
        'Commercial', 'Proprietary', 'All Rights Reserved'
    }
    
    def __init__(self, requirements_file: str = "config/requirements.txt"):
        self.requirements_file = Path(requirements_file)
        self.licenses: List[LicenseInfo] = []
        
    def get_installed_packages(self) -> List[Tuple[str, str]]:
        """Get list of installed packages and versions"""
        try:
            result = subprocess.run(
                ['pip', 'freeze'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            packages = []
            for line in result.stdout.strip().split('\n'):
                if line and '==' in line:
                    name, version = line.split('==', 1)
                    packages.append((name.strip(), version.strip()))
            return packages
        except subprocess.CalledProcessError as e:
            print(f"Error getting installed packages: {e}")
            return []
    
    def get_package_license(self, package: str, version: str) -> str:
        """Get license information for a package"""
        try:
            # Try pip show first
            result = subprocess.run(
                ['pip', 'show', package], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if line.startswith('License:'):
                    license_text = line.split('License:', 1)[1].strip()
                    if license_text and license_text != 'UNKNOWN':
                        return license_text
            
            # Fallback to PyPI API
            return self._get_license_from_pypi(package)
            
        except subprocess.CalledProcessError:
            return self._get_license_from_pypi(package)
    
    def _get_license_from_pypi(self, package: str) -> str:
        """Get license from PyPI JSON API"""
        try:
            url = f"https://pypi.org/pypi/{package}/json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                info = data.get('info', {})
                
                # Try license field first
                license_text = info.get('license', '')
                if license_text and license_text.strip():
                    return license_text.strip()
                
                # Try classifiers
                classifiers = info.get('classifiers', [])
                for classifier in classifiers:
                    if classifier.startswith('License ::'):
                        # Extract license from classifier
                        parts = classifier.split(' :: ')
                        if len(parts) >= 3:
                            return parts[-1]
            
            return "UNKNOWN"
            
        except Exception as e:
            print(f"Warning: Could not fetch license for {package}: {e}")
            return "UNKNOWN"
    
    def categorize_license(self, license_text: str) -> LicenseType:
        """Categorize license type"""
        license_upper = license_text.upper()
        
        # Check for open source licenses
        for open_license in self.OPEN_LICENSES:
            if open_license.upper() in license_upper:
                return LicenseType.OPEN_FOUNDATION
        
        # Check for LGPL
        for lgpl_license in self.LGPL_LICENSES:
            if lgpl_license.upper() in license_upper:
                return LicenseType.COPYLEFT
        
        # Check for GPL
        for gpl_license in self.GPL_LICENSES:
            if gpl_license.upper() in license_upper:
                return LicenseType.COPYLEFT
        
        # Check for proprietary
        for prop_license in self.PROPRIETARY_LICENSES:
            if prop_license.upper() in license_upper:
                return LicenseType.PROPRIETARY
        
        return LicenseType.UNKNOWN
    
    def is_compatible(self, license_type: LicenseType, license_text: str) -> bool:
        """Check if license is compatible with our project"""
        if license_type == LicenseType.OPEN_FOUNDATION:
            return True
        elif license_type == LicenseType.COPYLEFT:
            # LGPL is generally acceptable for dynamic linking
            return any(lgpl in license_text.upper() for lgpl in 
                      [l.upper() for l in self.LGPL_LICENSES])
        elif license_type == LicenseType.PROPRIETARY:
            return False
        else:  # UNKNOWN
            return False
    
    def validate_all_licenses(self) -> bool:
        """Validate all package licenses"""
        print("🔍 Scanning package licenses...")
        
        packages = self.get_installed_packages()
        if not packages:
            print("❌ No packages found")
            return False
        
        all_compatible = True
        
        for package, version in packages:
            license_text = self.get_package_license(package, version)
            license_type = self.categorize_license(license_text)
            compatible = self.is_compatible(license_type, license_text)
            
            license_info = LicenseInfo(
                package=package,
                version=version,
                license=license_text,
                license_type=license_type,
                compatible=compatible
            )
            
            self.licenses.append(license_info)
            
            if not compatible:
                all_compatible = False
                print(f"⚠️  {package} ({version}): {license_text} - INCOMPATIBLE")
            else:
                print(f"✅ {package} ({version}): {license_text}")
        
        return all_compatible
    
    def generate_license_report(self, output_file: str = "docs/legal/LICENSE_SCAN.md"):
        """Generate detailed license compliance report"""
        report_path = Path(output_file)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w') as f:
            f.write("# Automated License Scan Report\n\n")
            f.write(f"Generated: {self._get_timestamp()}\n\n")
            
            # Summary
            total = len(self.licenses)
            compatible = sum(1 for l in self.licenses if l.compatible)
            incompatible = total - compatible
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Packages**: {total}\n")
            f.write(f"- **Compatible**: {compatible}\n")
            f.write(f"- **Incompatible**: {incompatible}\n\n")
            
            # By category
            categories = {}
            for license_info in self.licenses:
                cat = license_info.license_type.value
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(license_info)
            
            f.write("## By License Category\n\n")
            for category, licenses in categories.items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                f.write("| Package | Version | License | Compatible |\n")
                f.write("|---------|---------|---------|------------|\n")
                
                for license_info in sorted(licenses, key=lambda x: x.package):
                    status = "✅" if license_info.compatible else "❌"
                    f.write(f"| {license_info.package} | {license_info.version} | "
                           f"{license_info.license} | {status} |\n")
                f.write("\n")
            
            # Incompatible packages
            incompatible_packages = [l for l in self.licenses if not l.compatible]
            if incompatible_packages:
                f.write("## ⚠️ Incompatible Packages\n\n")
                f.write("The following packages have license compatibility issues:\n\n")
                for license_info in incompatible_packages:
                    f.write(f"- **{license_info.package}** ({license_info.version}): "
                           f"{license_info.license}\n")
                f.write("\n")
            
            f.write("## Compliance Actions\n\n")
            f.write("- [ ] Review incompatible packages for alternatives\n")
            f.write("- [ ] Legal review for acceptable copyleft licenses\n")
            f.write("- [ ] Update ATTRIBUTIONS.md with required attributions\n")
            f.write("- [ ] Document license compliance in distribution\n\n")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    def export_json(self, output_file: str = "docs/legal/license_scan.json"):
        """Export license data as JSON"""
        data = {
            "scan_timestamp": self._get_timestamp(),
            "total_packages": len(self.licenses),
            "compatible_packages": sum(1 for l in self.licenses if l.compatible),
            "packages": [
                {
                    "package": l.package,
                    "version": l.version,
                    "license": l.license,
                    "license_type": l.license_type.value,
                    "compatible": l.compatible
                }
                for l in self.licenses
            ]
        }
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)

def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate license compatibility of project dependencies"
    )
    parser.add_argument(
        "--requirements", 
        default="config/requirements.txt",
        help="Requirements file to check"
    )
    parser.add_argument(
        "--output", 
        default="docs/legal/LICENSE_SCAN.md",
        help="Output report file"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also export JSON data"
    )
    parser.add_argument(
        "--fail-on-incompatible",
        action="store_true",
        help="Exit with error code if incompatible licenses found"
    )
    
    args = parser.parse_args()
    
    validator = LicenseValidator(args.requirements)
    
    # Validate licenses
    all_compatible = validator.validate_all_licenses()
    
    # Generate reports
    validator.generate_license_report(args.output)
    print(f"\n📄 License report generated: {args.output}")
    
    if args.json:
        json_file = args.output.replace('.md', '.json')
        validator.export_json(json_file)
        print(f"📄 JSON data exported: {json_file}")
    
    # Exit with appropriate code
    if args.fail_on_incompatible and not all_compatible:
        print("\n❌ Build failed due to incompatible licenses")
        sys.exit(1)
    elif all_compatible:
        print("\n✅ All licenses are compatible!")
    else:
        print("\n⚠️ Some licenses may need review")
    
    return 0

if __name__ == "__main__":
    main()
