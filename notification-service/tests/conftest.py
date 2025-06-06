"""Configuration des tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import User, Notification, Webhook
from app.dependencies import get_password_hash, create_access_token


# Base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Crée une session de base de données pour les tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Crée un client de test."""
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """Crée un utilisateur de test."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_token(test_user):
    """Crée un token de test."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture(scope="function")
def test_notification(db_session, test_user):
    """Crée une notification de test."""
    notification = Notification(
        user_id=test_user.id,
        channel="email",
        recipient="test@example.com",
        subject="Test Subject",
        content="Test Content",
        status="pending"
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification


@pytest.fixture(scope="function")
def test_webhook(db_session, test_user):
    """Crée un webhook de test."""
    webhook = Webhook(
        user_id=test_user.id,
        url="https://example.com/webhook",
        events=["notification.created", "notification.updated"],
        secret="test_secret"
    )
    db_session.add(webhook)
    db_session.commit()
    db_session.refresh(webhook)
    return webhook 