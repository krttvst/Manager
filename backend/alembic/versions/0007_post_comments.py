"""post comments

Revision ID: 0007_post_comments
Revises: 0006_suggestions_source_hash
Create Date: 2026-02-09 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "0007_post_comments"
down_revision = "0006_suggestions_source_hash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "post_comments",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("author_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False, server_default="comment"),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_post_comments_post_id", "post_comments", ["post_id"])
    op.create_index("ix_post_comments_author_user_id", "post_comments", ["author_user_id"])


def downgrade() -> None:
    op.drop_index("ix_post_comments_author_user_id", table_name="post_comments")
    op.drop_index("ix_post_comments_post_id", table_name="post_comments")
    op.drop_table("post_comments")

