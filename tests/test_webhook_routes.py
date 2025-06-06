import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_webhook(client, test_token):
    """Teste la création d'un webhook."""
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created", "notification.sent"],
        "description": "Test webhook"
    }
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["url"] == webhook_data["url"]
    assert data["events"] == webhook_data["events"]
    assert data["description"] == webhook_data["description"]
    assert data["is_active"] is True

def test_get_webhook(client, test_token, test_webhook):
    """Teste la récupération d'un webhook."""
    response = client.get(
        f"/webhooks/{test_webhook.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_webhook.id
    assert data["url"] == test_webhook.url
    assert data["events"] == test_webhook.events

def test_update_webhook(client, test_token, test_webhook):
    update_data = {
        "url": "https://example.com/webhook/updated",
        "events": ["notification.delivered"],
        "description": "Updated webhook"
    }
    response = client.patch(
        f"/webhooks/{test_webhook.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url"] == update_data["url"]
    assert data["events"] == update_data["events"]
    assert data["description"] == update_data["description"]

def test_delete_webhook(client, test_token, test_webhook):
    """Teste la suppression d'un webhook."""
    response = client.delete(
        f"/webhooks/{test_webhook.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_list_webhooks(client, test_token):
    response = client.get(
        "/webhooks/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_filter_webhooks(client, test_token):
    params = {
        "is_active": True,
        "event": "notification.created"
    }
    response = client.get(
        "/webhooks/",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for webhook in data:
        assert webhook["is_active"] is True
        assert "notification.created" in webhook["events"]

def test_invalid_url(client, test_token):
    """Teste la création d'un webhook avec des données invalides."""
    webhook_data = {
        "url": "invalid_url",
        "events": ["notification.created"],
        "description": "Test webhook"
    }
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_events(client, test_token):
    """Teste la création d'un webhook avec des événements invalides."""
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["invalid_event"],
        "description": "Test webhook"
    }
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_webhook_delivery(client, test_token, test_webhook):
    """Teste la livraison d'un événement webhook."""
    response = client.post(
        f"/webhooks/{test_webhook.id}/test",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True

def test_webhook_stats(client, test_token, test_webhook):
    """Teste les statistiques d'un webhook."""
    response = client.get(
        f"/webhooks/{test_webhook.id}/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_deliveries" in data
    assert "success_rate" in data
    assert "last_delivery" in data 