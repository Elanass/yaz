#!/usr/bin/env python3
"""
Surgify Platform Entry Point
Clean entry point that imports from the organized src structure
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set PYTHONPATH environment variable
os.environ['PYTHONPATH'] = str(src_path)

from surgify.main import main

if __name__ == "__main__":
    main()
