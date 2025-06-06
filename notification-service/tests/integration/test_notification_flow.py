"""Tests d'intégration pour le service de notification.

Ce module contient les tests d'intégration pour vérifier le bon fonctionnement
du service de notification, incluant la création, la récupération, la mise à jour
et la suppression des notifications.
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Generator, Any, Dict, List

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.models import (
    Notification,
    NotificationChannel,
    NotificationPriority,
    NotificationStatus,
)
from app.schemas import NotificationCreate, NotificationUpdate

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite://"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, Any, None]:
    """Crée une session de base de données pour les tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, Any, None]:
    """Crée un client de test FastAPI."""
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
def test_notification(db_session: Session) -> Notification:
    """Crée une notification de test."""
    notification = Notification(
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        subject="Test Notification",
        content="This is a test notification",
        priority=NotificationPriority.HIGH,
        status=NotificationStatus.PENDING,
        notification_metadata={"test": "data"},
        created_at=datetime.utcnow(),
    )
    db_session.add(notification)
    db_session.commit()
    db_session.refresh(notification)
    return notification


class TestNotificationCRUD:
    """Tests pour les opérations CRUD de base."""

    def test_create_notification(self, client: TestClient, db_session: Session) -> None:
        """Teste la création d'une notification."""
        notification_data = {
            "channel": "EMAIL",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "content": "Test Content",
            "priority": "HIGH",
            "notification_metadata": {"test": "data"}
        }
        response = client.post("/notifications/", json=notification_data)
        assert response.status_code == 201
        data = response.json()
        assert data["channel"] == "EMAIL"
        assert data["recipient"] == "test@example.com"

    def test_get_notification(self, client: TestClient, test_notification: Notification) -> None:
        """Teste la récupération d'une notification."""
        response = client.get(f"/notifications/{test_notification.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_notification.id
        assert data["channel"] == "EMAIL"

    def test_update_notification(self, client: TestClient, test_notification: Notification) -> None:
        """Teste la mise à jour d'une notification."""
        update_data = {
            "subject": "Updated Subject",
            "content": "Updated Content"
        }
        response = client.patch(f"/notifications/{test_notification.id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["subject"] == "Updated Subject"
        assert data["content"] == "Updated Content"

    def test_delete_notification(self, client: TestClient, test_notification: Notification) -> None:
        """Teste la suppression d'une notification."""
        response = client.delete(f"/notifications/{test_notification.id}")
        assert response.status_code == 204
        response = client.get(f"/notifications/{test_notification.id}")
        assert response.status_code == 404


class TestNotificationQueries:
    """Tests pour les requêtes de notifications."""

    def test_list_notifications(self, client: TestClient, test_notification: Notification) -> None:
        """Teste la liste des notifications."""
        response = client.get("/notifications/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["id"] == test_notification.id

    def test_filter_notifications(self, client: TestClient, test_notification: Notification) -> None:
        """Teste le filtrage des notifications."""
        response = client.get("/notifications/?channel=EMAIL&priority=HIGH")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(n["channel"] == "EMAIL" for n in data)
        assert all(n["priority"] == "HIGH" for n in data)


class TestNotificationValidation:
    """Tests pour la validation des notifications."""

    def test_invalid_channel(self, client: TestClient) -> None:
        """Teste la validation d'un canal invalide."""
        notification_data = {
            "channel": "INVALID",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "content": "Test Content",
            "priority": "HIGH"
        }
        response = client.post("/notifications/", json=notification_data)
        assert response.status_code == 422

    def test_invalid_priority(self, client: TestClient) -> None:
        """Teste la validation d'une priorité invalide."""
        notification_data = {
            "channel": "EMAIL",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "content": "Test Content",
            "priority": "INVALID"
        }
        response = client.post("/notifications/", json=notification_data)
        assert response.status_code == 422


class TestNotificationDelivery:
    """Tests pour la livraison des notifications."""

    def test_send_notification(self, client: TestClient, test_notification: Notification) -> None:
        """Teste l'envoi d'une notification."""
        response = client.post(f"/notifications/{test_notification.id}/send")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "SENT"
        assert data["sent_at"] is not None

    def test_batch_send(self, client: TestClient, db_session: Session) -> None:
        """Teste l'envoi en lot de notifications."""
        notifications = [
            {
                "channel": "EMAIL",
                "recipient": f"test{i}@example.com",
                "subject": f"Test {i}",
                "content": f"Content {i}",
                "priority": "HIGH"
            }
            for i in range(3)
        ]
        response = client.post("/notifications/batch", json=notifications)
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3
        assert all(n["status"] == "PENDING" for n in data)


class TestBatchOperations:
    """Tests pour les opérations par lots."""

    def test_batch_create(self, client: TestClient) -> None:
        """Teste la création en lot de notifications."""
        notifications = [
            {
                "channel": "EMAIL",
                "recipient": f"test{i}@example.com",
                "subject": f"Test {i}",
                "content": f"Content {i}",
                "priority": "HIGH"
            }
            for i in range(3)
        ]
        response = client.post("/notifications/batch", json=notifications)
        assert response.status_code == 201
        data = response.json()
        assert len(data) == 3

    def test_batch_update(self, client: TestClient, db_session: Session) -> None:
        """Teste la mise à jour en lot de notifications."""
        # Créer des notifications de test
        notifications = []
        for i in range(3):
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                recipient=f"test{i}@example.com",
                subject=f"Test {i}",
                content=f"Content {i}",
                priority=NotificationPriority.HIGH,
                status=NotificationStatus.PENDING
            )
            db_session.add(notification)
        db_session.commit()

        # Mettre à jour les notifications
        update_data = [
            {"id": n.id, "subject": f"Updated {i}"}
            for i, n in enumerate(notifications)
        ]
        response = client.patch("/notifications/batch", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all(n["subject"].startswith("Updated") for n in data)

    def test_batch_delete(self, client: TestClient, db_session: Session) -> None:
        """Teste la suppression en lot de notifications."""
        # Créer des notifications de test
        notifications = []
        for i in range(3):
            notification = Notification(
                channel=NotificationChannel.EMAIL,
                recipient=f"test{i}@example.com",
                subject=f"Test {i}",
                content=f"Content {i}",
                priority=NotificationPriority.HIGH,
                status=NotificationStatus.PENDING
            )
            db_session.add(notification)
        db_session.commit()

        # Supprimer les notifications
        notification_ids = [n.id for n in notifications]
        response = client.delete("/notifications/batch", json=notification_ids)
        assert response.status_code == 204

        # Vérifier que les notifications ont été supprimées
        for notification_id in notification_ids:
            response = client.get(f"/notifications/{notification_id}")
            assert response.status_code == 404 