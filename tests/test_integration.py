import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.models import NotificationChannel, NotificationPriority, NotificationStatus

def test_notification_workflow(client, test_token, test_user):
    """Teste le flux complet de création et d'envoi d'une notification."""
    # Création d'un template
    template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "content": "Test Content",
        "channel": NotificationChannel.EMAIL,
        "description": "Test template description"
    }
    template_response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert template_response.status_code == status.HTTP_201_CREATED
    template_id = template_response.json()["id"]

    # Création d'une notification avec le template
    notification_data = {
        "title": "Test Notification",
        "content": "This is a test notification",
        "channel": NotificationChannel.EMAIL,
        "priority": NotificationPriority.MEDIUM,
        "recipient_id": test_user.id,
        "template_id": template_id
    }
    notification_response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert notification_response.status_code == status.HTTP_201_CREATED
    notification_id = notification_response.json()["id"]

    # Vérification de la notification
    get_notification_response = client.get(
        f"/notifications/{notification_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert get_notification_response.status_code == status.HTTP_200_OK
    notification = get_notification_response.json()
    assert notification["status"] == NotificationStatus.PENDING

    # Mise à jour de la notification
    update_data = {
        "priority": NotificationPriority.HIGH
    }
    update_response = client.patch(
        f"/notifications/{notification_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert update_response.status_code == status.HTTP_200_OK
    assert update_response.json()["priority"] == NotificationPriority.HIGH

    # Vérification des statistiques
    stats_response = client.get(
        "/stats/notifications",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert stats_response.status_code == status.HTTP_200_OK
    stats = stats_response.json()
    assert stats["total"] > 0
    assert stats["by_channel"][NotificationChannel.EMAIL] > 0

def test_webhook_notification_workflow(client, test_token, test_user):
    """Teste le flux complet de création d'un webhook et d'envoi d'une notification."""
    # Création d'un webhook
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created", "notification.sent"],
        "description": "Test webhook"
    }
    webhook_response = client.post(
        "/webhooks/",
        json=webhook_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert webhook_response.status_code == status.HTTP_201_CREATED
    webhook_id = webhook_response.json()["id"]

    # Création d'une notification
    notification_data = {
        "title": "Test Notification",
        "content": "This is a test notification",
        "channel": NotificationChannel.EMAIL,
        "priority": NotificationPriority.MEDIUM,
        "recipient_id": test_user.id
    }
    notification_response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert notification_response.status_code == status.HTTP_201_CREATED
    notification_id = notification_response.json()["id"]

    # Vérification des statistiques du webhook
    webhook_stats_response = client.get(
        f"/webhooks/{webhook_id}/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert webhook_stats_response.status_code == status.HTTP_200_OK
    webhook_stats = webhook_stats_response.json()
    assert "total_deliveries" in webhook_stats
    assert "success_rate" in webhook_stats

def test_user_notification_workflow(client, test_token, test_user):
    """Teste le flux complet de création d'un utilisateur et d'envoi de notifications."""
    # Création d'un nouvel utilisateur
    new_user_data = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "testpassword123"
    }
    new_user_response = client.post(
        "/users/",
        json=new_user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert new_user_response.status_code == status.HTTP_201_CREATED
    new_user_id = new_user_response.json()["id"]

    # Création de plusieurs notifications pour le nouvel utilisateur
    notifications_data = [
        {
            "title": f"Test Notification {i}",
            "content": f"This is test notification {i}",
            "channel": NotificationChannel.EMAIL,
            "priority": NotificationPriority.MEDIUM,
            "recipient_id": new_user_id
        }
        for i in range(3)
    ]
    batch_response = client.post(
        "/notifications/batch",
        json=notifications_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert batch_response.status_code == status.HTTP_201_CREATED
    notifications = batch_response.json()
    assert len(notifications) == 3

    # Vérification des statistiques de l'utilisateur
    user_stats_response = client.get(
        f"/users/{new_user_id}/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert user_stats_response.status_code == status.HTTP_200_OK
    user_stats = user_stats_response.json()
    assert "total_notifications" in user_stats
    assert user_stats["total_notifications"] >= 3

def test_template_notification_workflow(client, test_token, test_user):
    """Teste le flux complet de création d'un template et d'envoi de notifications."""
    # Création d'un template
    template_data = {
        "name": "Test Template",
        "subject": "Test Subject",
        "content": "Test Content",
        "channel": NotificationChannel.EMAIL,
        "description": "Test template description"
    }
    template_response = client.post(
        "/templates/",
        json=template_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert template_response.status_code == status.HTTP_201_CREATED
    template_id = template_response.json()["id"]

    # Création de plusieurs notifications avec le template
    notifications_data = [
        {
            "title": f"Test Notification {i}",
            "content": f"This is test notification {i}",
            "channel": NotificationChannel.EMAIL,
            "priority": NotificationPriority.MEDIUM,
            "recipient_id": test_user.id,
            "template_id": template_id
        }
        for i in range(3)
    ]
    batch_response = client.post(
        "/notifications/batch",
        json=notifications_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert batch_response.status_code == status.HTTP_201_CREATED
    notifications = batch_response.json()
    assert len(notifications) == 3

    # Vérification des statistiques du template
    template_usage_response = client.get(
        f"/templates/{template_id}/usage",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert template_usage_response.status_code == status.HTTP_200_OK
    template_usage = template_usage_response.json()
    assert template_usage["total_uses"] >= 3 