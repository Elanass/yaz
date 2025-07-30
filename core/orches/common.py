# orchestrator/common.py
"""
Common utilities for orchestrator module.
"""

import logging
import os
from some_config_loader import load_config  # adjust to your loader
from some_logger import get_logger          # adjust to your logger
from your_di_framework import Container      # optional DI container

# Load global configuration
config = load_config(os.getenv("CONFIG_PATH", "config.yml"))

# Initialize logger
logger = get_logger(name="orches")

# Initialize DI container (if used)
container = Container()
container.register("config", config)
container.register("logger", logger)