"""initial documents table

Revision ID: 0001
Revises:
Create Date: 2026-05-18

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("filename", sa.String(length=512), nullable=False),
        sa.Column("page_count", sa.Integer(), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("content_markdown", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("documents")
