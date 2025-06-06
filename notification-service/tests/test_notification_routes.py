"""Tests pour les routes de notification."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import Notification, NotificationChannel, NotificationPriority, NotificationStatus


def test_create_notification_route(client, test_token):
    """Teste la création d'une notification via l'API."""
    notification_data = {
        "channel": "email",
        "recipient": "recipient@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "normal"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["channel"] == notification_data["channel"]
    assert data["recipient"] == notification_data["recipient"]
    assert data["subject"] == notification_data["subject"]
    assert data["content"] == notification_data["content"]
    assert data["priority"] == notification_data["priority"]
    assert data["status"] == "pending"


def test_get_notification_route(client, test_token, test_notification):
    """Teste la récupération d'une notification via l'API."""
    response = client.get(
        f"/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_notification.id
    assert data["channel"] == test_notification.channel
    assert data["recipient"] == test_notification.recipient


def test_update_notification_route(client, test_token, test_notification):
    """Teste la mise à jour d'une notification via l'API."""
    update_data = {
        "subject": "Updated Subject",
        "content": "Updated Content"
    }
    response = client.put(
        f"/notifications/{test_notification.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["subject"] == update_data["subject"]
    assert data["content"] == update_data["content"]


def test_delete_notification_route(client, test_token, test_notification):
    """Teste la suppression d'une notification via l'API."""
    response = client.delete(
        f"/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(
        f"/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_notifications_route(client, test_token, test_notification):
    """Teste la liste des notifications via l'API."""
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(n["id"] == test_notification.id for n in data)


def test_filter_notifications_route(client, test_token, test_notification):
    """Teste le filtrage des notifications via l'API."""
    response = client.get(
        "/notifications/?channel=email&priority=normal",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(n["channel"] == "email" for n in data)
    assert all(n["priority"] == "normal" for n in data)


def test_get_notification_stats_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification via l'API."""
    response = client.get(
        "/notifications/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "by_channel" in data
    assert "by_priority" in data
    assert "by_status" in data


def test_create_notification_invalid_data(client, test_token):
    """Teste la création d'une notification avec des données invalides."""
    notification_data = {
        "channel": "invalid_channel",
        "recipient": "invalid_email",
        "priority": "invalid_priority"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_notification(client, test_token):
    """Teste la récupération d'une notification inexistante."""
    response = client.get(
        "/notifications/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_notification(client, test_token):
    """Teste la mise à jour d'une notification inexistante."""
    update_data = {
        "subject": "Updated Subject",
        "content": "Updated Content"
    }
    response = client.put(
        "/notifications/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_notification(client, test_token):
    """Teste la suppression d'une notification inexistante."""
    response = client.delete(
        "/notifications/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND 