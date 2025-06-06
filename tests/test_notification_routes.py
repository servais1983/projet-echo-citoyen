import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import NotificationChannel, NotificationPriority, NotificationStatus

def test_create_notification(client, test_token):
    notification_data = {
        "channel": NotificationChannel.EMAIL,
        "recipient": "test@example.com",
        "subject": "Test Notification",
        "content": "This is a test notification",
        "priority": NotificationPriority.MEDIUM
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
    assert data["status"] == NotificationStatus.PENDING

def test_get_notification(client, test_token, test_notification):
    response = client.get(
        f"/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_notification.id
    assert data["channel"] == test_notification.channel
    assert data["recipient"] == test_notification.recipient

def test_update_notification(client, test_token, test_notification):
    update_data = {
        "subject": "Updated Subject",
        "content": "Updated content",
        "priority": NotificationPriority.HIGH
    }
    
    response = client.patch(
        f"/notifications/{test_notification.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["subject"] == update_data["subject"]
    assert data["content"] == update_data["content"]
    assert data["priority"] == update_data["priority"]

def test_delete_notification(client, test_token, test_notification):
    response = client.delete(
        f"/notifications/{test_notification.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_list_notifications(client, test_token):
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_filter_notifications(client, test_token):
    params = {
        "channel": NotificationChannel.EMAIL,
        "priority": NotificationPriority.HIGH,
        "status": NotificationStatus.PENDING
    }
    
    response = client.get(
        "/notifications/",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for notification in data:
        assert notification["channel"] == params["channel"]
        assert notification["priority"] == params["priority"]
        assert notification["status"] == params["status"]

def test_invalid_channel(client, test_token):
    notification_data = {
        "channel": "invalid_channel",
        "recipient": "test@example.com",
        "subject": "Test Notification",
        "content": "This is a test notification"
    }
    
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_priority(client, test_token):
    notification_data = {
        "channel": NotificationChannel.EMAIL,
        "recipient": "test@example.com",
        "subject": "Test Notification",
        "content": "This is a test notification",
        "priority": "invalid_priority"
    }
    
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_send_notification(client, test_token, test_notification):
    response = client.post(
        f"/notifications/{test_notification.id}/send",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == NotificationStatus.SENT

def test_batch_create(client, test_token):
    notifications_data = [
        {
            "channel": NotificationChannel.EMAIL,
            "recipient": "test1@example.com",
            "subject": "Test 1",
            "content": "Content 1"
        },
        {
            "channel": NotificationChannel.SMS,
            "recipient": "+1234567890",
            "subject": "Test 2",
            "content": "Content 2"
        }
    ]
    
    response = client.post(
        "/notifications/batch",
        json=notifications_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 2
    assert all(n["status"] == NotificationStatus.PENDING for n in data)

def test_batch_update(client, test_token, test_notification):
    update_data = [
        {
            "id": test_notification.id,
            "subject": "Updated Subject",
            "priority": NotificationPriority.HIGH
        }
    ]
    
    response = client.patch(
        "/notifications/batch",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["subject"] == "Updated Subject"
    assert data[0]["priority"] == NotificationPriority.HIGH

def test_batch_delete(client, test_token, test_notification):
    response = client.delete(
        "/notifications/batch",
        json=[test_notification.id],
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_create_notification_invalid_data(client, test_token):
    """Teste la création d'une notification avec des données invalides."""
    notification_data = {
        "channel": "invalid_channel",
        "recipient": "invalid_email",
        "subject": "",
        "content": "",
        "priority": "invalid_priority"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

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