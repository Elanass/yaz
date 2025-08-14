"""
YAZ Healthcare Platform - Applications Module

Organized service architecture:
- External Services (/apps/external/): Open APIs for external integrations  
- Internal Services (/apps/internal/): Restricted platform management

External Services:
- surge: Surgery Analytics Platform
- move: Logistics Management Platform

Internal Services:
- clinica: Clinical Management System
- educa: Medical Education Platform
- insura: Insurance Management System
"""

__all__ = ["external", "internal"]
