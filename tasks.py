#!/usr/bin/env python3
"""
Surgify Platform Task Runner
Provides utility tasks for development, testing, and deployment
"""

import subprocess
import sys
from pathlib import Path

def lint():
    """Run linting checks"""
    print("🔍 Running linting checks...")
    try:
        subprocess.run(["python", "-m", "flake8", "src/", "--max-line-length=88"], check=True)
        print("✅ Linting passed")
    except subprocess.CalledProcessError:
        print("❌ Linting failed")
        sys.exit(1)

def format_code():
    """Format code with black and isort"""
    print("🎨 Formatting code...")
    subprocess.run(["python", "-m", "black", "src/"], check=False)
    subprocess.run(["python", "-m", "isort", "src/"], check=False)
    print("✅ Code formatted")

def test():
    """Run tests"""
    print("🧪 Running tests...")
    try:
        subprocess.run(["python", "-m", "pytest", "tests/", "-v"], check=True)
        print("✅ Tests passed")
    except subprocess.CalledProcessError:
        print("❌ Tests failed")
        sys.exit(1)

def validate():
    """Run validation checks"""
    print("🚀 Running validation...")
    subprocess.run(["python", "tools/validate_surgify.py"], check=False)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tasks.py <command>")
        print("Commands: lint, format, test, validate")
        sys.exit(1)
    
    command = sys.argv[1]
    if command == "lint":
        lint()
    elif command == "format":
        format_code() 
    elif command == "test":
        test()
    elif command == "validate":
        validate()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
