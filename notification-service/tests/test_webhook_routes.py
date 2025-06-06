"""Tests pour les routes de webhook."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session


def test_create_webhook_route(client, test_token):
    """Teste la création d'un webhook."""
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created", "notification.updated"],
        "secret": "test_secret"
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
    assert "secret" not in data


def test_get_webhook_route(client, test_token, test_webhook):
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
    assert "secret" not in data


def test_update_webhook_route(client, test_token, test_webhook):
    """Teste la mise à jour d'un webhook."""
    update_data = {
        "url": "https://example.com/updated-webhook",
        "events": ["notification.created", "notification.deleted"]
    }
    response = client.put(
        f"/webhooks/{test_webhook.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["url"] == update_data["url"]
    assert data["events"] == update_data["events"]


def test_delete_webhook_route(client, test_token, test_webhook):
    """Teste la suppression d'un webhook."""
    response = client.delete(
        f"/webhooks/{test_webhook.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(
        f"/webhooks/{test_webhook.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_webhooks_route(client, test_token, test_webhook):
    """Teste la liste des webhooks."""
    response = client.get(
        "/webhooks/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(w["id"] == test_webhook.id for w in data)


def test_filter_webhooks_route(client, test_token, test_webhook):
    """Teste le filtrage des webhooks."""
    response = client.get(
        "/webhooks/?event=notification.created",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all("notification.created" in w["events"] for w in data)


def test_create_webhook_invalid_data(client, test_token):
    """Teste la création d'un webhook avec des données invalides."""
    webhook_data = {
        "url": "invalid_url",
        "events": ["invalid_event"],
        "secret": "test_secret"
    }
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_webhook(client, test_token):
    """Teste la récupération d'un webhook inexistant."""
    response = client.get(
        "/webhooks/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_webhook(client, test_token):
    """Teste la mise à jour d'un webhook inexistant."""
    update_data = {
        "url": "https://example.com/updated-webhook",
        "events": ["notification.created"]
    }
    response = client.put(
        "/webhooks/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_webhook(client, test_token):
    """Teste la suppression d'un webhook inexistant."""
    response = client.delete(
        "/webhooks/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_webhook_delivery_route(client, test_webhook):
    """Teste la livraison d'un webhook."""
    event_data = {
        "event": "notification.created",
        "data": {
            "id": 1,
            "channel": "email",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "content": "Test Content"
        }
    }
    response = client.post(
        f"/webhooks/{test_webhook.id}/deliver",
        json=event_data,
        headers={"X-Webhook-Signature": "test_signature"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["message"] == "Webhook delivered successfully"


def test_webhook_delivery_invalid_signature(client, test_webhook):
    """Teste la livraison d'un webhook avec une signature invalide."""
    event_data = {
        "event": "notification.created",
        "data": {
            "id": 1,
            "channel": "email",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "content": "Test Content"
        }
    }
    response = client.post(
        f"/webhooks/{test_webhook.id}/deliver",
        json=event_data,
        headers={"X-Webhook-Signature": "invalid_signature"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_unauthorized_access(client):
    """Teste l'accès non autorisé aux webhooks."""
    # Test sans token
    response = client.get("/webhooks/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test avec token invalide
    response = client.get(
        "/webhooks/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test création sans token
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created"],
        "secret": "test_secret"
    }
    response = client.post("/webhooks/", json=webhook_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_webhook_event_validation(client, test_token):
    """Teste la validation des événements de webhook."""
    # Test avec événement invalide
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["invalid.event"],
        "secret": "test_secret"
    }
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test avec liste d'événements vide
    webhook_data["events"] = []
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_webhook_url_validation(client, test_token):
    """Teste la validation de l'URL du webhook."""
    # Test avec URL invalide
    webhook_data = {
        "url": "not_a_url",
        "events": ["notification.created"],
        "secret": "test_secret"
    }
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test avec URL non HTTPS
    webhook_data["url"] = "http://example.com/webhook"
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Test avec URL sans protocole
    webhook_data["url"] = "example.com/webhook"
    response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY 