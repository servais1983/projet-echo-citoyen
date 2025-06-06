"""Tests pour les routes de l'API."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import Notification, User


def test_root_endpoint(client):
    """Teste le endpoint racine."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert data["message"] == "Bienvenue sur l'API de notifications"


def test_health_check(client):
    """Teste le endpoint de vérification de santé."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_protected_route_without_token(client):
    """Teste l'accès à une route protégée sans token."""
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_route_with_invalid_token(client):
    """Teste l'accès à une route protégée avec un token invalide."""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_protected_route_with_valid_token(client, test_user, test_token):
    """Teste l'accès à une route protégée avec un token valide."""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email


def test_notification_creation_with_invalid_data(client, test_token):
    """Teste la création d'une notification avec des données invalides."""
    response = client.post(
        "/notifications/",
        json={
            "channel": "invalid_channel",
            "recipient": "invalid_email",
            "priority": "invalid_priority"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_notification_update_with_invalid_id(client, test_token):
    """Teste la mise à jour d'une notification avec un ID invalide."""
    response = client.put(
        "/notifications/999999",
        json={
            "subject": "Updated Subject",
            "content": "Updated Content"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_notification_deletion_with_invalid_id(client, test_token):
    """Teste la suppression d'une notification avec un ID invalide."""
    response = client.delete(
        "/notifications/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND 