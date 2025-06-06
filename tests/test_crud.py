import pytest
from datetime import datetime
from app.crud import (
    get_user,
    get_user_by_email,
    create_user,
    update_user,
    delete_user,
    get_notification,
    get_notifications,
    create_notification,
    update_notification,
    delete_notification,
    get_template,
    get_templates,
    create_template,
    update_template,
    delete_template,
    get_webhook,
    get_webhooks,
    create_webhook,
    update_webhook,
    delete_webhook
)
from app.models import (
    User,
    Notification,
    Template,
    Webhook,
    NotificationChannel,
    NotificationStatus,
    NotificationPriority
)

def test_user_crud_operations(db):
    """Teste les opérations CRUD pour les utilisateurs."""
    # Test de création d'utilisateur
    user_data = {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User",
        "is_active": True,
        "is_superuser": False
    }
    user = create_user(db, user_data)
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_superuser is False
    
    # Test de récupération d'utilisateur par ID
    retrieved_user = get_user(db, user.id)
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email
    
    # Test de récupération d'utilisateur par email
    retrieved_user = get_user_by_email(db, user.email)
    assert retrieved_user.id == user.id
    assert retrieved_user.email == user.email
    
    # Test de mise à jour d'utilisateur
    update_data = {
        "full_name": "Updated User",
        "is_active": False
    }
    updated_user = update_user(db, user.id, update_data)
    assert updated_user.full_name == "Updated User"
    assert updated_user.is_active is False
    
    # Test de suppression d'utilisateur
    delete_user(db, user.id)
    deleted_user = get_user(db, user.id)
    assert deleted_user is None

def test_notification_crud_operations(db):
    """Teste les opérations CRUD pour les notifications."""
    # Création d'un utilisateur pour les tests
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Test de création de notification
    notification_data = {
        "title": "Test Notification",
        "content": "Test Content",
        "channel": NotificationChannel.EMAIL,
        "status": NotificationStatus.PENDING,
        "priority": NotificationPriority.NORMAL,
        "recipient_id": user.id
    }
    notification = create_notification(db, notification_data)
    assert notification.title == "Test Notification"
    assert notification.content == "Test Content"
    assert notification.channel == NotificationChannel.EMAIL
    assert notification.status == NotificationStatus.PENDING
    assert notification.priority == NotificationPriority.NORMAL
    assert notification.recipient_id == user.id
    
    # Test de récupération de notification
    retrieved_notification = get_notification(db, notification.id)
    assert retrieved_notification.id == notification.id
    assert retrieved_notification.title == notification.title
    
    # Test de récupération des notifications
    notifications = get_notifications(db, skip=0, limit=10)
    assert len(notifications) > 0
    assert notifications[0].id == notification.id
    
    # Test de mise à jour de notification
    update_data = {
        "title": "Updated Notification",
        "status": NotificationStatus.SENT
    }
    updated_notification = update_notification(db, notification.id, update_data)
    assert updated_notification.title == "Updated Notification"
    assert updated_notification.status == NotificationStatus.SENT
    
    # Test de suppression de notification
    delete_notification(db, notification.id)
    deleted_notification = get_notification(db, notification.id)
    assert deleted_notification is None

def test_template_crud_operations(db):
    """Teste les opérations CRUD pour les templates."""
    # Création d'un utilisateur pour les tests
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Test de création de template
    template_data = {
        "name": "Test Template",
        "content": "Hello {{name}}!",
        "variables": ["name"],
        "user_id": user.id
    }
    template = create_template(db, template_data)
    assert template.name == "Test Template"
    assert template.content == "Hello {{name}}!"
    assert template.variables == ["name"]
    assert template.user_id == user.id
    
    # Test de récupération de template
    retrieved_template = get_template(db, template.id)
    assert retrieved_template.id == template.id
    assert retrieved_template.name == template.name
    
    # Test de récupération des templates
    templates = get_templates(db, skip=0, limit=10)
    assert len(templates) > 0
    assert templates[0].id == template.id
    
    # Test de mise à jour de template
    update_data = {
        "name": "Updated Template",
        "content": "Hello {{name}}! Welcome!"
    }
    updated_template = update_template(db, template.id, update_data)
    assert updated_template.name == "Updated Template"
    assert updated_template.content == "Hello {{name}}! Welcome!"
    
    # Test de suppression de template
    delete_template(db, template.id)
    deleted_template = get_template(db, template.id)
    assert deleted_template is None

def test_webhook_crud_operations(db):
    """Teste les opérations CRUD pour les webhooks."""
    # Création d'un utilisateur pour les tests
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Test de création de webhook
    webhook_data = {
        "url": "https://example.com/webhook",
        "events": ["notification.created"],
        "user_id": user.id,
        "is_active": True
    }
    webhook = create_webhook(db, webhook_data)
    assert webhook.url == "https://example.com/webhook"
    assert webhook.events == ["notification.created"]
    assert webhook.user_id == user.id
    assert webhook.is_active is True
    
    # Test de récupération de webhook
    retrieved_webhook = get_webhook(db, webhook.id)
    assert retrieved_webhook.id == webhook.id
    assert retrieved_webhook.url == webhook.url
    
    # Test de récupération des webhooks
    webhooks = get_webhooks(db, skip=0, limit=10)
    assert len(webhooks) > 0
    assert webhooks[0].id == webhook.id
    
    # Test de mise à jour de webhook
    update_data = {
        "url": "https://new-example.com/webhook",
        "is_active": False
    }
    updated_webhook = update_webhook(db, webhook.id, update_data)
    assert updated_webhook.url == "https://new-example.com/webhook"
    assert updated_webhook.is_active is False
    
    # Test de suppression de webhook
    delete_webhook(db, webhook.id)
    deleted_webhook = get_webhook(db, webhook.id)
    assert deleted_webhook is None

