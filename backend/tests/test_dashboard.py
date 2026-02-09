from datetime import datetime, timedelta

from app.core.security import hash_password, create_access_token
from app.models.channel import Channel
from app.models.post import Post
from app.models.user import User
from app.models.enums import UserRole, PostStatus


def test_dashboard_overview_requires_auth(client):
    resp = client.get("/v1/dashboard/overview")
    assert resp.status_code == 401


def test_dashboard_overview_aggregates(client, db_session):
    channel = Channel(title="Ch", telegram_channel_identifier="@ch")
    user = User(email="u@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([channel, user])
    db_session.commit()

    now = datetime.utcnow()
    p1 = Post(
        channel_id=channel.id,
        title="Draft",
        body_text="x",
        status=PostStatus.draft,
        created_by=user.id,
        updated_by=user.id,
        created_at=now - timedelta(days=2),
        updated_at=now - timedelta(days=2),
    )
    p2 = Post(
        channel_id=channel.id,
        title="Scheduled future",
        body_text="x",
        status=PostStatus.scheduled,
        scheduled_at=now + timedelta(hours=2),
        created_by=user.id,
        updated_by=user.id,
    )
    p3 = Post(
        channel_id=channel.id,
        title="Scheduled overdue",
        body_text="x",
        status=PostStatus.scheduled,
        scheduled_at=now - timedelta(hours=1),
        created_by=user.id,
        updated_by=user.id,
    )
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    token = create_access_token(str(user.id))
    resp = client.get("/v1/dashboard/overview", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()

    # Totals
    assert data["total_status_counts"]["draft"] >= 1
    assert data["total_status_counts"]["scheduled"] >= 2

    # Per-channel summary
    ch_rows = [r for r in data["channels"] if r["channel_id"] == channel.id]
    assert len(ch_rows) == 1
    row = ch_rows[0]
    assert row["status_counts"]["draft"] == 1
    assert row["status_counts"]["scheduled"] == 2
    assert row["overdue_scheduled_count"] == 1
    assert row["next_scheduled_at"] is not None

