import os
from app.db.session import SessionLocal
from app.db.init_db import init_admin


def main():
    email = os.getenv("ADMIN_EMAIL", "admin@example.com")
    password = os.getenv("ADMIN_PASSWORD", "admin")
    db = SessionLocal()
    try:
        user = init_admin(db, email, password)
        print(f"Admin ready: {user.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
