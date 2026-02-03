"""add agent settings

Revision ID: 0003_agent_settings
Revises: 0002_channel_avatar
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_agent_settings"
down_revision = "0002_channel_avatar"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("length", sa.Integer(), nullable=False, server_default="400"),
        sa.Column("style", sa.String(length=64), nullable=False, server_default="формальный"),
        sa.Column("format", sa.String(length=64), nullable=False, server_default="статья"),
        sa.Column("temperature", sa.Float(), nullable=False, server_default="0.4"),
        sa.Column("extra", sa.Text(), nullable=True),
        sa.Column("tone_text", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("channel_id"),
    )
    op.create_index(op.f("ix_agent_settings_channel_id"), "agent_settings", ["channel_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_agent_settings_channel_id"), table_name="agent_settings")
    op.drop_table("agent_settings")
