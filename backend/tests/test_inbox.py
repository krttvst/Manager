from app.core.security import hash_password, create_access_token
from app.models.channel import Channel
from app.models.suggestion import Suggestion
from app.models.user import User
from app.models.enums import UserRole


def test_inbox_requires_editor(client, db_session):
    ch = Channel(title="Ch", telegram_channel_identifier="@ch_inbox")
    editor = User(email="editor_inbox@example.com", password_hash=hash_password("secret"), role=UserRole.editor)
    viewer = User(email="viewer_inbox@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([ch, editor, viewer])
    db_session.commit()

    s = Suggestion(
        channel_id=ch.id,
        title="Hello",
        body_text="Body",
        media_url=None,
        source_url="https://example.com/a",
        source_hash="x" * 64,
    )
    db_session.add(s)
    db_session.commit()

    viewer_token = create_access_token(str(viewer.id))
    resp = client.get("/v1/inbox/suggestions", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 403

    editor_token = create_access_token(str(editor.id))
    resp = client.get("/v1/inbox/suggestions", headers={"Authorization": f"Bearer {editor_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["channel_title"] == "Ch"

