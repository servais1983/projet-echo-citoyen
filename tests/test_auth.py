import pytest
from fastapi import status
from datetime import datetime, timedelta
from app.core.security import create_access_token
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app
from app.models import User
from app.schemas import UserCreate

client = TestClient(app)

@pytest.fixture
def test_user():
    """Crée un utilisateur de test."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }

@pytest.fixture
def test_user_token(test_user):
    """Crée un token pour l'utilisateur de test."""
    return create_access_token(
        data={"sub": test_user["email"]},
        expires_delta=timedelta(minutes=15)
    )

def test_register_user(test_user):
    """Teste l'enregistrement d'un nouvel utilisateur."""
    response = client.post(
        "/auth/register",
        json=test_user
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["full_name"] == test_user["full_name"]
    assert "id" in data
    assert "password" not in data

def test_register_existing_user(test_user):
    """Teste l'enregistrement d'un utilisateur existant."""
    # Premier enregistrement
    client.post("/auth/register", json=test_user)
    
    # Tentative de réenregistrement
    response = client.post(
        "/auth/register",
        json=test_user
    )
    assert response.status_code == 400
    assert "email already registered" in response.json()["detail"].lower()

def test_login_success(test_user):
    """Teste la connexion réussie."""
    # Crée l'utilisateur
    client.post("/auth/register", json=test_user)
    
    # Tente de se connecter
    response = client.post(
        "/auth/login",
        json={
            "username": test_user["email"],
            "password": test_user["password"]
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(test_user):
    """Teste la connexion avec un mauvais mot de passe."""
    # Crée l'utilisateur
    client.post("/auth/register", json=test_user)
    
    # Tente de se connecter avec un mauvais mot de passe
    response = client.post(
        "/auth/login",
        json={
            "username": test_user["email"],
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_login_nonexistent_user():
    """Teste la connexion d'un utilisateur inexistant."""
    response = client.post(
        "/auth/login",
        json={
            "username": "nonexistent@example.com",
            "password": "anypassword"
        }
    )
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

def test_get_current_user(test_user_token):
    """Teste la récupération de l'utilisateur courant."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "full_name" in data

def test_get_current_user_no_token():
    """Teste la récupération de l'utilisateur sans token."""
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

def test_get_current_user_invalid_token():
    """Teste la récupération de l'utilisateur avec un token invalide."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_password_reset_request(test_user):
    """Teste la demande de réinitialisation de mot de passe."""
    # Crée l'utilisateur
    client.post("/auth/register", json=test_user)
    
    # Demande de réinitialisation
    response = client.post(
        "/auth/password-reset-request",
        json={"email": test_user["email"]}
    )
    assert response.status_code == 200
    assert "reset token sent" in response.json()["message"].lower()

def test_password_reset_nonexistent_user():
    """Teste la demande de réinitialisation pour un utilisateur inexistant."""
    response = client.post(
        "/auth/password-reset-request",
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == 404
    assert "user not found" in response.json()["detail"].lower()

def test_password_reset(test_user):
    """Teste la réinitialisation du mot de passe."""
    # Crée l'utilisateur
    client.post("/auth/register", json=test_user)
    
    # Demande de réinitialisation
    reset_response = client.post(
        "/auth/password-reset-request",
        json={"email": test_user["email"]}
    )
    reset_token = reset_response.json()["reset_token"]
    
    # Réinitialisation du mot de passe
    new_password = "newpassword123"
    response = client.post(
        "/auth/password-reset",
        json={
            "token": reset_token,
            "new_password": new_password
        }
    )
    assert response.status_code == 200
    assert "password updated" in response.json()["message"].lower()
    
    # Vérifie que la connexion fonctionne avec le nouveau mot de passe
    login_response = client.post(
        "/auth/login",
        json={
            "username": test_user["email"],
            "password": new_password
        }
    )
    assert login_response.status_code == 200

def test_login_invalid_credentials():
    """Teste la connexion avec des identifiants invalides."""
    login_data = {
        "username": "test@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_token(test_user_token):
    """Teste la vérification du token."""
    response = client.get(
        "/auth/verify",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == "test@example.com"

def test_inactive_user():
    """Teste la connexion d'un utilisateur inactif."""
    login_data = {
        "username": "inactive@example.com",
        "password": "testpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_admin_user():
    """Teste la connexion d'un administrateur."""
    login_data = {
        "username": "admin@example.com",
        "password": "adminpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_login_user():
    """Teste la connexion d'un utilisateur normal."""
    login_data = {
        "username": "user@example.com",
        "password": "userpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_change_password_success(test_user_token):
    """Teste le changement de mot de passe réussi."""
    password_data = {
        "current_password": "testpassword",
        "new_password": "newpassword"
    }
    response = client.post(
        "/auth/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

def test_change_password_wrong_current(test_user_token):
    """Teste le changement de mot de passe avec un mot de passe actuel incorrect."""
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword"
    }
    response = client.post(
        "/auth/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_verify_invalid_token():
    """Teste la vérification d'un token invalide."""
    response = client.get(
        "/auth/verify",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_register_new_user():
    """Teste l'inscription d'un nouvel utilisateur."""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "full_name": "New User"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data

def test_change_password_no_token():
    """Teste le changement de mot de passe sans token."""
    password_data = {
        "current_password": "testpassword",
        "new_password": "newpassword"
    }
    response = client.post("/auth/change-password", json=password_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 