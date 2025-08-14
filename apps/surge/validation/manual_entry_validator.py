"""Manual Entry Validation for Surgify Platform
Creates domain-specific forms and real-time validation hooks.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclass
class ValidationForm:
    name: str
    fields: list[dict[str, Any]]
    validators: list[Callable[[dict[str, Any]], list[str]]] = field(
        default_factory=list
    )

    def add_real_time_validation(self) -> None:
        # Placeholder hook for UI layer to connect websocket/live validation
        pass

    def add_medical_terminology_check(self) -> None:
        # Placeholder for SNOMED/ICD validation integration
        pass

    def add_data_consistency_validation(self) -> None:
        # Placeholder for cross-field consistency checks
        pass


class ManualEntryValidator:
    def create_surgical_entry_form(self) -> ValidationForm:
        return ValidationForm(
            name="surgical_case",
            fields=[
                {"name": "patient_id", "type": "string", "required": True},
                {"name": "age", "type": "number", "required": True},
                {"name": "gender", "type": "string", "required": True},
                {"name": "diagnosis", "type": "string", "required": True},
                {"name": "procedure", "type": "string", "required": True},
                {"name": "outcome", "type": "string", "required": False},
            ],
        )

    def create_cellular_entry_form(self) -> ValidationForm:
        return ValidationForm(
            name="cellular_specimen",
            fields=[
                {"name": "specimen_id", "type": "string", "required": True},
                {"name": "cell_type", "type": "string", "required": True},
                {"name": "marker_panel", "type": "array", "required": False},
                {"name": "experimental_condition", "type": "string", "required": False},
            ],
        )

    def create_hybrid_entry_form(self) -> ValidationForm:
        return ValidationForm(
            name="hybrid_record",
            fields=[
                {"name": "entity_id", "type": "string", "required": True},
                {"name": "domain_link", "type": "string", "required": True},
                {"name": "notes", "type": "string", "required": False},
            ],
        )

    def setup_validation_forms(self, domain: str) -> ValidationForm:
        forms = {
            "surgical": self.create_surgical_entry_form(),
            "cellular": self.create_cellular_entry_form(),
            "hybrid": self.create_hybrid_entry_form(),
        }

        form = forms.get(domain, self.create_surgical_entry_form())
        form.add_real_time_validation()
        form.add_medical_terminology_check()
        form.add_data_consistency_validation()
        return form
