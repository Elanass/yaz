"""Shared Pydantic base classes for consistent configuration across the platform."""

from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base model for all API-facing Pydantic models.

    Provides consistent configuration for:
    - Alias support (for protected namespaces like model_*)
    - Attribute population from ORM objects
    - Protected namespace handling
    """

    model_config = ConfigDict(
        protected_namespaces=(),  # Allow model_* field names with aliases
        populate_by_name=True,  # Support both field names and aliases
        from_attributes=True,  # Support ORM object conversion
        arbitrary_types_allowed=True,  # Allow custom types like datetime
    )
