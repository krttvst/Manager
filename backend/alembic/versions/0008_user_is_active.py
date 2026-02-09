"""user is_active

Revision ID: 0008_user_is_active
Revises: 0007_post_comments
Create Date: 2026-02-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0008_user_is_active"
down_revision = "0007_post_comments"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.alter_column("users", "is_active", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "is_active")

