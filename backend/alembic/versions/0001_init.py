"""init

Revision ID: 0001_init
Revises: 
Create Date: 2026-02-02 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = sa.Enum("admin", "author", "editor", "viewer", name="userrole")
    post_status = sa.Enum(
        "draft",
        "pending",
        "approved",
        "scheduled",
        "published",
        "rejected",
        "failed",
        name="poststatus",
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="author"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "channels",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("telegram_channel_identifier", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_channels_telegram", "channels", ["telegram_channel_identifier"], unique=True)

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("channel_id", sa.Integer, sa.ForeignKey("channels.id"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("media_url", sa.String(500), nullable=True),
        sa.Column("status", post_status, nullable=False, server_default="draft"),
        sa.Column("scheduled_at", sa.DateTime, nullable=True),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("telegram_message_id", sa.String(128), nullable=True),
        sa.Column("last_known_views", sa.Integer, nullable=True),
        sa.Column("publish_attempts", sa.Integer, nullable=False, server_default="0"),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("updated_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("editor_comment", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_posts_channel_id", "posts", ["channel_id"])
    op.create_index("ix_posts_status", "posts", ["status"])

    op.create_table(
        "source_items",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("post_id", sa.Integer, sa.ForeignKey("posts.id"), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=False),
        sa.Column("extracted_text", sa.Text, nullable=False),
        sa.Column("language_detected", sa.String(32), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_source_items_post_id", "source_items", ["post_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("actor_user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("payload_json", sa.JSON, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_audit_logs_entity_id", "audit_logs", ["entity_id"])


def downgrade() -> None:
    op.drop_index("ix_audit_logs_entity_id", table_name="audit_logs")
    op.drop_table("audit_logs")
    op.drop_index("ix_source_items_post_id", table_name="source_items")
    op.drop_table("source_items")
    op.drop_index("ix_posts_status", table_name="posts")
    op.drop_index("ix_posts_channel_id", table_name="posts")
    op.drop_table("posts")
    op.drop_index("ix_channels_telegram", table_name="channels")
    op.drop_table("channels")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS poststatus")
    op.execute("DROP TYPE IF EXISTS userrole")
