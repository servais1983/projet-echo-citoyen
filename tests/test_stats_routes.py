import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import NotificationChannel, NotificationPriority, NotificationStatus

def test_get_notification_stats(client, test_token):
    """Teste la récupération des statistiques des notifications."""
    response = client.get(
        "/stats/notifications",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "by_channel" in data
    assert "by_status" in data
    assert "by_priority" in data
    assert "success_rate" in data

def test_get_user_stats(client, test_token):
    """Teste la récupération des statistiques des utilisateurs."""
    response = client.get(
        "/stats/users",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "active" in data
    assert "inactive" in data
    assert "by_role" in data

def test_get_template_stats(client, test_token):
    """Teste la récupération des statistiques des templates."""
    response = client.get(
        "/stats/templates",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "by_channel" in data
    assert "most_used" in data

def test_get_webhook_stats(client, test_token):
    """Teste la récupération des statistiques des webhooks."""
    response = client.get(
        "/stats/webhooks",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "active" in data
    assert "by_event" in data
    assert "delivery_success_rate" in data

def test_get_stats_with_filters(client, test_token):
    """Teste la récupération des statistiques avec des filtres de date."""
    params = {
        "start_date": (datetime.now() - timedelta(days=7)).isoformat(),
        "end_date": datetime.now().isoformat()
    }
    response = client.get(
        "/stats/notifications",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert "by_channel" in data
    assert "by_status" in data

def test_get_stats_unauthorized(client):
    """Teste la récupération des statistiques sans autorisation."""
    response = client.get("/stats/notifications")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_stats_invalid_filters(client, test_token):
    """Teste la récupération des statistiques avec des filtres invalides."""
    params = {
        "start_date": "invalid_date",
        "end_date": "invalid_date"
    }
    response = client.get(
        "/stats/notifications",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_get_stats_with_channel_filter(client, test_token):
    """Teste la récupération des statistiques filtrées par canal."""
    params = {
        "channel": NotificationChannel.EMAIL
    }
    response = client.get(
        "/stats/notifications",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert data["by_channel"][NotificationChannel.EMAIL] > 0

def test_get_stats_with_status_filter(client, test_token):
    """Teste la récupération des statistiques filtrées par statut."""
    params = {
        "status": NotificationStatus.SENT
    }
    response = client.get(
        "/stats/notifications",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert data["by_status"][NotificationStatus.SENT] > 0

def test_get_stats_with_priority_filter(client, test_token):
    """Teste la récupération des statistiques filtrées par priorité."""
    params = {
        "priority": NotificationPriority.HIGH
    }
    response = client.get(
        "/stats/notifications",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total" in data
    assert data["by_priority"][NotificationPriority.HIGH] > 0 