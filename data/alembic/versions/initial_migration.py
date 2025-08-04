"""
Initial migration
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String, nullable=False, unique=True),
        sa.Column('email', sa.String, nullable=False, unique=True),
        sa.Column('hashed_password', sa.String, nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('role', sa.String, nullable=False)
    )

    op.create_table(
        'cases',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('patient_id', sa.String, nullable=False),
        sa.Column('surgery_type', sa.String, nullable=False),
        sa.Column('status', sa.String, nullable=False),
        sa.Column('pre_op_notes', sa.Text, nullable=True),
        sa.Column('post_op_notes', sa.Text, nullable=True)
    )

def downgrade():
    op.drop_table('cases')
    op.drop_table('users')
