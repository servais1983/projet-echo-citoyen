"""Tests pour les modèles de l'application."""

import pytest
from sqlalchemy.orm import Session

from app.models import (
    User,
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus
)


def test_create_user(test_db):
    """Teste la création d'un utilisateur."""
    user = User(
        email="test@example.com",
        hashed_password="hashedpassword123",
        full_name="Test User"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashedpassword123"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False


def test_create_notification(test_db, test_user):
    """Teste la création d'une notification."""
    notification = Notification(
        channel=NotificationChannel.EMAIL,
        recipient="recipient@example.com",
        subject="Test Subject",
        content="Test Content",
        priority=NotificationPriority.NORMAL,
        status=NotificationStatus.PENDING,
        created_by=test_user.id
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    assert notification.id is not None
    assert notification.channel == NotificationChannel.EMAIL
    assert notification.recipient == "recipient@example.com"
    assert notification.subject == "Test Subject"
    assert notification.content == "Test Content"
    assert notification.priority == NotificationPriority.NORMAL
    assert notification.status == NotificationStatus.PENDING
    assert notification.created_by == test_user.id


def test_notification_relationships(test_db, test_user):
    """Teste les relations de la notification."""
    notification = Notification(
        channel=NotificationChannel.EMAIL,
        recipient="recipient@example.com",
        subject="Test Subject",
        content="Test Content",
        priority=NotificationPriority.NORMAL,
        status=NotificationStatus.PENDING,
        created_by=test_user.id
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    assert notification.creator is not None
    assert notification.creator.id == test_user.id
    assert notification.creator.email == test_user.email


def test_notification_status_transitions(test_db, test_user):
    """Teste les transitions d'état des notifications."""
    notification = Notification(
        channel=NotificationChannel.EMAIL,
        recipient="recipient@example.com",
        subject="Test Subject",
        content="Test Content",
        priority=NotificationPriority.NORMAL,
        status=NotificationStatus.PENDING,
        created_by=test_user.id
    )
    test_db.add(notification)
    test_db.commit()
    test_db.refresh(notification)

    # Transition vers SENT
    notification.status = NotificationStatus.SENT
    test_db.commit()
    test_db.refresh(notification)
    assert notification.status == NotificationStatus.SENT

    # Transition vers DELIVERED
    notification.status = NotificationStatus.DELIVERED
    test_db.commit()
    test_db.refresh(notification)
    assert notification.status == NotificationStatus.DELIVERED

    # Transition vers FAILED
    notification.status = NotificationStatus.FAILED
    test_db.commit()
    test_db.refresh(notification)
    assert notification.status == NotificationStatus.FAILED


def test_notification_priority_levels(test_db, test_user):
    """Teste les différents niveaux de priorité des notifications."""
    priorities = [
        NotificationPriority.LOW,
        NotificationPriority.NORMAL,
        NotificationPriority.HIGH,
        NotificationPriority.URGENT
    ]

    for priority in priorities:
        notification = Notification(
            channel=NotificationChannel.EMAIL,
            recipient="recipient@example.com",
            subject=f"Test {priority}",
            content="Test Content",
            priority=priority,
            status=NotificationStatus.PENDING,
            created_by=test_user.id
        )
        test_db.add(notification)
        test_db.commit()
        test_db.refresh(notification)
        assert notification.priority == priority 