"""Add gastric domain entity models

Revision ID: gastric_entities_001
Revises: e0c738223574
Create Date: 2025-08-10 12:00:00.000000

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "gastric_entities_001"
down_revision = "e0c738223574"
branch_labels = None
depends_on = None


def upgrade():
    """Add tables for gastric system, tumor unit, and cell entity models"""

    # Create gastric_systems table
    op.create_table(
        "gastric_systems",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("system_id", sa.String(255), nullable=False, unique=True),
        sa.Column("patient_id", sa.String(255), nullable=False),
        sa.Column("primary_region", sa.String(50), nullable=False),
        sa.Column("involved_regions", sa.JSON(), nullable=True),
        sa.Column("functional_status", sa.String(50), nullable=False),
        sa.Column("gastric_emptying_time", sa.Float(), nullable=True),
        sa.Column("acid_production_level", sa.String(50), nullable=True),
        sa.Column("wall_thickness_mm", sa.Float(), nullable=True),
        sa.Column("mucosal_integrity", sa.String(100), nullable=True),
        sa.Column("vascular_supply", sa.String(100), nullable=True),
        sa.Column("prior_interventions", sa.JSON(), nullable=True),
        sa.Column("anatomical_variants", sa.JSON(), nullable=True),
        sa.Column("assessment_date", sa.DateTime(), nullable=False),
        sa.Column("assessed_by", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gastric_systems_patient_id", "gastric_systems", ["patient_id"])

    # Create tumor_units table
    op.create_table(
        "tumor_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tumor_id", sa.String(255), nullable=False, unique=True),
        sa.Column("case_id", sa.String(255), nullable=False),
        sa.Column("patient_id", sa.String(255), nullable=False),
        sa.Column("t_stage", sa.String(10), nullable=False),
        sa.Column("n_stage", sa.String(10), nullable=False),
        sa.Column("m_stage", sa.String(10), nullable=False),
        sa.Column("overall_stage", sa.String(10), nullable=True),
        sa.Column("histology_type", sa.String(100), nullable=False),
        sa.Column("tumor_grade", sa.String(10), nullable=False),
        sa.Column("primary_location", sa.String(50), nullable=False),
        sa.Column("tumor_size_cm", sa.Float(), nullable=True),
        sa.Column("depth_of_invasion", sa.String(100), nullable=True),
        sa.Column("lymph_nodes_examined", sa.Integer(), nullable=True),
        sa.Column("lymph_nodes_positive", sa.Integer(), nullable=True),
        sa.Column("resection_margin", sa.String(10), nullable=True),
        sa.Column("proximal_margin_cm", sa.Float(), nullable=True),
        sa.Column("distal_margin_cm", sa.Float(), nullable=True),
        sa.Column("circumferential_margin_mm", sa.Float(), nullable=True),
        sa.Column("her2_status", sa.String(50), nullable=True),
        sa.Column("her2_score", sa.String(10), nullable=True),
        sa.Column("msi_status", sa.String(50), nullable=True),
        sa.Column("pdl1_expression", sa.Float(), nullable=True),
        sa.Column("ebv_status", sa.String(50), nullable=True),
        sa.Column("molecular_subtype", sa.String(100), nullable=True),
        sa.Column("genetic_alterations", sa.JSON(), nullable=True),
        sa.Column("mutation_burden", sa.String(50), nullable=True),
        sa.Column("radiological_size_cm", sa.Float(), nullable=True),
        sa.Column("imaging_features", sa.JSON(), nullable=True),
        sa.Column("pathology_date", sa.DateTime(), nullable=True),
        sa.Column("pathologist", sa.String(255), nullable=True),
        sa.Column("specimen_type", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tumor_units_patient_id", "tumor_units", ["patient_id"])
    op.create_index("ix_tumor_units_case_id", "tumor_units", ["case_id"])

    # Create independent_cell_entities table
    op.create_table(
        "independent_cell_entities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cell_entity_id", sa.String(255), nullable=False, unique=True),
        sa.Column("tumor_id", sa.String(255), nullable=False),
        sa.Column("sample_id", sa.String(255), nullable=True),
        sa.Column("her2_expression", sa.String(50), nullable=True),
        sa.Column("her2_gene_amplification", sa.Boolean(), nullable=True),
        sa.Column("her2_fish_ratio", sa.Float(), nullable=True),
        sa.Column("ki67_percentage", sa.Float(), nullable=True),
        sa.Column("mitotic_rate", sa.Integer(), nullable=True),
        sa.Column("mlh1_expression", sa.String(50), nullable=True),
        sa.Column("msh2_expression", sa.String(50), nullable=True),
        sa.Column("msh6_expression", sa.String(50), nullable=True),
        sa.Column("pms2_expression", sa.String(50), nullable=True),
        sa.Column("msi_status", sa.String(50), nullable=True),
        sa.Column("pdl1_expression", sa.Float(), nullable=True),
        sa.Column("pdl1_cps_score", sa.Float(), nullable=True),
        sa.Column("cd8_til_density", sa.String(50), nullable=True),
        sa.Column("p53_expression", sa.String(50), nullable=True),
        sa.Column("p53_mutation_status", sa.String(50), nullable=True),
        sa.Column("e_cadherin_expression", sa.String(50), nullable=True),
        sa.Column("beta_catenin_pattern", sa.String(100), nullable=True),
        sa.Column("cyclin_d1_expression", sa.String(50), nullable=True),
        sa.Column("rb_expression", sa.String(50), nullable=True),
        sa.Column("cell_morphology", sa.String(255), nullable=True),
        sa.Column("tissue_architecture", sa.String(255), nullable=True),
        sa.Column("stromal_reaction", sa.String(255), nullable=True),
        sa.Column("staining_method", sa.String(255), nullable=True),
        sa.Column("antibody_clone", sa.String(255), nullable=True),
        sa.Column("analysis_date", sa.DateTime(), nullable=False),
        sa.Column("analyzed_by", sa.String(255), nullable=True),
        sa.Column("tissue_quality", sa.String(100), nullable=True),
        sa.Column("fixation_time", sa.Float(), nullable=True),
        sa.Column("processing_protocol", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_independent_cell_entities_tumor_id",
        "independent_cell_entities",
        ["tumor_id"],
    )


def downgrade():
    """Remove gastric domain entity tables"""
    op.drop_index("ix_independent_cell_entities_tumor_id", "independent_cell_entities")
    op.drop_table("independent_cell_entities")

    op.drop_index("ix_tumor_units_case_id", "tumor_units")
    op.drop_index("ix_tumor_units_patient_id", "tumor_units")
    op.drop_table("tumor_units")

    op.drop_index("ix_gastric_systems_patient_id", "gastric_systems")
    op.drop_table("gastric_systems")
