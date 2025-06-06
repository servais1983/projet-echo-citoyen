import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
import os
import sys

# Ajout du répertoire parent au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db
from app.main import app
from app.models import Alert, AlertType, AlertStatus

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

@pytest.fixture(scope="function")
def test_alert(db_session):
    alert = Alert(
        type=AlertType.INFO,
        message="Test alert",
        status=AlertStatus.ACTIVE,
        created_at=datetime.utcnow()
    )
    db_session.add(alert)
    db_session.commit()
    db_session.refresh(alert)
    return alert

def test_create_alert(client):
    response = client.post(
        "/alerts/",
        json={
            "type": "INFO",
            "message": "Test alert",
            "status": "ACTIVE"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "INFO"
    assert data["message"] == "Test alert"
    assert data["status"] == "ACTIVE"

def test_get_alert(client, test_alert):
    response = client.get(f"/alerts/{test_alert.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_alert.id
    assert data["type"] == test_alert.type
    assert data["message"] == test_alert.message
    assert data["status"] == test_alert.status

def test_update_alert(client, test_alert):
    response = client.put(
        f"/alerts/{test_alert.id}",
        json={
            "type": "WARNING",
            "message": "Updated test alert",
            "status": "RESOLVED"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "WARNING"
    assert data["message"] == "Updated test alert"
    assert data["status"] == "RESOLVED"

def test_delete_alert(client, test_alert):
    response = client.delete(f"/alerts/{test_alert.id}")
    assert response.status_code == 200
    response = client.get(f"/alerts/{test_alert.id}")
    assert response.status_code == 404

def test_list_alerts(client, test_alert):
    response = client.get("/alerts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_alert.id

def test_get_alerts_with_filters(client, test_alert):
    response = client.get("/alerts/?type=INFO&status=ACTIVE")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "INFO"
    assert data[0]["status"] == "ACTIVE"

def test_get_alert_stats(client, test_alert):
    # Création d'une deuxième alerte
    alert2 = Alert(
        type=AlertType.WARNING,
        message="Test alert 2",
        status=AlertStatus.RESOLVED,
        created_at=datetime.utcnow()
    )
    db_session = next(client.app.dependency_overrides[get_db]())
    db_session.add(alert2)
    db_session.commit()
    
    response = client.get("/alerts/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_alerts"] == 2
    assert "type_distribution" in data
    assert "status_distribution" in data

def test_invalid_alert_creation(client):
    response = client.post(
        "/alerts/",
        json={
            "type": "INVALID_TYPE",
            "message": "Test alert",
            "status": "ACTIVE"
        }
    )
    assert response.status_code == 422

def test_update_nonexistent_alert(client):
    response = client.put(
        "/alerts/999",
        json={
            "type": "WARNING",
            "message": "Updated test alert",
            "status": "RESOLVED"
        }
    )
    assert response.status_code == 404

def test_alert_resolution(client, test_alert):
    response = client.put(
        f"/alerts/{test_alert.id}",
        json={
            "type": test_alert.type,
            "message": test_alert.message,
            "status": "RESOLVED"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "RESOLVED"
    assert "resolved_at" in data 