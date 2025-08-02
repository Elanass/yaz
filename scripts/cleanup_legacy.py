#!/usr/bin/env python3
"""
Cleanup script for unused legacy files and __pycache__ directories
"""
import os
import shutil
from pathlib import Path

def cleanup_legacy_files():
    """Remove unused legacy files"""
    workspace = Path("/workspaces/yaz")
    
    # Find legacy files that aren't imported anywhere
    legacy_files = list(workspace.glob("**/legacy_*.py"))
    
    print("🧹 Cleaning up legacy files...")
    for file in legacy_files:
        print(f"   Removing: {file}")
        file.unlink()
    
    print(f"✅ Removed {len(legacy_files)} legacy files")

def cleanup_pycache():
    """Remove __pycache__ directories"""
    workspace = Path("/workspaces/yaz")
    
    print("🧹 Cleaning up __pycache__ directories...")
    pycache_dirs = list(workspace.glob("**/__pycache__"))
    
    for dir_path in pycache_dirs:
        if ".venv" not in str(dir_path):  # Don't touch virtual environment
            print(f"   Removing: {dir_path}")
            shutil.rmtree(dir_path)
    
    print(f"✅ Removed {len(pycache_dirs)} __pycache__ directories")

def cleanup_pyc_files():
    """Remove .pyc files"""
    workspace = Path("/workspaces/yaz")
    
    print("🧹 Cleaning up .pyc files...")
    pyc_files = list(workspace.glob("**/*.pyc"))
    
    for file in pyc_files:
        if ".venv" not in str(file):  # Don't touch virtual environment
            print(f"   Removing: {file}")
            file.unlink()
    
    print(f"✅ Removed {len(pyc_files)} .pyc files")

if __name__ == "__main__":
    print("🚀 Starting codebase cleanup...")
    cleanup_legacy_files()
    cleanup_pycache()
    cleanup_pyc_files()
    print("✨ Cleanup completed!")
