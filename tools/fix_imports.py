#!/usr/bin/env python3
"""
Fix absolute imports to relative imports in surgify codebase
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path):
    """Fix absolute surgify imports in a single file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # Calculate relative path depth
        src_path = Path('src/surgify')
        relative_path = file_path.relative_to(src_path)
        depth = len(relative_path.parts) - 1
        
        # Create the appropriate relative import prefix
        if depth == 0:
            prefix = "."
        elif depth == 1:
            prefix = ".."
        else:
            prefix = "..." + "." * (depth - 2)
        
        # Fix patterns like: from surgify.core.config import ...
        pattern = r'from surgify\.([^.\s]+(?:\.[^.\s]+)*)'
        replacement = f'from {prefix}\\1'
        content = re.sub(pattern, replacement, content)
        
        # Fix patterns like: import surgify.core.config
        pattern = r'import surgify\.([^.\s]+(?:\.[^.\s]+)*)'
        replacement = f'from {prefix} import \\1'
        content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ Fixed imports in {file_path}")
            return True
        else:
            print(f"⚪ No changes needed in {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all absolute imports in the codebase"""
    src_dir = Path('src/surgify')
    if not src_dir.exists():
        print("❌ src/surgify directory not found")
        return
    
    fixed_count = 0
    total_count = 0
    
    for py_file in src_dir.rglob('*.py'):
        if py_file.name == '__init__.py':
            continue
        total_count += 1
        if fix_imports_in_file(py_file):
            fixed_count += 1
    
    print(f"\n📊 Import Fix Summary:")
    print(f"   Files processed: {total_count}")
    print(f"   Files modified: {fixed_count}")
    print(f"   Files unchanged: {total_count - fixed_count}")

if __name__ == "__main__":
    main()
