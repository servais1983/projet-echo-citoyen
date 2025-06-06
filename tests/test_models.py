import pytest
from datetime import datetime
from app.models import (
    User,
    Notification,
    NotificationTemplate,
    Webhook,
    Stats,
    Base,
    NotificationChannel,
    NotificationStatus,
    NotificationPriority
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Crée une session de base de données pour les tests."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_user_model(db_session):
    """Teste le modèle User."""
    # Création d'un utilisateur
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Vérification
    db_user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert db_user is not None
    assert db_user.email == "test@example.com"
    assert db_user.full_name == "Test User"
    assert db_user.is_active is True
    assert db_user.created_at is not None
    assert db_user.updated_at is not None

def test_notification_model(db_session):
    """Teste le modèle Notification."""
    # Création d'un utilisateur
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Création d'une notification
    notification = Notification(
        title="Test Notification",
        content="This is a test notification",
        type="info",
        user_id=user.id,
        status="pending"
    )
    db_session.add(notification)
    db_session.commit()
    
    # Vérification
    db_notification = db_session.query(Notification).filter(
        Notification.user_id == user.id
    ).first()
    assert db_notification is not None
    assert db_notification.title == "Test Notification"
    assert db_notification.content == "This is a test notification"
    assert db_notification.type == "info"
    assert db_notification.status == "pending"
    assert db_notification.created_at is not None

def test_notification_template_model(db_session):
    """Teste le modèle NotificationTemplate."""
    # Création d'un template
    template = NotificationTemplate(
        name="Test Template",
        content="Hello {{name}}!",
        type="welcome",
        variables=["name"]
    )
    db_session.add(template)
    db_session.commit()
    
    # Vérification
    db_template = db_session.query(NotificationTemplate).filter(
        NotificationTemplate.name == "Test Template"
    ).first()
    assert db_template is not None
    assert db_template.content == "Hello {{name}}!"
    assert db_template.type == "welcome"
    assert "name" in db_template.variables
    assert db_template.created_at is not None

def test_webhook_model(db_session):
    """Teste le modèle Webhook."""
    # Création d'un utilisateur
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Création d'un webhook
    webhook = Webhook(
        url="https://example.com/webhook",
        events=["notification.created", "notification.updated"],
        user_id=user.id,
        is_active=True
    )
    db_session.add(webhook)
    db_session.commit()
    
    # Vérification
    db_webhook = db_session.query(Webhook).filter(
        Webhook.user_id == user.id
    ).first()
    assert db_webhook is not None
    assert db_webhook.url == "https://example.com/webhook"
    assert "notification.created" in db_webhook.events
    assert "notification.updated" in db_webhook.events
    assert db_webhook.is_active is True
    assert db_webhook.created_at is not None

def test_stats_model(db_session):
    """Teste le modèle Stats."""
    # Création d'un utilisateur
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Création de statistiques
    stats = Stats(
        user_id=user.id,
        notifications_sent=10,
        notifications_delivered=8,
        notifications_failed=2,
        period="daily",
        date=datetime.now().date()
    )
    db_session.add(stats)
    db_session.commit()
    
    # Vérification
    db_stats = db_session.query(Stats).filter(
        Stats.user_id == user.id
    ).first()
    assert db_stats is not None
    assert db_stats.notifications_sent == 10
    assert db_stats.notifications_delivered == 8
    assert db_stats.notifications_failed == 2
    assert db_stats.period == "daily"
    assert db_stats.date is not None

def test_user_relationships(db_session):
    """Teste les relations du modèle User."""
    # Création d'un utilisateur
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    
    # Création de notifications
    notification1 = Notification(
        title="Test 1",
        content="Content 1",
        user_id=user.id
    )
    notification2 = Notification(
        title="Test 2",
        content="Content 2",
        user_id=user.id
    )
    db_session.add_all([notification1, notification2])
    
    # Création d'un webhook
    webhook = Webhook(
        url="https://example.com/webhook",
        events=["notification.created"],
        user_id=user.id
    )
    db_session.add(webhook)
    
    # Création de statistiques
    stats = Stats(
        user_id=user.id,
        notifications_sent=2,
        period="daily"
    )
    db_session.add(stats)
    db_session.commit()
    
    # Vérification des relations
    db_user = db_session.query(User).filter(User.email == "test@example.com").first()
    assert len(db_user.notifications) == 2
    assert len(db_user.webhooks) == 1
    assert len(db_user.stats) == 1

def test_notification_relationships(db_session):
    """Teste les relations du modèle Notification."""
    # Création d'un utilisateur
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )
    db_session.add(user)
    
    # Création d'un template
    template = NotificationTemplate(
        name="Test Template",
        content="Hello {{name}}!",
        type="welcome"
    )
    db_session.add(template)
    db_session.commit()
    
    # Création d'une notification
    notification = Notification(
        title="Test",
        content="Content",
        user_id=user.id,
        template_id=template.id
    )
    db_session.add(notification)
    db_session.commit()
    
    # Vérification des relations
    db_notification = db_session.query(Notification).filter(
        Notification.user_id == user.id
    ).first()
    assert db_notification.user is not None
    assert db_notification.template is not None
    assert db_notification.user.email == "test@example.com"
    assert db_notification.template.name == "Test Template"

