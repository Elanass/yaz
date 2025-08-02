"""
Feature package - Core features of the YAZ surgical decision support platform

This package contains the main feature modules:
- analysis: Statistical modeling and decision support
- auth: Authentication and authorization
- decisions: Decision engines including ADCI framework  
- protocols: Clinical protocol management
"""

# Import all feature modules for easy access
from . import analysis
from . import auth
from . import decisions
from . import protocols

__all__ = [
    'analysis',
    'auth', 
    'decisions',
    'protocols'
]
