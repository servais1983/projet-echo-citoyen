"""Tests pour les routes de statistiques."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import Notification, NotificationChannel, NotificationPriority, NotificationStatus


def test_get_notification_stats_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification."""
    response = client.get(
        "/stats/notifications",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "by_channel" in data
    assert "by_priority" in data
    assert "by_status" in data


def test_get_notification_stats_by_date_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification par date."""
    response = client.get(
        "/stats/notifications/by-date",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]
    assert "count" in data[0]


def test_get_notification_stats_by_channel_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification par canal."""
    response = client.get(
        "/stats/notifications/by-channel",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "email" in data
    assert "sms" in data
    assert "push" in data


def test_get_notification_stats_by_priority_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification par priorité."""
    response = client.get(
        "/stats/notifications/by-priority",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "low" in data
    assert "normal" in data
    assert "high" in data
    assert "urgent" in data


def test_get_notification_stats_by_status_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification par statut."""
    response = client.get(
        "/stats/notifications/by-status",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, dict)
    assert "pending" in data
    assert "sent" in data
    assert "delivered" in data
    assert "failed" in data


def test_get_notification_stats_with_filters_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification avec des filtres."""
    response = client.get(
        "/stats/notifications?channel=email&priority=normal&status=pending",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "by_channel" in data
    assert "by_priority" in data
    assert "by_status" in data


def test_get_notification_stats_with_date_range_route(client, test_token, test_notification):
    """Teste la récupération des statistiques de notification avec une plage de dates."""
    response = client.get(
        "/stats/notifications/by-date?start_date=2024-01-01&end_date=2024-12-31",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "date" in data[0]
    assert "count" in data[0]


def test_get_notification_stats_with_invalid_filters(client, test_token):
    """Teste la récupération des statistiques de notification avec des filtres invalides."""
    response = client.get(
        "/stats/notifications?channel=invalid&priority=invalid&status=invalid",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_notification_stats_with_invalid_date_range(client, test_token):
    """Teste la récupération des statistiques de notification avec une plage de dates invalide."""
    response = client.get(
        "/stats/notifications/by-date?start_date=invalid&end_date=invalid",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 