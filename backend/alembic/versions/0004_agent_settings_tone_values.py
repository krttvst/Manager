"""add agent settings tone values

Revision ID: 0004_agent_settings_tone_values
Revises: 0003_agent_settings
Create Date: 2026-02-03
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_agent_settings_tone_values"
down_revision = "0003_agent_settings"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agent_settings", sa.Column("tone_values", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("agent_settings", "tone_values")
