from datetime import datetime, timedelta

from app.core.security import hash_password, create_access_token
from app.models.channel import Channel
from app.models.post import Post
from app.models.user import User
from app.models.enums import UserRole, PostStatus


def test_list_schedule_auth(client, db_session):
    user = User(email="u_sched@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add(user)
    db_session.commit()
    token = create_access_token(str(user.id))

    resp = client.get("/v1/schedule", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert "items" in resp.json()


def test_requeue_requires_editor(client, db_session):
    ch = Channel(title="Ch", telegram_channel_identifier="@ch_sched")
    editor = User(email="editor_sched@example.com", password_hash=hash_password("secret"), role=UserRole.editor)
    viewer = User(email="viewer_sched@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([ch, editor, viewer])
    db_session.commit()

    post = Post(
        channel_id=ch.id,
        title="T",
        body_text="B",
        status=PostStatus.failed,
        created_by=editor.id,
        updated_by=editor.id,
        updated_at=datetime.utcnow(),
        created_at=datetime.utcnow(),
        last_error="x",
    )
    db_session.add(post)
    db_session.commit()

    viewer_token = create_access_token(str(viewer.id))
    resp = client.post(
        f"/v1/schedule/posts/{post.id}/requeue",
        json={"delay_seconds": 0},
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403

    editor_token = create_access_token(str(editor.id))
    resp = client.post(
        f"/v1/schedule/posts/{post.id}/requeue",
        json={"delay_seconds": 0},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "scheduled"


def test_list_schedule_filters(client, db_session):
    ch = Channel(title="Ch2", telegram_channel_identifier="@ch_sched2")
    user = User(email="u_sched2@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([ch, user])
    db_session.commit()

    now = datetime.utcnow()
    p1 = Post(
        channel_id=ch.id,
        title="Soon",
        body_text="B",
        status=PostStatus.scheduled,
        scheduled_at=now + timedelta(hours=1),
        created_by=user.id,
        updated_by=user.id,
    )
    db_session.add(p1)
    db_session.commit()

    token = create_access_token(str(user.id))
    resp = client.get(
        "/v1/schedule",
        params={"channel_id": ch.id, "since": (now + timedelta(minutes=30)).isoformat()},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
