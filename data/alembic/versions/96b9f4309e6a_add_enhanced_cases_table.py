"""add_enhanced_cases_table

Revision ID: 96b9f4309e6a
Revises: e0c738223574
Create Date: 2025-08-06 22:20:48.232603

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '96b9f4309e6a'
down_revision = 'e0c738223574'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enhanced_cases table
    op.create_table(
        'enhanced_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('case_number', sa.String(50), nullable=True),
        sa.Column('patient_id', sa.String(50), nullable=True),
        sa.Column('surgeon_id', sa.Integer(), nullable=True),
        sa.Column('procedure_type', sa.String(100), nullable=True),
        sa.Column('diagnosis', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=True, default='planned'),
        sa.Column('priority', sa.String(20), nullable=True, default='normal'),
        sa.Column('scheduled_date', sa.DateTime(), nullable=True),
        sa.Column('actual_start', sa.DateTime(), nullable=True),
        sa.Column('actual_end', sa.DateTime(), nullable=True),
        sa.Column('risk_score', sa.Numeric(5, 2), nullable=True),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_number')
    )


def downgrade() -> None:
    op.drop_table('enhanced_cases')