def test_crud_relationships(db):
    """Teste les relations entre les modèles dans les opérations CRUD."""
    # Création d'un utilisateur
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Création d'un template
    template = create_template(db, {
        "name": "Test Template",
        "content": "Hello {{name}}!",
        "variables": ["name"],
        "user_id": user.id
    })
    
    # Création d'une notification avec le template
    notification = create_notification(db, {
        "title": "Test Notification",
        "content": "Test Content",
        "channel": NotificationChannel.EMAIL,
        "recipient_id": user.id,
        "template_id": template.id
    })
    
    # Vérification des relations
    retrieved_notification = get_notification(db, notification.id)
    assert retrieved_notification.recipient_id == user.id
    assert retrieved_notification.template_id == template.id
    
    # Création d'un webhook
    webhook = create_webhook(db, {
        "url": "https://example.com/webhook",
        "events": ["notification.created"],
        "user_id": user.id
    })
    
    # Vérification des relations
    retrieved_webhook = get_webhook(db, webhook.id)
    assert retrieved_webhook.user_id == user.id

def test_crud_filters(db):
    """Teste les filtres dans les opérations CRUD."""
    # Création d'un utilisateur
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Création de notifications avec différents statuts
    for status in [NotificationStatus.PENDING, NotificationStatus.SENT, NotificationStatus.FAILED]:
        create_notification(db, {
            "title": f"Test Notification {status}",
            "content": "Test Content",
            "channel": NotificationChannel.EMAIL,
            "status": status,
            "recipient_id": user.id
        })
    
    # Test du filtre par statut
    pending_notifications = get_notifications(db, status=NotificationStatus.PENDING)
    assert all(n.status == NotificationStatus.PENDING for n in pending_notifications)
    
    sent_notifications = get_notifications(db, status=NotificationStatus.SENT)
    assert all(n.status == NotificationStatus.SENT for n in sent_notifications)
    
    # Création de templates avec différents noms
    for name in ["Template 1", "Template 2", "Template 3"]:
        create_template(db, {
            "name": name,
            "content": "Test Content",
            "user_id": user.id
        })
    
    # Test du filtre par nom de template
    templates = get_templates(db, name="Template 1")
    assert all(t.name == "Template 1" for t in templates)
    
    # Création de webhooks avec différents états
    for is_active in [True, False]:
        create_webhook(db, {
            "url": f"https://example.com/webhook-{is_active}",
            "events": ["notification.created"],
            "user_id": user.id,
            "is_active": is_active
        })
    
    # Test du filtre par état de webhook
    active_webhooks = get_webhooks(db, is_active=True)
    assert all(w.is_active is True for w in active_webhooks)
    
    inactive_webhooks = get_webhooks(db, is_active=False)
    assert all(w.is_active is False for w in inactive_webhooks)

def test_crud_pagination(db):
    """Teste la pagination dans les opérations CRUD."""
    # Création d'un utilisateur
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Création de 50 notifications
    for i in range(50):
        create_notification(db, {
            "title": f"Test Notification {i}",
            "content": "Test Content",
            "channel": NotificationChannel.EMAIL,
            "recipient_id": user.id
        })
    
    # Test de la pagination
    page1 = get_notifications(db, skip=0, limit=10)
    assert len(page1) == 10
    
    page2 = get_notifications(db, skip=10, limit=10)
    assert len(page2) == 10
    
    page3 = get_notifications(db, skip=20, limit=10)
    assert len(page3) == 10
    
    # Vérification que les pages sont différentes
    assert page1[0].id != page2[0].id
    assert page2[0].id != page3[0].id

def test_crud_sorting(db):
    """Teste le tri dans les opérations CRUD."""
    # Création d'un utilisateur
    user = create_user(db, {
        "email": "test@example.com",
        "hashed_password": "hashed_password",
        "full_name": "Test User"
    })
    
    # Création de notifications avec différentes dates
    for i in range(5):
        create_notification(db, {
            "title": f"Test Notification {i}",
            "content": "Test Content",
            "channel": NotificationChannel.EMAIL,
            "recipient_id": user.id
        })
    
    # Test du tri par date de création (décroissant)
    notifications = get_notifications(db, sort_by="created_at", sort_order="desc")
    assert len(notifications) > 1
    assert notifications[0].created_at >= notifications[1].created_at
    
    # Test du tri par date de création (croissant)
    notifications = get_notifications(db, sort_by="created_at", sort_order="asc")
    assert len(notifications) > 1
    assert notifications[0].created_at <= notifications[1].created_at 