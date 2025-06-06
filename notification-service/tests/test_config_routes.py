"""Tests pour les routes de configuration."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session


def test_get_config_route(client, test_token):
    """Teste la récupération de la configuration."""
    response = client.get(
        "/config",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "sms" in data
    assert "push" in data


def test_update_config_route(client, test_token):
    """Teste la mise à jour de la configuration."""
    config_data = {
        "email": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "testpassword",
            "from_email": "noreply@example.com"
        },
        "sms": {
            "provider": "twilio",
            "account_sid": "test_sid",
            "auth_token": "test_token",
            "from_number": "+1234567890"
        },
        "push": {
            "provider": "firebase",
            "api_key": "test_api_key",
            "project_id": "test_project"
        }
    }
    response = client.put(
        "/config",
        json=config_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == config_data["email"]
    assert data["sms"] == config_data["sms"]
    assert data["push"] == config_data["push"]


def test_get_config_without_auth(client):
    """Teste la récupération de la configuration sans authentification."""
    response = client.get("/config")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_config_without_auth(client):
    """Teste la mise à jour de la configuration sans authentification."""
    config_data = {
        "email": {
            "smtp_server": "smtp.example.com",
            "smtp_port": 587,
            "smtp_username": "test@example.com",
            "smtp_password": "testpassword",
            "from_email": "noreply@example.com"
        }
    }
    response = client.put("/config", json=config_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_update_config_invalid_data(client, test_token):
    """Teste la mise à jour de la configuration avec des données invalides."""
    config_data = {
        "email": {
            "smtp_server": "invalid",
            "smtp_port": "invalid",
            "smtp_username": "invalid",
            "smtp_password": "invalid",
            "from_email": "invalid"
        }
    }
    response = client.put(
        "/config",
        json=config_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_email_config_route(client, test_token):
    """Teste la récupération de la configuration email."""
    response = client.get(
        "/config/email",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "smtp_server" in data
    assert "smtp_port" in data
    assert "smtp_username" in data
    assert "from_email" in data


def test_get_sms_config_route(client, test_token):
    """Teste la récupération de la configuration SMS."""
    response = client.get(
        "/config/sms",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "provider" in data
    assert "account_sid" in data
    assert "from_number" in data


def test_get_push_config_route(client, test_token):
    """Teste la récupération de la configuration push."""
    response = client.get(
        "/config/push",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "provider" in data
    assert "api_key" in data
    assert "project_id" in data


def test_update_email_config_route(client, test_token):
    """Teste la mise à jour de la configuration email."""
    email_config = {
        "smtp_server": "smtp.example.com",
        "smtp_port": 587,
        "smtp_username": "test@example.com",
        "smtp_password": "testpassword",
        "from_email": "noreply@example.com"
    }
    response = client.put(
        "/config/email",
        json=email_config,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == email_config


def test_update_sms_config_route(client, test_token):
    """Teste la mise à jour de la configuration SMS."""
    sms_config = {
        "provider": "twilio",
        "account_sid": "test_sid",
        "auth_token": "test_token",
        "from_number": "+1234567890"
    }
    response = client.put(
        "/config/sms",
        json=sms_config,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == sms_config


def test_update_push_config_route(client, test_token):
    """Teste la mise à jour de la configuration push."""
    push_config = {
        "provider": "firebase",
        "api_key": "test_api_key",
        "project_id": "test_project"
    }
    response = client.put(
        "/config/push",
        json=push_config,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == push_config 