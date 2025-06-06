import pytest
from datetime import datetime
from app.schemas import (
    UserBase,
    UserCreate,
    UserLogin,
    UserUpdate,
    NotificationBase,
    NotificationCreate,
    NotificationUpdate,
    TemplateBase,
    TemplateCreate,
    TemplateUpdate,
    WebhookBase,
    WebhookCreate,
    WebhookUpdate,
    Token,
    TokenData
)

def test_user_base_schema():
    """Teste le schéma UserBase."""
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User"
    }
    user = UserBase(**user_data)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"

def test_user_create_schema():
    """Teste le schéma UserCreate."""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword",
        "full_name": "Test User"
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
    assert user.password == "testpassword"
    assert user.full_name == "Test User"

def test_user_login_schema():
    """Teste le schéma UserLogin."""
    login_data = {
        "username": "test@example.com",
        "password": "testpassword"
    }
    login = UserLogin(**login_data)
    assert login.username == "test@example.com"
    assert login.password == "testpassword"

def test_user_update_schema():
    """Teste le schéma UserUpdate."""
    update_data = {
        "email": "new@example.com",
        "full_name": "New User",
        "password": "newpassword"
    }
    update = UserUpdate(**update_data)
    assert update.email == "new@example.com"
    assert update.full_name == "New User"
    assert update.password == "newpassword"

def test_notification_base_schema():
    """Teste le schéma NotificationBase."""
    notification_data = {
        "title": "Test Notification",
        "content": "Test Content",
        "channel": "email",
        "priority": "normal"
    }
    notification = NotificationBase(**notification_data)
    assert notification.title == "Test Notification"
    assert notification.content == "Test Content"
    assert notification.channel == "email"
    assert notification.priority == "normal"

def test_notification_create_schema():
    """Teste le schéma NotificationCreate."""
    notification_data = {
        "title": "Test Notification",
        "content": "Test Content",
        "channel": "email",
        "priority": "normal",
        "recipient_id": 1,
        "template_id": 1
    }
    notification = NotificationCreate(**notification_data)
    assert notification.title == "Test Notification"
    assert notification.content == "Test Content"
    assert notification.channel == "email"
    assert notification.priority == "normal"
    assert notification.recipient_id == 1
    assert notification.template_id == 1

def test_notification_update_schema():
    """Teste le schéma NotificationUpdate."""
    update_data = {
        "title": "Updated Notification",
        "content": "Updated Content",
        "status": "sent"
    }
    update = NotificationUpdate(**update_data)
    assert update.title == "Updated Notification"
    assert update.content == "Updated Content"
    assert update.status == "sent"

def test_template_base_schema():
    """Teste le schéma TemplateBase."""
    template_data = {
        "name": "Test Template",
        "content": "Hello {{name}}!",
        "variables": ["name"]
    }
    template = TemplateBase(**template_data)
    assert template.name == "Test Template"
    assert template.content == "Hello {{name}}!"
    assert template.variables == ["name"]

def test_template_create_schema():
    """Teste le schéma TemplateCreate."""
    template_data = {
        "name": "Test Template",
        "content": "Hello {{name}}!",
        "variables": ["name"],
        "user_id": 1
    }
    template = TemplateCreate(**template_data)
    assert template.name == "Test Template"
    assert template.content == "Hello {{name}}!"
    assert template.variables == ["name"]
    assert template.user_id == 1

def test_template_update_schema():
    """Teste le schéma TemplateUpdate."""
    update_data = {
        "name": "Updated Template",
        "content": "Hello {{name}}! Welcome!",
        "variables": ["name", "welcome"]
    }
    update = TemplateUpdate(**update_data)
    assert update.name == "Updated Template"
    assert update.content == "Hello {{name}}! Welcome!"
    assert update.variables == ["name", "welcome"]

def test_webhook_base_schema():
    """Teste le schéma WebhookBase."""
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created"]
    }
    webhook = WebhookBase(**webhook_data)
    assert webhook.url == "https://example.com/webhook"
    assert webhook.events == ["notification.created"]

