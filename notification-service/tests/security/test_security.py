import pytest
from fastapi.testclient import TestClient
import jwt
from datetime import datetime, timedelta
import json

from app.main import app
from tests.config import SECRET_KEY, ALGORITHM

client = TestClient(app)

def test_cors_headers():
    """Test des en-têtes CORS"""
    response = client.options(
        "/notifications/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST"
        }
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_security_headers():
    """Test des en-têtes de sécurité"""
    response = client.get("/notifications/")
    headers = response.headers
    
    assert "X-Content-Type-Options" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in headers
    assert "X-XSS-Protection" in headers
    assert "Strict-Transport-Security" in headers
    assert "Content-Security-Policy" in headers

def test_jwt_token_validation():
    """Test de la validation des tokens JWT"""
    # Token expiré
    expired_token = jwt.encode(
        {
            "sub": "test@example.com",
            "exp": datetime.utcnow() - timedelta(hours=1)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

    # Token invalide
    invalid_token = "invalid.token.here"
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {invalid_token}"}
    )
    assert response.status_code == 401

def test_sql_injection_prevention():
    """Test de la prévention des injections SQL"""
    # Tentative d'injection SQL dans le titre
    notification = {
        "subject": "'; DROP TABLE notifications; --",
        "content": "Test content",
        "channel": "email",
        "recipient": "test@example.com",
        "priority": "high"
    }
    
    response = client.post(
        "/notifications/",
        json=notification,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 400

def test_xss_prevention():
    """Test de la prévention des attaques XSS"""
    # Tentative d'injection XSS dans le contenu
    notification = {
        "subject": "Test XSS",
        "content": "<script>alert('XSS')</script>",
        "channel": "email",
        "recipient": "test@example.com",
        "priority": "high"
    }
    
    response = client.post(
        "/notifications/",
        json=notification,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 400

def test_rate_limiting():
    """Test de la limitation de taux"""
    # Envoyer plusieurs requêtes rapidement
    for _ in range(100):
        response = client.get(
            "/notifications/",
            headers={"Authorization": f"Bearer {get_test_token()}"}
        )
    
    # La requête suivante devrait être limitée
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 429

def test_input_validation():
    """Test de la validation des entrées"""
    # Email invalide
    notification = {
        "subject": "Test",
        "content": "Test content",
        "channel": "email",
        "recipient": "invalid-email",
        "priority": "high"
    }
    
    response = client.post(
        "/notifications/",
        json=notification,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 400

    # Canal invalide
    notification["channel"] = "invalid-channel"
    response = client.post(
        "/notifications/",
        json=notification,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 400

    # Priorité invalide
    notification["channel"] = "email"
    notification["priority"] = "invalid-priority"
    response = client.post(
        "/notifications/",
        json=notification,
        headers={"Authorization": f"Bearer {get_test_token()}"}
    )
    assert response.status_code == 400

def test_authentication_required():
    """Test de l'authentification requise"""
    # Requête sans token
    response = client.get("/notifications/")
    assert response.status_code == 401

    # Requête avec token invalide
    response = client.get(
        "/notifications/",
        headers={"Authorization": "Bearer invalid.token"}
    )
    assert response.status_code == 401

def get_test_token():
    """Helper pour obtenir un token de test valide"""
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    return response.json()["access_token"] 