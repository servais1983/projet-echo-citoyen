def test_email_service_success(client, test_token):
    """Teste l'envoi d'un email avec succès."""
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

def test_email_service_failure(client, test_token):
    """Teste l'échec de l'envoi d'un email."""
    notification_data = {
        "channel": "email",
        "recipient": "invalid-email",
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

def test_slack_service_success(client, test_token):
    """Teste l'envoi d'un message Slack avec succès."""
    notification_data = {
        "channel": "slack",
        "recipient": "#test-channel",
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
    assert data["channel"] == "slack"
    assert data["recipient"] == "#test-channel"
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Test Content"
    assert data["priority"] == "high"

def test_slack_service_failure(client, test_token):
    """Teste l'échec de l'envoi d'un message Slack."""
    notification_data = {
        "channel": "slack",
        "recipient": "invalid-channel",
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

def test_sms_service_success(client, test_token):
    """Teste l'envoi d'un SMS avec succès."""
    notification_data = {
        "channel": "sms",
        "recipient": "+1234567890",
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
    assert data["channel"] == "sms"
    assert data["recipient"] == "+1234567890"
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Test Content"
    assert data["priority"] == "high"

def test_sms_service_failure(client, test_token):
    """Teste l'échec de l'envoi d'un SMS."""
    notification_data = {
        "channel": "sms",
        "recipient": "invalid-number",
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

def test_rate_limiting(client, test_token):
    """Teste la limitation de débit."""
    for _ in range(10):
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
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS

def test_retry_mechanism(client, test_token):
    """Teste le mécanisme de nouvelle tentative."""
    notification_data = {
        "channel": "email",
        "recipient": "test@example.com",
        "subject": "Test Subject",
        "content": "Test Content",
        "priority": "high",
        "retry_count": 3
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["retry_count"] == 3 