def test_webhook_create_schema():
    """Teste le schéma WebhookCreate."""
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created"],
        "user_id": 1
    }
    webhook = WebhookCreate(**webhook_data)
    assert webhook.url == "https://example.com/webhook"
    assert webhook.events == ["notification.created"]
    assert webhook.user_id == 1

def test_webhook_update_schema():
    """Teste le schéma WebhookUpdate."""
    update_data = {
        "url": "https://new-example.com/webhook",
        "events": ["notification.created", "notification.updated"],
        "is_active": False
    }
    update = WebhookUpdate(**update_data)
    assert update.url == "https://new-example.com/webhook"
    assert update.events == ["notification.created", "notification.updated"]
    assert update.is_active is False

def test_token_schema():
    """Teste le schéma Token."""
    token_data = {
        "access_token": "test_token",
        "token_type": "bearer"
    }
    token = Token(**token_data)
    assert token.access_token == "test_token"
    assert token.token_type == "bearer"

def test_token_data_schema():
    """Teste le schéma TokenData."""
    token_data = {
        "sub": "test@example.com",
        "exp": datetime.now()
    }
    token = TokenData(**token_data)
    assert token.sub == "test@example.com"
    assert isinstance(token.exp, datetime)

def test_schema_validation():
    """Teste la validation des schémas."""
    # Test de validation du schéma UserCreate
    with pytest.raises(ValueError):
        UserCreate(
            email="invalid_email",
            password="testpassword",
            full_name="Test User"
        )
    
    # Test de validation du schéma NotificationCreate
    with pytest.raises(ValueError):
        NotificationCreate(
            title="Test Notification",
            content="Test Content",
            channel="invalid_channel",
            priority="normal",
            recipient_id=1
        )
    
    # Test de validation du schéma TemplateCreate
    with pytest.raises(ValueError):
        TemplateCreate(
            name="Test Template",
            content="Hello {{name}}!",
            variables="invalid_variables",
            user_id=1
        )
    
    # Test de validation du schéma WebhookCreate
    with pytest.raises(ValueError):
        WebhookCreate(
            url="invalid_url",
            events="invalid_events",
            user_id=1
        )

def test_schema_optional_fields():
    """Teste les champs optionnels des schémas."""
    # Test des champs optionnels du schéma UserUpdate
    update_data = {"email": "new@example.com"}
    update = UserUpdate(**update_data)
    assert update.email == "new@example.com"
    assert update.full_name is None
    assert update.password is None
    
    # Test des champs optionnels du schéma NotificationUpdate
    update_data = {"status": "sent"}
    update = NotificationUpdate(**update_data)
    assert update.status == "sent"
    assert update.title is None
    assert update.content is None
    
    # Test des champs optionnels du schéma TemplateUpdate
    update_data = {"name": "Updated Template"}
    update = TemplateUpdate(**update_data)
    assert update.name == "Updated Template"
    assert update.content is None
    assert update.variables is None
    
    # Test des champs optionnels du schéma WebhookUpdate
    update_data = {"is_active": False}
    update = WebhookUpdate(**update_data)
    assert update.is_active is False
    assert update.url is None
    assert update.events is None

def test_schema_default_values():
    """Teste les valeurs par défaut des schémas."""
    # Test des valeurs par défaut du schéma NotificationBase
    notification_data = {
        "title": "Test Notification",
        "content": "Test Content"
    }
    notification = NotificationBase(**notification_data)
    assert notification.channel == "email"
    assert notification.priority == "normal"
    
    # Test des valeurs par défaut du schéma WebhookBase
    webhook_data = {
        "url": "https://example.com/webhook"
    }
    webhook = WebhookBase(**webhook_data)
    assert webhook.events == ["notification.created"]
    
    # Test des valeurs par défaut du schéma Token
    token_data = {
        "access_token": "test_token"
    }
    token = Token(**token_data)
    assert token.token_type == "bearer" 