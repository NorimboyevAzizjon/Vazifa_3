import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# Test database setup (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Yangi toza test bazasini yaratadi va har bir testdan keyin tozalaydi."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    """Ro'yxatdan o'tgan birinchi test foydalanuvchisining Bearer auth tokeni."""
    register_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "password123",
        "full_name": "Test User",
    }
    client.post("/api/auth/register", json=register_data)

    login_res = client.post("/api/auth/login", json={"username": "testuser", "password": "password123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def second_auth_headers(client):
    """Ikkinchi alohida foydalanuvchining Bearer auth tokeni (izolyatsiyani tekshirish uchun)."""
    register_data = {
        "username": "seconduser",
        "email": "seconduser@example.com",
        "password": "password456",
        "full_name": "Second User",
    }
    client.post("/api/auth/register", json=register_data)

    login_res = client.post("/api/auth/login", json={"username": "seconduser", "password": "password456"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
