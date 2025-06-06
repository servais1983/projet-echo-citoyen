"""Tests pour les routes de template."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session


def test_create_template_route(client, test_token):
    """Teste la création d'un template."""
    template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "content": "Hello {{name}}, this is a test notification.",
        "channel": "email"
    }
    response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == template_data["name"]
    assert data["subject"] == template_data["subject"]
    assert data["content"] == template_data["content"]
    assert data["channel"] == template_data["channel"]


def test_get_template_route(client, test_token, test_template):
    """Teste la récupération d'un template."""
    response = client.get(
        f"/templates/{test_template.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_template.id
    assert data["name"] == test_template.name
    assert data["subject"] == test_template.subject
    assert data["content"] == test_template.content
    assert data["channel"] == test_template.channel


def test_update_template_route(client, test_token, test_template):
    """Teste la mise à jour d'un template."""
    update_data = {
        "name": "Updated Template",
        "subject": "Updated Subject",
        "content": "Updated content for {{name}}."
    }
    response = client.put(
        f"/templates/{test_template.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["subject"] == update_data["subject"]
    assert data["content"] == update_data["content"]


def test_delete_template_route(client, test_token, test_template):
    """Teste la suppression d'un template."""
    response = client.delete(
        f"/templates/{test_template.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(
        f"/templates/{test_template.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_templates_route(client, test_token, test_template):
    """Teste la liste des templates."""
    response = client.get(
        "/templates/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(t["id"] == test_template.id for t in data)


def test_filter_templates_route(client, test_token, test_template):
    """Teste le filtrage des templates."""
    response = client.get(
        "/templates/?channel=email",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(t["channel"] == "email" for t in data)


def test_create_template_invalid_data(client, test_token):
    """Teste la création d'un template avec des données invalides."""
    template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "content": "Invalid content",
        "channel": "invalid_channel"
    }
    response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_template(client, test_token):
    """Teste la récupération d'un template inexistant."""
    response = client.get(
        "/templates/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_template(client, test_token):
    """Teste la mise à jour d'un template inexistant."""
    update_data = {
        "name": "Updated Template",
        "subject": "Updated Subject",
        "content": "Updated content."
    }
    response = client.put(
        "/templates/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_template(client, test_token):
    """Teste la suppression d'un template inexistant."""
    response = client.delete(
        "/templates/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_preview_template_route(client, test_token, test_template):
    """Teste l'aperçu d'un template."""
    preview_data = {
        "name": "John Doe",
        "company": "Example Corp"
    }
    response = client.post(
        f"/templates/{test_template.id}/preview",
        json=preview_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "subject" in data
    assert "content" in data
    assert "John Doe" in data["content"]
    assert "Example Corp" in data["content"] 