"""add channel avatar_url

Revision ID: 0002_channel_avatar
Revises: 0001_init
Create Date: 2026-02-03 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_channel_avatar"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("channels", sa.Column("avatar_url", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("channels", "avatar_url")
