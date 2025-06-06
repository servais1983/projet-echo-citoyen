def test_create_notification(client, test_token):
    """Teste la création d'une notification."""
    notification_data = {
        "channel": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "high"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["channel"] == "email"
    assert data["recipient"] == "test@example.com"
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Test Content"
    assert data["priority"] == "high"
    return data["id"]

def test_get_notification(client, test_token, notification_id):
    """Teste la récupération d'une notification."""
    response = client.get(
        f"/notifications/{notification_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == notification_id
    assert data["channel"] == "email"
    assert data["recipient"] == "test@example.com"
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Test Content"
    assert data["priority"] == "high"

def test_update_notification(client, test_token, notification_id):
    """Teste la mise à jour d'une notification."""
    update_data = {
        "subject": "Updated Subject",
        "content": "Updated Content"
    }
    response = client.patch(
        f"/notifications/{notification_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == notification_id
    assert data["subject"] == "Updated Subject"
    assert data["content"] == "Updated Content"

def test_delete_notification(client, test_token, notification_id):
    """Teste la suppression d'une notification."""
    response = client.delete(
        f"/notifications/{notification_id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_list_notifications(client, test_token):
    """Teste la liste des notifications."""
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_filter_notifications(client, test_token):
    """Teste le filtrage des notifications."""
    response = client.get(
        "/notifications/?channel=email&priority=high",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for notification in data:
        assert notification["channel"] == "email"
        assert notification["priority"] == "high"

def test_invalid_channel(client, test_token):
    """Teste la validation d'un canal invalide."""
    notification_data = {
        "channel": "invalid",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "high"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_priority(client, test_token):
    """Teste la validation d'une priorité invalide."""
    notification_data = {
        "channel": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "invalid"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_send_notification(client, test_token):
    """Teste l'envoi d'une notification."""
    notification_data = {
        "channel": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "high"
    }
    response = client.post(
        "/notifications/send",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "sent"

def test_batch_send(client, test_token):
    """Teste l'envoi en lot de notifications."""
    notifications = [
        {
            "channel": "email",
            "recipient": "test1@example.com",
            "subject": "Test Subject 1",
            "content": "Test Content 1",
            "priority": "high"
        },
        {
            "channel": "email",
            "recipient": "test2@example.com",
            "subject": "Test Subject 2",
            "content": "Test Content 2",
            "priority": "high"
        }
    ]
    response = client.post(
        "/notifications/batch/send",
        json={"notifications": notifications},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 2
    for notification in data:
        assert notification["status"] == "sent"

def test_batch_create(client, test_token):
    """Teste la création en lot de notifications."""
    notifications = [
        {
            "channel": "email",
            "recipient": "test1@example.com",
            "subject": "Test Subject 1",
            "content": "Test Content 1",
            "priority": "high"
        },
        {
            "channel": "email",
            "recipient": "test2@example.com",
            "subject": "Test Subject 2",
            "content": "Test Content 2",
            "priority": "high"
        }
    ]
    response = client.post(
        "/notifications/batch",
        json={"notifications": notifications},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data) == 2

def test_batch_update(client, test_token):
    """Teste la mise à jour en lot de notifications."""
    notifications = [
        {
            "id": 1,
            "subject": "Updated Subject 1",
            "content": "Updated Content 1"
        },
        {
            "id": 2,
            "subject": "Updated Subject 2",
            "content": "Updated Content 2"
        }
    ]
    response = client.patch(
        "/notifications/batch",
        json={"notifications": notifications},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2

def test_batch_delete(client, test_token):
    """Teste la suppression en lot de notifications."""
    notification_ids = [1, 2]
    response = client.delete(
        "/notifications/batch",
        json={"notification_ids": notification_ids},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT 