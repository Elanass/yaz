#!/usr/bin/env python3
"""
Task runner for Surgify Platform
Provides linting, formatting, and other development tasks
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: str, description: str = "") -> bool:
    """Run a shell command and return success status"""
    if description:
        print(f"🔄 {description}")
    
    try:
        result = subprocess.run(
            cmd.split(), 
            capture_output=True, 
            text=True, 
            cwd=Path(__file__).parent.parent  # Go up to workspace root
        )
        
        if result.returncode == 0:
            if description:
                print(f"✅ {description} completed successfully")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running command '{cmd}': {e}")
        return False


def lint():
    """Run linting checks"""
    print("🔍 Running linting checks...")
    
    # Check if flake8 is available
    try:
        subprocess.run(["flake8", "--version"], capture_output=True, check=True)
        flake8_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        flake8_available = False
    
    if flake8_available:
        success = run_command(
            "flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503", 
            "Running flake8 linting"
        )
        if not success:
            return False
    else:
        print("⚠️  flake8 not available, skipping linting")
    
    # Run mypy if available
    try:
        subprocess.run(["mypy", "--version"], capture_output=True, check=True)
        mypy_available = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        mypy_available = False
    
    if mypy_available:
        success = run_command(
            "mypy src/ --ignore-missing-imports", 
            "Running mypy type checking"
        )
        if not success:
            print("⚠️  mypy found issues, but continuing...")
    else:
        print("⚠️  mypy not available, skipping type checking")
    
    print("✅ Linting checks completed")
    return True


def format_code():
    """Format code with black and isort"""
    print("🎨 Formatting code...")
    
    success = run_command(
        "black src/ tests/", 
        "Formatting with black"
    )
    if not success:
        return False
    
    success = run_command(
        "isort src/ tests/ --profile black", 
        "Sorting imports with isort"
    )
    if not success:
        return False
    
    print("✅ Code formatting completed")
    return True


def test():
    """Run tests"""
    print("🧪 Running tests...")
    
    success = run_command(
        "python -m pytest tests/unit/ -v", 
        "Running unit tests"
    )
    
    if success:
        print("✅ All tests passed")
    else:
        print("❌ Some tests failed")
    
    return success


def main():
    """Main task runner"""
    parser = argparse.ArgumentParser(description="Surgify Platform Task Runner")
    parser.add_argument(
        "task", 
        choices=["lint", "format", "test", "all"],
        help="Task to run"
    )
    
    args = parser.parse_args()
    
    if args.task == "lint":
        success = lint()
    elif args.task == "format":
        success = format_code()
    elif args.task == "test":
        success = test()
    elif args.task == "all":
        success = format_code() and lint() and test()
    else:
        print(f"Unknown task: {args.task}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
