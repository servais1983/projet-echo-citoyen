"""Tests pour les schémas de l'application."""

import pytest
from pydantic import ValidationError

from app.schemas import (
    UserCreate,
    UserUpdate,
    UserInDB,
    User,
    NotificationCreate,
    NotificationUpdate,
    NotificationInDB,
    Notification,
    Token,
    TokenData
)


def test_user_create_schema():
    """Teste le schéma de création d'utilisateur."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    user = UserCreate(**user_data)
    assert user.email == user_data["email"]
    assert user.password == user_data["password"]
    assert user.full_name == user_data["full_name"]


def test_user_create_schema_validation():
    """Teste la validation du schéma de création d'utilisateur."""
    with pytest.raises(ValidationError):
        UserCreate(
            email="invalid-email",
            password="short",
            full_name="Test User"
        )


def test_user_update_schema():
    """Teste le schéma de mise à jour d'utilisateur."""
    user_data = {
        "email": "updated@example.com",
        "full_name": "Updated Name"
    }
    user = UserUpdate(**user_data)
    assert user.email == user_data["email"]
    assert user.full_name == user_data["full_name"]


def test_user_in_db_schema():
    """Teste le schéma d'utilisateur en base de données."""
    user_data = {
        "id": 1,
        "email": "test@example.com",
        "hashed_password": "hashedpassword123",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }
    user = UserInDB(**user_data)
    assert user.id == user_data["id"]
    assert user.email == user_data["email"]
    assert user.hashed_password == user_data["hashed_password"]
    assert user.full_name == user_data["full_name"]
    assert user.is_active == user_data["is_active"]
    assert user.is_superuser == user_data["is_superuser"]


def test_notification_create_schema():
    """Teste le schéma de création de notification."""
    notification_data = {
        "channel": "email",
        "recipient": "recipient@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "normal"
    }
    notification = NotificationCreate(**notification_data)
    assert notification.channel == notification_data["channel"]
    assert notification.recipient == notification_data["recipient"]
    assert notification.subject == notification_data["subject"]
    assert notification.content == notification_data["content"]
    assert notification.priority == notification_data["priority"]


def test_notification_create_schema_validation():
    """Teste la validation du schéma de création de notification."""
    with pytest.raises(ValidationError):
        NotificationCreate(
            channel="invalid_channel",
            recipient="invalid_email",
            subject="Test Subject",
            content="Test Content",
            priority="invalid_priority"
        )


def test_notification_update_schema():
    """Teste le schéma de mise à jour de notification."""
    notification_data = {
        "subject": "Updated Subject",
        "content": "Updated Content"
    }
    notification = NotificationUpdate(**notification_data)
    assert notification.subject == notification_data["subject"]
    assert notification.content == notification_data["content"]


def test_notification_in_db_schema():
    """Teste le schéma de notification en base de données."""
    notification_data = {
        "id": 1,
        "channel": "email",
        "recipient": "recipient@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "normal",
        "status": "pending",
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00",
        "created_by": 1
    }
    notification = NotificationInDB(**notification_data)
    assert notification.id == notification_data["id"]
    assert notification.channel == notification_data["channel"]
    assert notification.recipient == notification_data["recipient"]
    assert notification.subject == notification_data["subject"]
    assert notification.content == notification_data["content"]
    assert notification.priority == notification_data["priority"]
    assert notification.status == notification_data["status"]
    assert notification.created_at == notification_data["created_at"]
    assert notification.updated_at == notification_data["updated_at"]
    assert notification.created_by == notification_data["created_by"]


def test_token_schema():
    """Teste le schéma de token."""
    token_data = {
        "access_token": "test_token",
        "token_type": "bearer"
    }
    token = Token(**token_data)
    assert token.access_token == token_data["access_token"]
    assert token.token_type == token_data["token_type"]


def test_token_data_schema():
    """Teste le schéma de données de token."""
    token_data = {
        "email": "test@example.com"
    }
    token = TokenData(**token_data)
    assert token.email == token_data["email"] 