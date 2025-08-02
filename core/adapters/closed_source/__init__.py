"""
Closed Source Adapters Module
Enterprise-grade proprietary integrations
"""

from .closed_source_adapter import (
    ClosedSourceAdapter,
    get_closed_source_adapter,
    is_enterprise_licensed
)

__all__ = [
    "ClosedSourceAdapter",
    "get_closed_source_adapter", 
    "is_enterprise_licensed"
]
