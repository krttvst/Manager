import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure env vars are set before importing app/settings.
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_SECRET", "test_secret")
os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")
os.environ.setdefault("N8N_API_KEY", "test-n8n-key")
os.environ.setdefault("MEDIA_DIR", "/tmp/manager_tg_test_media")

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402
from app.db import base_class_imports  # noqa: F401,E402
from app.api.deps import get_db  # noqa: E402
from app.main import app  # noqa: E402


connect_args = {"check_same_thread": False}
if settings.database_url.endswith(":memory:"):
    # For sqlite :memory: each new connection is a fresh DB unless we reuse the same connection.
    engine = create_engine(settings.database_url, connect_args=connect_args, poolclass=StaticPool)
else:
    engine = create_engine(settings.database_url, connect_args=connect_args)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="session")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
