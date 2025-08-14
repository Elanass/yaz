"""Add manual entry tables

Revision ID: add_manual_entry_tables
Revises: 
Create Date: 2025-01-08 00:00:00.000000

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import Column, DateTime, Integer, String, Text

# revision identifiers, used by Alembic.
revision = "add_manual_entry_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create text_entries table
    op.create_table(
        "text_entries",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("patient_id", sa.String(20), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=True),
        sa.Column("entry_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_text_entries_id"), "text_entries", ["id"], unique=False)
    op.create_index(
        op.f("ix_text_entries_patient_id"), "text_entries", ["patient_id"], unique=False
    )
    op.create_index(
        op.f("ix_text_entries_case_id"), "text_entries", ["case_id"], unique=False
    )
    op.create_index(
        op.f("ix_text_entries_created_at"), "text_entries", ["created_at"], unique=False
    )

    # Create media_files table
    op.create_table(
        "media_files",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("patient_id", sa.String(20), nullable=False),
        sa.Column("case_id", sa.String(36), nullable=True),
        sa.Column("media_type", sa.String(20), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("file_path", sa.String(500), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("content_type", sa.String(100), nullable=True),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_media_files_id"), "media_files", ["id"], unique=False)
    op.create_index(
        op.f("ix_media_files_patient_id"), "media_files", ["patient_id"], unique=False
    )
    op.create_index(
        op.f("ix_media_files_case_id"), "media_files", ["case_id"], unique=False
    )
    op.create_index(
        op.f("ix_media_files_created_at"), "media_files", ["created_at"], unique=False
    )


def downgrade():
    # Drop media_files table
    op.drop_index(op.f("ix_media_files_created_at"), table_name="media_files")
    op.drop_index(op.f("ix_media_files_case_id"), table_name="media_files")
    op.drop_index(op.f("ix_media_files_patient_id"), table_name="media_files")
    op.drop_index(op.f("ix_media_files_id"), table_name="media_files")
    op.drop_table("media_files")

    # Drop text_entries table
    op.drop_index(op.f("ix_text_entries_created_at"), table_name="text_entries")
    op.drop_index(op.f("ix_text_entries_case_id"), table_name="text_entries")
    op.drop_index(op.f("ix_text_entries_patient_id"), table_name="text_entries")
    op.drop_index(op.f("ix_text_entries_id"), table_name="text_entries")
    op.drop_table("text_entries")