def test_template_model(db_session):
    """Teste le modèle Template."""
    template = NotificationTemplate(
        name="Test Template",
        content="Hello {{name}}!",
        variables=["name"],
        type="welcome"
    )
    db_session.add(template)
    db_session.commit()
    
    assert template.name == "Test Template"
    assert template.content == "Hello {{name}}!"
    assert template.variables == ["name"]
    assert template.type == "welcome"
    assert isinstance(template.created_at, datetime)
    assert isinstance(template.updated_at, datetime)

def test_notification_channel_enum():
    """Teste l'énumération NotificationChannel."""
    assert NotificationChannel.EMAIL.value == "email"
    assert NotificationChannel.SMS.value == "sms"
    assert NotificationChannel.PUSH.value == "push"
    assert NotificationChannel.WEBHOOK.value == "webhook"

def test_notification_status_enum():
    """Teste l'énumération NotificationStatus."""
    assert NotificationStatus.PENDING.value == "pending"
    assert NotificationStatus.SENT.value == "sent"
    assert NotificationStatus.FAILED.value == "failed"
    assert NotificationStatus.CANCELLED.value == "cancelled"

def test_notification_priority_enum():
    """Teste l'énumération NotificationPriority."""
    assert NotificationPriority.LOW.value == "low"
    assert NotificationPriority.NORMAL.value == "normal"
    assert NotificationPriority.HIGH.value == "high"
    assert NotificationPriority.URGENT.value == "urgent"

def test_model_validation():
    """Teste la validation des modèles."""
    # Test de validation du modèle User
    with pytest.raises(ValueError):
        User(email="invalid_email")
    
    # Test de validation du modèle Notification
    with pytest.raises(ValueError):
        Notification(
            title="Test Notification",
            content="Test Content",
            channel="invalid_channel"
        )
    
    # Test de validation du modèle Template
    with pytest.raises(ValueError):
        NotificationTemplate(
            name="Test Template",
            content="Test Content",
            variables="invalid_variables"
        )
    
    # Test de validation du modèle Webhook
    with pytest.raises(ValueError):
        Webhook(
            url="invalid_url",
            events="invalid_events"
        )

def test_model_constraints(db_session):
    """Teste les contraintes des modèles."""
    # Test de contrainte d'unicité d'email
    user1 = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User 1"
    )
    db_session.add(user1)
    db_session.commit()
    
    user2 = User(
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User 2"
    )
    db_session.add(user2)
    with pytest.raises(Exception):
        db_session.commit()
    
    # Test de contrainte d'unicité de nom de template
    template1 = NotificationTemplate(
        name="Test Template",
        content="Test Content 1",
        type="welcome"
    )
    db_session.add(template1)
    db_session.commit()
    
    template2 = NotificationTemplate(
        name="Test Template",
        content="Test Content 2",
        type="welcome"
    )
    db_session.add(template2)
    with pytest.raises(Exception):
        db_session.commit()
    
    # Test de contrainte d'unicité d'URL de webhook
    webhook1 = Webhook(
        url="https://example.com/webhook",
        events=["notification.created"],
        user_id=user1.id
    )
    db_session.add(webhook1)
    db_session.commit()
    
    webhook2 = Webhook(
        url="https://example.com/webhook",
        events=["notification.created"],
        user_id=user1.id
    )
    db_session.add(webhook2)
    with pytest.raises(Exception):
        db_session.commit() 