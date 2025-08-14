"""Repository interfaces for data access layer."""

from .base import BaseRepository, Repository
from .healthcare import (
    PatientRepository,
    ProviderRepository,
    EncounterRepository,
    ObservationRepository
)

__all__ = [
    "BaseRepository",
    "Repository", 
    "PatientRepository",
    "ProviderRepository",
    "EncounterRepository",
    "ObservationRepository",
]
