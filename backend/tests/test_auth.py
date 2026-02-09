from app.core.security import hash_password, create_access_token
from app.models.user import User
from app.models.enums import UserRole


def test_login_and_role_enforcement(client, db_session):
    admin = User(email="admin@example.com", password_hash=hash_password("secret"), role=UserRole.admin)
    author = User(email="author@example.com", password_hash=hash_password("secret"), role=UserRole.author)
    db_session.add_all([admin, author])
    db_session.commit()

    resp = client.post("/v1/auth/login", json={"email": "admin@example.com", "password": "secret"})
    assert resp.status_code == 200
    token = resp.json().get("access_token")
    assert token

    author_token = create_access_token(str(author.id))
    resp = client.post(
        "/v1/users/",
        json={"email": "x@example.com", "password": "secret", "role": "author"},
        headers={"Authorization": f"Bearer {author_token}"},
    )
    assert resp.status_code == 403

    resp = client.post(
        "/v1/users/",
        json={"email": "x2@example.com", "password": "secret", "role": "author"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
