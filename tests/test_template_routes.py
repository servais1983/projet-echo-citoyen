import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import NotificationChannel

def test_create_template(client, test_token):
    template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "content": "Test Content",
        "channel": NotificationChannel.EMAIL,
        "description": "Test template description"
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
    assert data["description"] == template_data["description"]

def test_get_template(client, test_token, test_template):
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

def test_update_template(client, test_token, test_template):
    update_data = {
        "name": "Updated Template",
        "subject": "Updated Subject",
        "content": "Updated Content",
        "description": "Updated description"
    }
    
    response = client.patch(
        f"/templates/{test_template.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["subject"] == update_data["subject"]
    assert data["content"] == update_data["content"]
    assert data["description"] == update_data["description"]

def test_delete_template(client, test_token, test_template):
    response = client.delete(
        f"/templates/{test_template.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_list_templates(client, test_token):
    response = client.get(
        "/templates/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_filter_templates(client, test_token):
    params = {
        "channel": NotificationChannel.EMAIL,
        "search": "Test"
    }
    
    response = client.get(
        "/templates/",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for template in data:
        assert template["channel"] == NotificationChannel.EMAIL
        assert "Test" in template["name"] or "Test" in template["subject"]

def test_invalid_channel(client, test_token):
    template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "content": "Test Content",
        "channel": "invalid_channel",
        "description": "Test template description"
    }
    
    response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_template_validation(client, test_token):
    template_data = {
        "name": "",
        "subject": "",
        "content": "",
        "channel": NotificationChannel.EMAIL
    }
    
    response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_template_duplicate_name(client, test_token, test_template):
    template_data = {
        "name": test_template.name,
        "subject": "Test Subject",
        "content": "Test Content",
        "channel": NotificationChannel.EMAIL
    }
    
    response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_template_usage(client, test_token, test_template):
    response = client.get(
        f"/templates/{test_template.id}/usage",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_uses" in data
    assert "last_used" in data
    assert "success_rate" in data 