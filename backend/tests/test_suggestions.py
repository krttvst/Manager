from app.core.security import hash_password, create_access_token
from app.models.channel import Channel
from app.models.user import User
from app.models.enums import UserRole


def test_suggestions_idempotent(client, db_session):
    channel = Channel(title="Test", telegram_channel_identifier="@test")
    db_session.add(channel)
    db_session.commit()

    payload = {
        "title": "News",
        "body_text": "Body",
        "source_url": "https://example.com/news-1",
        "media_url": None,
    }
    headers = {"X-API-Key": "test-n8n-key"}

    resp = client.post(f"/v1/channels/{channel.id}/suggestions", json=payload, headers=headers)
    assert resp.status_code == 200

    resp = client.post(f"/v1/channels/{channel.id}/suggestions", json=payload, headers=headers)
    assert resp.status_code == 409


def test_suggestions_accept_reject(client, db_session):
    channel = Channel(title="Test 2", telegram_channel_identifier="@test2")
    editor = User(email="editor@example.com", password_hash=hash_password("secret"), role=UserRole.editor)
    db_session.add_all([channel, editor])
    db_session.commit()

    headers = {"X-API-Key": "test-n8n-key"}
    payload = {"title": "News A", "body_text": "Body A", "source_url": "https://example.com/a"}
    resp = client.post(f"/v1/channels/{channel.id}/suggestions", json=payload, headers=headers)
    assert resp.status_code == 200
    suggestion_id = resp.json()["id"]

    token = create_access_token(str(editor.id))
    resp = client.post(
        f"/v1/channels/{channel.id}/suggestions/{suggestion_id}/accept",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "draft"

    resp = client.get(
        f"/v1/channels/{channel.id}/suggestions",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json() == []

    payload = {"title": "News B", "body_text": "Body B", "source_url": "https://example.com/b"}
    resp = client.post(f"/v1/channels/{channel.id}/suggestions", json=payload, headers=headers)
    assert resp.status_code == 200
    suggestion_id = resp.json()["id"]

    resp = client.delete(
        f"/v1/channels/{channel.id}/suggestions/{suggestion_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 204
