from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.enums import UserRole


def test_users_list_admin_only(client, db_session):
    admin = User(email="admin_users@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    viewer = User(email="viewer_users@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([admin, viewer])
    db_session.commit()

    viewer_token = create_access_token(str(viewer.id))
    resp = client.get("/v1/users", headers={"Authorization": f"Bearer {viewer_token}"})
    assert resp.status_code == 403

    admin_token = create_access_token(str(admin.id))
    resp = client.get("/v1/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert any(u["email"] == "admin_users@example.com" for u in data["items"])


def test_users_role_update(client, db_session):
    admin = User(email="admin_users2@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    user = User(email="u_users2@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([admin, user])
    db_session.commit()

    token = create_access_token(str(admin.id))
    resp = client.patch(
        f"/v1/users/{user.id}/role",
        json={"role": "author"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "author"


def test_users_password_update(client, db_session):
    admin = User(email="admin_users3@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    user = User(email="u_users3@example.com", password_hash=hash_password("secret"), role=UserRole.viewer)
    db_session.add_all([admin, user])
    db_session.commit()

    token = create_access_token(str(admin.id))
    resp = client.patch(
        f"/v1/users/{user.id}/password",
        json={"password": "new_secret"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200


def test_users_active_toggle_blocks_login(client, db_session):
    admin = User(email="admin_users4@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    user = User(email="u_users4@example.com", password_hash=hash_password("secret"), role=UserRole.viewer, is_active=True)
    db_session.add_all([admin, user])
    db_session.commit()

    token = create_access_token(str(admin.id))
    resp = client.patch(
        f"/v1/users/{user.id}/active",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    # login is forbidden for inactive user
    resp = client.post("/v1/auth/login", json={"email": "u_users4@example.com", "password": "secret"})
    assert resp.status_code == 403


def test_users_reset_password(client, db_session):
    admin = User(email="admin_users5@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    user = User(email="u_users5@example.com", password_hash=hash_password("old_pw"), role=UserRole.viewer, is_active=True)
    db_session.add_all([admin, user])
    db_session.commit()

    admin_token = create_access_token(str(admin.id))
    resp = client.post(f"/v1/users/{user.id}/reset-password", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    temp_password = resp.json()["temporary_password"]
    assert temp_password

    # Old password no longer works
    resp = client.post("/v1/auth/login", json={"email": "u_users5@example.com", "password": "old_pw"})
    assert resp.status_code == 401

    # Temporary password works
    resp = client.post("/v1/auth/login", json={"email": "u_users5@example.com", "password": temp_password})
    assert resp.status_code == 200
