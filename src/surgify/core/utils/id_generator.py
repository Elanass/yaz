"""
ID Generator Utility

Provides functions to generate unique identifiers across the platform.
"""

import uuid


def generate_id(prefix: str = "", length: int = 12) -> str:
    """
    Generate a unique identifier string with an optional prefix.

    Args:
        prefix: Optional string to prepend to the ID.
        length: Number of characters from the UUID hex string.

    Returns:
        A unique identifier string.
    """
    return f"{prefix}{uuid.uuid4().hex[:length]}"
