"""Tests pour les opérations CRUD."""

import pytest
from sqlalchemy.orm import Session

from app.crud import (
    create_user,
    get_user,
    get_user_by_email,
    get_users,
    update_user,
    delete_user,
    create_notification,
    get_notification,
    get_notifications,
    update_notification,
    delete_notification
)
from app.models import User, Notification
from app.schemas import UserCreate, UserUpdate, NotificationCreate, NotificationUpdate


def test_create_user_crud(test_db):
    """Teste la création d'un utilisateur via CRUD."""
    user_in = UserCreate(
        email="test@example.com",
        password="testpassword123",
        full_name="Test User"
    )
    user = create_user(test_db, user_in)
    assert user.email == user_in.email
    assert user.full_name == user_in.full_name
    assert user.hashed_password is not None


def test_get_user_crud(test_db, test_user):
    """Teste la récupération d'un utilisateur via CRUD."""
    user = get_user(test_db, test_user.id)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


def test_get_user_by_email_crud(test_db, test_user):
    """Teste la récupération d'un utilisateur par email via CRUD."""
    user = get_user_by_email(test_db, test_user.email)
    assert user is not None
    assert user.id == test_user.id
    assert user.email == test_user.email


def test_get_users_crud(test_db, test_user):
    """Teste la récupération de tous les utilisateurs via CRUD."""
    users = get_users(test_db)
    assert len(users) > 0
    assert any(user.id == test_user.id for user in users)


def test_update_user_crud(test_db, test_user):
    """Teste la mise à jour d'un utilisateur via CRUD."""
    user_in = UserUpdate(
        email="updated@example.com",
        full_name="Updated Name"
    )
    user = update_user(test_db, test_user, user_in)
    assert user.email == user_in.email
    assert user.full_name == user_in.full_name


def test_delete_user_crud(test_db, test_user):
    """Teste la suppression d'un utilisateur via CRUD."""
    delete_user(test_db, test_user)
    user = get_user(test_db, test_user.id)
    assert user is None


def test_create_notification_crud(test_db, test_user):
    """Teste la création d'une notification via CRUD."""
    notification_in = NotificationCreate(
        channel="email",
        recipient="recipient@example.com",
        subject="Test Subject",
        content="Test Content",
        priority="normal"
    )
    notification = create_notification(test_db, notification_in, test_user.id)
    assert notification.channel == notification_in.channel
    assert notification.recipient == notification_in.recipient
    assert notification.subject == notification_in.subject
    assert notification.content == notification_in.content
    assert notification.priority == notification_in.priority
    assert notification.created_by == test_user.id


def test_get_notification_crud(test_db, test_notification):
    """Teste la récupération d'une notification via CRUD."""
    notification = get_notification(test_db, test_notification.id)
    assert notification is not None
    assert notification.id == test_notification.id
    assert notification.channel == test_notification.channel


def test_get_notifications_crud(test_db, test_notification):
    """Teste la récupération de toutes les notifications via CRUD."""
    notifications = get_notifications(test_db)
    assert len(notifications) > 0
    assert any(n.id == test_notification.id for n in notifications)


def test_update_notification_crud(test_db, test_notification):
    """Teste la mise à jour d'une notification via CRUD."""
    notification_in = NotificationUpdate(
        subject="Updated Subject",
        content="Updated Content"
    )
    notification = update_notification(test_db, test_notification, notification_in)
    assert notification.subject == notification_in.subject
    assert notification.content == notification_in.content


def test_delete_notification_crud(test_db, test_notification):
    """Teste la suppression d'une notification via CRUD."""
    delete_notification(test_db, test_notification)
    notification = get_notification(test_db, test_notification.id)
    assert notification is None 