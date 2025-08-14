"""merge_heads

Revision ID: e0c738223574
Revises: add_manual_entry_tables, 20250805_cockroachdb_migration
Create Date: 2025-08-06 22:19:31.461886

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e0c738223574"
down_revision = ("add_manual_entry_tables", "20250805_cockroachdb_migration")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
