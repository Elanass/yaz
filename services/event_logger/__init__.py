"""
Event Logger package for HIPAA/GDPR compliant audit trails.

This package provides comprehensive event logging for clinical applications,
ensuring proper tracking of all data access, modifications, and clinical
decisions.
"""

from .service import (
    event_logger,
    EventLogger,
    EventLog,
    EventSeverity,
    EventCategory,
    EventSource,
    EventContext,
    EventData,
    log_clinical_decision,
    log_data_access,
    log_protocol_deviation
)

__all__ = [
    'event_logger',
    'EventLogger',
    'EventLog',
    'EventSeverity',
    'EventCategory',
    'EventSource',
    'EventContext',
    'EventData',
    'log_clinical_decision',
    'log_data_access',
    'log_protocol_deviation'
]
