from app.core.security import hash_password, create_access_token
from app.models.channel import Channel
from app.models.user import User
from app.models.enums import UserRole


def test_agent_settings_put_editor_only(client, db_session):
    channel = Channel(title="Ch", telegram_channel_identifier="@ch_agent")
    viewer = User(email="viewer_agent@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    editor = User(email="editor_agent@example.com", password_hash=hash_password("secret"), role=UserRole.editor)
    db_session.add_all([channel, viewer, editor])
    db_session.commit()

    payload = {
        "length": 100,
        "style": "neutral",
        "format": "plain",
        "temperature": 0.3,
        "extra": None,
        "tone_text": None,
        "tone_values": None,
    }

    viewer_token = create_access_token(str(viewer.id))
    resp = client.put(
        f"/v1/channels/{channel.id}/agent-settings",
        json=payload,
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert resp.status_code == 403

    editor_token = create_access_token(str(editor.id))
    resp = client.put(
        f"/v1/channels/{channel.id}/agent-settings",
        json=payload,
        headers={"Authorization": f"Bearer {editor_token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["channel_id"] == channel.id
    assert data["length"] == 100

