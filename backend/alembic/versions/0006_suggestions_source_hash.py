"""suggestions source hash

Revision ID: 0006_suggestions_source_hash
Revises: 0005_suggestions
Create Date: 2026-02-04 12:30:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0006_suggestions_source_hash"
down_revision = "0005_suggestions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("suggestions", sa.Column("source_hash", sa.String(length=64), nullable=True))
    op.create_index("ix_suggestions_source_hash", "suggestions", ["source_hash"])
    op.create_unique_constraint("uq_suggestions_channel_source_hash", "suggestions", ["channel_id", "source_hash"])

    op.execute(
        """
        UPDATE suggestions
        SET source_hash = lpad(md5(COALESCE(source_url, title || '\n' || body_text)), 64, '0')
        WHERE source_hash IS NULL
        """
    )
    op.alter_column("suggestions", "source_hash", nullable=False)


def downgrade() -> None:
    op.drop_constraint("uq_suggestions_channel_source_hash", "suggestions", type_="unique")
    op.drop_index("ix_suggestions_source_hash", table_name="suggestions")
    op.drop_column("suggestions", "source_hash")
