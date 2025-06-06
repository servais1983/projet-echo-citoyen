"""Tests de sécurité pour le service de notification."""

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from jose import jwt
from datetime import datetime, timedelta
from fastapi import status
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    sanitize_input,
    rate_limit,
    get_current_user,
    verify_token,
    generate_csrf_token,
    verify_csrf_token
)
from app.models import User
from app.db.session import SessionLocal

from app.main import app

# Désactive le rate limiting pendant les tests
app.state.testing = True

@pytest.fixture
def db():
    """Fixture pour la base de données."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db):
    """Crée un utilisateur de test sans doublon."""
    from sqlalchemy.exc import NoResultFound
    # Supprimer l'utilisateur s'il existe déjà
    user = db.query(User).filter_by(email="test@example.com").first()
    if user:
        db.delete(user)
        db.commit()
    # Créer le nouvel utilisateur
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True,
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def test_token(test_user):
    """Crée un token pour l'utilisateur de test."""
    return create_access_token(
        data={"sub": test_user.email},
        expires_delta=timedelta(minutes=15)
    )

def test_cors_headers(client):
    """Teste les en-têtes CORS."""
    response = client.options(
        "/notifications/",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,Authorization"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_security_headers(client):
    """Teste les en-têtes de sécurité."""
    response = client.get("/notifications/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    # Vérification des en-têtes de sécurité de base
    assert "x-content-type-options" in response.headers
    assert "x-frame-options" in response.headers
    assert "x-xss-protection" in response.headers
    assert "content-security-policy" in response.headers
    
    # Vérification des nouveaux en-têtes de sécurité
    assert "referrer-policy" in response.headers
    assert "permissions-policy" in response.headers
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
    
    # Vérification de la politique CSP
    csp = response.headers["content-security-policy"]
    assert "default-src 'self'" in csp
    assert "frame-ancestors 'none'" in csp
    assert "form-action 'self'" in csp

def test_jwt_token_validation(client):
    """Teste la validation du token JWT."""
    # Test avec un token expiré
    expired_token = create_access_token(
        data={"sub": "test@example.com"},
        expires_delta=timedelta(microseconds=1)
    )
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test avec un token invalide
    response = client.get(
        "/notifications/",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Test avec un token valide
    valid_token = create_access_token(
        data={"sub": "test@example.com"},
        expires_delta=timedelta(minutes=15)
    )
    payload = verify_token(valid_token)
    assert "jti" in payload
    assert "iat" in payload
    assert "exp" in payload
    assert payload["sub"] == "test@example.com"

def test_sql_injection_prevention(client, test_token):
    """Teste la prévention des injections SQL."""
    sql_injection = "'; DROP TABLE users; --"
    response = client.get(
        f"/notifications/?title={sql_injection}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

def test_xss_prevention(client, test_token):
    """Teste la prévention des attaques XSS."""
    malicious_content = "<script>alert('xss')</script>"
    notification_data = {
        "title": malicious_content,
        "content": malicious_content,
        "type": "info",
        "status": "pending",
        "user_id": 1
    }
    
    # Générer un token CSRF
    csrf_token = generate_csrf_token()
    
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={
            "Authorization": f"Bearer {test_token}",
            "X-CSRF-Token": csrf_token
        },
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "<script>" not in data["title"]
    assert "<script>" not in data["content"]

def test_rate_limiting(client, test_token):
    """Teste la limitation de débit."""
    # Désactiver le mode test pour ce test
    app.state.testing = False
    
    # Test des requêtes dans la limite
    for _ in range(2):
        response = client.get(
            "/notifications/",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK

    # Test du dépassement de limite
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    
    # Réactiver le mode test
    app.state.testing = True

def test_input_validation(client, test_token):
    """Teste la validation des entrées."""
    invalid_data = {
        "title": "",
        "content": "",
        "type": "invalid",
        "status": "invalid",
        "user_id": 1
    }
    
    # Générer un token CSRF
    csrf_token = generate_csrf_token()
    
    response = client.post(
        "/notifications/",
        json=invalid_data,
        headers={
            "Authorization": f"Bearer {test_token}",
            "X-CSRF-Token": csrf_token
        },
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_password_hashing():
    """Teste le hachage et la vérification des mots de passe."""
    password = "test_password123"
    hashed = get_password_hash(password)
    
    # Vérifie que le hash est différent du mot de passe original
    assert hashed != password
    
    # Vérifie que le mot de passe est correctement vérifié
    assert verify_password(password, hashed)
    
    # Vérifie que le mauvais mot de passe est rejeté
    assert not verify_password("wrong_password", hashed)

def test_access_token_creation():
    """Teste la création des tokens d'accès."""
    data = {"sub": "test@example.com"}
    
    # Test sans délai d'expiration
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Test avec délai d'expiration personnalisé
    expires_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta)
    assert isinstance(token, str)
    assert len(token) > 0

def test_sanitize_input():
    """Teste la sanitization des entrées utilisateur."""
    # Test avec une chaîne normale
    input_text = "Hello World"
    assert sanitize_input(input_text) == "Hello World"
    
    # Test avec des caractères spéciaux
    input_text = "<script>alert('xss')</script>"
    sanitized = sanitize_input(input_text)
    assert "<" not in sanitized
    assert ">" not in sanitized
    
    # Test avec des caractères HTML
    input_text = "& < > \" '"
    sanitized = sanitize_input(input_text)
    assert "&amp;" in sanitized
    assert "&quot;" in sanitized
    assert "&#x27;" in sanitized
    
    # Test avec un type non-string
    assert sanitize_input(123) == "123"
    assert sanitize_input(None) == "None"

@pytest.mark.asyncio
async def test_get_current_user():
    """Teste la récupération de l'utilisateur courant."""
    # Crée une requête simulée
    class MockRequest:
        def __init__(self):
            self.headers = {}

    request = MockRequest()

    # Test sans token
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token manquant ou invalide"

def test_token_expiration(client):
    """Teste l'expiration des tokens."""
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(microseconds=1)  # Expiration très rapide
    token = create_access_token(data, expires_delta)

    # Attend que le token expire
    import time
    time.sleep(0.1)

    # Vérifie que le token est expiré
    response = client.get(
        "/notifications/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_csrf_protection(client, test_token):
    """Teste la protection CSRF."""
    # Test d'une requête POST sans token CSRF
    response = client.post(
        "/notifications/",
        json={"title": "Test", "content": "Test", "user_id": 1},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Test d'une requête POST avec token CSRF valide
    csrf_token = generate_csrf_token()
    response = client.post(
        "/notifications/",
        json={"title": "Test", "content": "Test", "user_id": 1},
        headers={
            "Authorization": f"Bearer {test_token}",
            "X-CSRF-Token": csrf_token
        },
        cookies={"csrf_token": csrf_token}
    )
    assert response.status_code == status.HTTP_201_CREATED

def test_sanitize_input_enhanced():
    """Teste la sanitization améliorée des entrées utilisateur."""
    # Test avec des caractères de contrôle
    input_text = "Hello\x00World\x1F"
    sanitized = sanitize_input(input_text)
    assert "\x00" not in sanitized
    assert "\x1F" not in sanitized
    
    # Test avec des balises HTML complexes
    input_text = "<div onclick='alert(1)'>Test</div>"
    sanitized = sanitize_input(input_text)
    assert "<div" not in sanitized
    assert "onclick" not in sanitized
    
    # Test avec des caractères Unicode
    input_text = "Hello\u2028World\u2029"
    sanitized = sanitize_input(input_text)
    assert "\u2028" not in sanitized
    assert "\u2029" not in sanitized
    
    # Test avec des caractères spéciaux multiples
    input_text = "&lt;script&gt;alert('xss')&lt;/script&gt;"
    sanitized = sanitize_input(input_text)
    assert "&lt;" not in sanitized
    assert "&gt;" not in sanitized 