import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi import status
from sqlalchemy.orm import Session

from main import app
from app.database import Base, get_db
from app.models import User, Notification, NotificationChannel, NotificationPriority, NotificationStatus
from app.dependencies import get_password_hash

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables de test
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture
def test_db():
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    return response.json()["access_token"]

def test_create_notification(test_token):
    """Teste la création d'une notification."""
    response = client.post(
        "/notifications/",
        json={
            "channel": "email",
            "recipient": "test@example.com",
            "subject": "Test Subject",
            "content": "Test Content",
            "priority": "normal"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["channel"] == "email"
    assert data["recipient"] == "test@example.com"
    assert data["subject"] == "Test Subject"
    assert data["content"] == "Test Content"
    assert data["priority"] == "normal"
    assert data["status"] == "pending"

def test_read_notification(test_token, test_db, test_user):
    """Teste la lecture d'une notification."""
    # Créer une notification de test
    notification = Notification(
        subject="Test Notification",
        content="Test Content",
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        priority=NotificationPriority.HIGH,
        created_by=test_user.id
    )
    test_db.add(notification)
    test_db.commit()
    
    response = client.get(f"/notifications/{notification.id}", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == notification.id
    assert data["channel"] == notification.channel
    assert data["recipient"] == notification.recipient

def test_update_notification(test_token, test_db, test_user):
    """Teste la mise à jour d'une notification."""
    # Créer une notification de test
    notification = Notification(
        subject="Test Notification",
        content="Test Content",
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        priority=NotificationPriority.HIGH,
        created_by=test_user.id
    )
    test_db.add(notification)
    test_db.commit()
    
    response = client.put(
        f"/notifications/{notification.id}",
        json={
            "subject": "Updated Subject",
            "content": "Updated Content"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["subject"] == "Updated Subject"
    assert data["content"] == "Updated Content"

def test_delete_notification(test_token, test_db, test_user):
    """Teste la suppression d'une notification."""
    # Créer une notification de test
    notification = Notification(
        subject="Test Notification",
        content="Test Content",
        channel=NotificationChannel.EMAIL,
        recipient="test@example.com",
        priority=NotificationPriority.HIGH,
        created_by=test_user.id
    )
    test_db.add(notification)
    test_db.commit()
    
    response = client.delete(f"/notifications/{notification.id}", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == status.HTTP_200_OK
    response = client.get(f"/notifications/{notification.id}", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_list_notifications(test_token, test_db, test_user):
    """Teste la liste des notifications."""
    # Créer quelques notifications de test
    notifications = [
        Notification(
            subject=f"Test Notification {i}",
            content=f"Content {i}",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority=NotificationPriority.MEDIUM,
            created_by=test_user.id
        )
        for i in range(3)
    ]
    
    for notification in notifications:
        test_db.add(notification)
    test_db.commit()
    
    response = client.get("/notifications/", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(n["id"] == notification.id for n in data)

def test_filter_notifications(test_token, test_db, test_user):
    """Teste le filtrage des notifications."""
    # Créer des notifications de test avec différents canaux et priorités
    notifications = [
        Notification(
            subject=f"Test {i}",
            content=f"Content {i}",
            channel=NotificationChannel.EMAIL if i % 2 == 0 else NotificationChannel.SLACK,
            recipient="test@example.com",
            priority=NotificationPriority.HIGH if i % 3 == 0 else NotificationPriority.MEDIUM,
            created_by=test_user.id
        )
        for i in range(6)
    ]
    
    for notification in notifications:
        test_db.add(notification)
    test_db.commit()
    
    response = client.get("/notifications/?channel=email&priority=normal", headers={"Authorization": f"Bearer {test_token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert all(n["channel"] == "email" for n in data)
    assert all(n["priority"] == "normal" for n in data)

def test_get_notification_stats(test_token, test_db, test_user):
    # Créer des notifications de test avec différents canaux et priorités
    notifications = [
        Notification(
            subject=f"Test {i}",
            content=f"Content {i}",
            channel=NotificationChannel.EMAIL if i % 2 == 0 else NotificationChannel.SLACK,
            recipient="test@example.com",
            priority=NotificationPriority.HIGH if i % 3 == 0 else NotificationPriority.MEDIUM,
            created_by=test_user.id
        )
        for i in range(6)
    ]
    
    for notification in notifications:
        test_db.add(notification)
    test_db.commit()
    
    response = client.get(
        "/notifications/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_notifications"] == 6
    assert "notifications_by_channel" in data
    assert "notifications_by_priority" in data

def test_create_notification_invalid_data(test_token):
    invalid_data = {
        "subject": "Test",
        "content": "Test",
        "channel": "invalid_channel",  # Canal invalide
        "recipient": "test@example.com",
        "priority": "high"
    }
    
    response = client.post(
        "/notifications/",
        json=invalid_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 422  # Erreur de validation

def test_get_nonexistent_notification(test_token):
    response = client.get(
        "/notifications/999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == 404

def test_get_notification_stats_with_filters(test_token, test_db, test_user):
    """Teste les statistiques des notifications avec des filtres."""
    # Créer des notifications de test avec différents canaux et priorités
    notifications = [
        Notification(
            subject=f"Test {i}",
            content=f"Content {i}",
            channel=NotificationChannel.EMAIL if i % 2 == 0 else NotificationChannel.SLACK,
            recipient="test@example.com",
            priority=NotificationPriority.HIGH if i % 3 == 0 else NotificationPriority.MEDIUM,
            created_by=test_user.id
        )
        for i in range(6)
    ]
    
    for notification in notifications:
        test_db.add(notification)
    test_db.commit()
    
    # Test avec filtre par canal
    response = client.get(
        "/notifications/stats?channel=email",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_notifications"] == 3
    assert data["notifications_by_channel"]["email"] == 3
    
    # Test avec filtre par priorité
    response = client.get(
        "/notifications/stats?priority=high",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_notifications"] == 2
    assert data["notifications_by_priority"]["high"] == 2

def test_unauthorized_access():
    """Teste l'accès non autorisé aux notifications."""
    # Test sans token
    response = client.get("/notifications/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test avec token invalide
    response = client.get(
        "/notifications/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Test création sans token
    response = client.post(
        "/notifications/",
        json={
            "channel": "email",
            "recipient": "test@example.com",
            "subject": "Test",
            "content": "Test",
            "priority": "normal"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 