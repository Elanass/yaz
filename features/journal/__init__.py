"""
Journal feature for structured clinical documentation.

This package provides comprehensive clinical documentation capabilities
with structured templates, auto-generation of content, and integration
with clinical workflows.
"""

from .service import (
    journal_service,
    JournalService,
    ClinicalTemplate,
    ClinicalNote,
    TemplateSection,
    TemplateField,
    FieldValue,
    SectionValues,
    NoteContributor,
    NoteVersion
)

from .auto_entries import (
    auto_generate_note_content,
    auto_generate_for_protocol,
    auto_generate_followup
)

__all__ = [
    'journal_service',
    'JournalService',
    'ClinicalTemplate',
    'ClinicalNote',
    'TemplateSection',
    'TemplateField',
    'FieldValue',
    'SectionValues',
    'NoteContributor',
    'NoteVersion',
    'auto_generate_note_content',
    'auto_generate_for_protocol',
    'auto_generate_followup'
]
