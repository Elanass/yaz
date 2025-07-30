# orchestrator/common.py
"""
Common utilities for orchestrator module.
"""

import logging

# Initialize global configuration (placeholder)
config = {
    "license": "LICENSE_KEY_PLACEHOLDER"
}

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrator")