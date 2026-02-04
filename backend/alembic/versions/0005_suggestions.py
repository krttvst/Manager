"""suggestions

Revision ID: 0005_suggestions
Revises: 0004_agent_settings_tone_values
Create Date: 2026-02-04 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0005_suggestions"
down_revision = "0004_agent_settings_tone_values"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "suggestions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("channel_id", sa.Integer(), sa.ForeignKey("channels.id"), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body_text", sa.Text(), nullable=False),
        sa.Column("media_url", sa.String(length=500), nullable=True),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_suggestions_channel_id", "suggestions", ["channel_id"])


def downgrade() -> None:
    op.drop_index("ix_suggestions_channel_id", table_name="suggestions")
    op.drop_table("suggestions")
