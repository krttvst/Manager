from app.core.security import hash_password, create_access_token
from app.models.channel import Channel
from app.models.post import Post
from app.models.user import User
from app.models.enums import UserRole, PostStatus


def test_comments_require_auth(client):
    resp = client.get("/v1/posts/1/comments")
    assert resp.status_code == 401


def test_create_and_list_comments(client, db_session):
    channel = Channel(title="Ch", telegram_channel_identifier="@ch_comments")
    user = User(email="u_comments@example.com", password_hash=hash_password("secret"), role=UserRole.author)
    db_session.add_all([channel, user])
    db_session.commit()

    post = Post(
        channel_id=channel.id,
        title="T",
        body_text="B",
        status=PostStatus.draft,
        created_by=user.id,
        updated_by=user.id,
    )
    db_session.add(post)
    db_session.commit()

    token = create_access_token(str(user.id))
    resp = client.post(
        f"/v1/posts/{post.id}/comments",
        json={"body_text": "Hello"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["post_id"] == post.id
    assert data["author_email"] == "u_comments@example.com"
    assert data["kind"] == "comment"

    resp = client.get(f"/v1/posts/{post.id}/comments", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["body_text"] == "Hello"


def test_reject_creates_comment(client, db_session):
    channel = Channel(title="Ch2", telegram_channel_identifier="@ch_comments2")
    author = User(email="author_comments@example.com", password_hash=hash_password("secret"), role=UserRole.author)
    editor = User(email="editor_comments@example.com", password_hash=hash_password("secret"), role=UserRole.editor)
    db_session.add_all([channel, author, editor])
    db_session.commit()

    post = Post(
        channel_id=channel.id,
        title="T",
        body_text="B",
        status=PostStatus.pending,
        created_by=author.id,
        updated_by=author.id,
    )
    db_session.add(post)
    db_session.commit()

    editor_token = create_access_token(str(editor.id))
    resp = client.post(
        f"/v1/posts/{post.id}/reject",
        json={"comment": "Needs changes"},
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    assert resp.status_code == 200

    resp = client.get(f"/v1/posts/{post.id}/comments", headers={"Authorization": f"Bearer {editor_token}"})
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["kind"] == "reject"
    assert items[0]["body_text"] == "Needs changes"

