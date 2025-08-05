"""
Alembic migration for CockroachDB compatibility
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250805_cockroachdb_migration'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Example: ensure all PKs are compatible, use SERIAL/BIGSERIAL for CockroachDB
    pass

def downgrade():
    pass
