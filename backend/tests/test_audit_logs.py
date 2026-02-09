from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.enums import UserRole
from app.services.audit import log_action


def test_audit_logs_admin_only(client, db_session):
    admin = User(email="admin_audit@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    viewer = User(email="viewer_audit@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([admin, viewer])
    db_session.commit()

    log_action(db_session, "post", 1, "create", admin.id, {"status": "draft"})

    viewer_token = create_access_token(str(viewer.id))
    resp = client.get("/v1/audit-logs", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 403

    admin_token = create_access_token(str(admin.id))
    resp = client.get("/v1/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1
    assert data["items"][0]["actor_email"] == "admin_audit@example.com"


def test_audit_logs_filtering(client, db_session):
    admin = User(email="admin2_audit@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    db_session.add(admin)
    db_session.commit()

    log_action(db_session, "post", 10, "create", admin.id, {"status": "draft"})
    log_action(db_session, "post", 10, "update", admin.id, {"status": "pending"})
    log_action(db_session, "channel", 2, "delete", admin.id, {"post_ids": [1, 2]})

    token = create_access_token(str(admin.id))
    resp = client.get(
        "/v1/audit-logs",
        params={"entity_type": "post", "entity_id": 10, "action": "update"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["entity_type"] == "post"
    assert data["items"][0]["entity_id"] == 10
    assert data["items"][0]["action"] == "update"
