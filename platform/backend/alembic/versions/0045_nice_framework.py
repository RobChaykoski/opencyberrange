"""Add NICE Framework reference data and lab mappings.

Revision ID: 0045_nice_framework
Revises: 0044_readiness_case_owner
Create Date: 2026-11-19

The NICE tables are global reference data. They carry no learner or tenant
identity, so they are deliberately outside tenant RLS.

The application calls ``Base.metadata.create_all`` during startup before the
Alembic upgrade. That can create these tables first, so every create is guarded
by an inspector check; the revision still stamps the database at 0045.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0045_nice_framework"
down_revision: Union[str, None] = "0044_readiness_case_owner"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    binding = op.get_bind()
    inspector = sa.inspect(binding)

    if not inspector.has_table("nice_components"):
        op.create_table(
            "nice_components",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("component_type", sa.String(20), nullable=False),
            sa.Column("code", sa.String(32), nullable=False),
            sa.Column("name", sa.String(200), nullable=True),
            sa.Column("statement", sa.Text(), nullable=True),
            sa.Column("category_code", sa.String(16), nullable=True),
            sa.Column("category_name", sa.String(120), nullable=True),
            sa.Column("version", sa.String(16), nullable=False),
            sa.Column(
                "is_active", sa.Boolean(), nullable=False, server_default=sa.true()
            ),
            sa.Column(
                "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.Column(
                "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.UniqueConstraint(
                "component_type", "code", name="uq_nice_component_type_code"
            ),
        )
        op.create_index(
            "ix_nice_components_component_type", "nice_components", ["component_type"]
        )
        op.create_index("ix_nice_components_code", "nice_components", ["code"])
        op.create_index(
            "ix_nice_components_type_code", "nice_components", ["component_type", "code"]
        )

    if not inspector.has_table("nice_links"):
        op.create_table(
            "nice_links",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "source_id",
                sa.Integer(),
                sa.ForeignKey("nice_components.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "target_id",
                sa.Integer(),
                sa.ForeignKey("nice_components.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("link_type", sa.String(24), nullable=False),
            sa.Column(
                "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.UniqueConstraint(
                "source_id", "target_id", "link_type", name="uq_nice_link"
            ),
        )
        op.create_index("ix_nice_links_source_id", "nice_links", ["source_id"])
        op.create_index("ix_nice_links_target_id", "nice_links", ["target_id"])
        op.create_index(
            "ix_nice_links_source_type", "nice_links", ["source_id", "link_type"]
        )

    if not inspector.has_table("nice_framework_meta"):
        op.create_table(
            "nice_framework_meta",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("version", sa.String(16), nullable=False),
            sa.Column("source", sa.String(24), nullable=False),
            sa.Column("source_url", sa.String(500), nullable=True),
            sa.Column(
                "fetched_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.Column("counts", sa.Text(), nullable=True),
            sa.Column(
                "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.Column(
                "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
        )

    if not inspector.has_table("lab_nice_components"):
        op.create_table(
            "lab_nice_components",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column(
                "lab_id",
                sa.Integer(),
                sa.ForeignKey("labs.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "component_id",
                sa.Integer(),
                sa.ForeignKey("nice_components.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column(
                "created_by_id",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            ),
            sa.Column(
                "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False
            ),
            sa.UniqueConstraint(
                "lab_id", "component_id", name="uq_lab_nice_component"
            ),
        )
        op.create_index(
            "ix_lab_nice_components_lab_id", "lab_nice_components", ["lab_id"]
        )
        op.create_index(
            "ix_lab_nice_components_component_id",
            "lab_nice_components",
            ["component_id"],
        )


def downgrade() -> None:
    op.drop_table("lab_nice_components")
    op.drop_table("nice_framework_meta")
    op.drop_table("nice_links")
    op.drop_table("nice_components")
