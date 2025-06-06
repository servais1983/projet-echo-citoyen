"""Tests de sécurité pour le service de notification."""

import pytest
import time
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from jose import jwt
from datetime import timedelta
from fastapi import status
from app.core.config import settings
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    sanitize_input,
    rate_limit,
    get_current_user
)

from app.main import app

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
    assert "x-content-type-options" in response.headers
    assert "x-frame-options" in response.headers
    assert "x-xss-protection" in response.headers
    assert "content-security-policy" in response.headers

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

def test_sql_injection_prevention(client, test_token):
    """Teste la prévention des injections SQL."""
    malicious_query = "' OR '1'='1"
    response = client.get(
        f"/notifications/?recipient={malicious_query}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_xss_prevention(client, test_token):
    """Teste la prévention des attaques XSS."""
    malicious_content = "<script>alert('xss')</script>"
    notification_data = {
        "channel": "email",
        "recipient": "test@example.com",
        "subject": malicious_content,
        "content": malicious_content,
        "priority": "high"
    }
    response = client.post(
        "/notifications/",
        json=notification_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "<script>" not in data["subject"]
    assert "<script>" not in data["content"]

@pytest.mark.asyncio
async def test_rate_limiting():
    """Teste la limitation de débit."""
    @rate_limit(limit=2, period=1)
    async def test_endpoint(request):
        return {"status": "success"}
    
    # Crée une requête simulée
    class MockRequest:
        def __init__(self, ip):
            self.client = type('Client', (), {'host': ip})()
    
    request = MockRequest("127.0.0.1")
    
    # Test des requêtes dans la limite
    for _ in range(2):
        result = await test_endpoint(request)
        assert result["status"] == "success"
    
    # Test du dépassement de limite
    with pytest.raises(HTTPException) as exc_info:
        await test_endpoint(request)
    assert exc_info.value.status_code == 429
    assert "Trop de requêtes" in str(exc_info.value.detail)

def test_input_validation(client, test_token):
    """Teste la validation des entrées."""
    invalid_data = {
        "channel": "invalid",
        "recipient": "invalid-email",
        "subject": "",
        "content": "",
        "priority": "invalid"
    }
    response = client.post(
        "/notifications/",
        json=invalid_data,
        headers={"Authorization": f"Bearer {test_token}"}
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

def test_get_current_user():
    """Teste la récupération de l'utilisateur courant."""
    # Crée une requête simulée
    class MockRequest:
        def __init__(self, headers=None):
            self.headers = headers or {}
    
    # Test sans token
    request = MockRequest()
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(request)
    assert exc_info.value.status_code == 401
    assert "Token manquant" in str(exc_info.value.detail)
    
    # Test avec token invalide
    request = MockRequest(headers={"Authorization": "Bearer invalid_token"})
    with pytest.raises(HTTPException) as exc_info:
        get_current_user(request)
    assert exc_info.value.status_code == 401
    assert "Token invalide" in str(exc_info.value.detail)

def test_token_expiration():
    """Teste l'expiration des tokens."""
    data = {"sub": "test@example.com"}
    expires_delta = timedelta(microseconds=1)  # Expiration très rapide
    token = create_access_token(data, expires_delta)
    
    # Attend que le token expire
    time.sleep(0.1)
    
    # Vérifie que le token est expiré
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def test_invalid_token():
    """Teste la gestion des tokens invalides."""
    with pytest.raises(jwt.JWTError):
        jwt.decode("invalid_token", settings.SECRET_KEY, algorithms=[settings.ALGORITHM]) 