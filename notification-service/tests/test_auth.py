import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from fastapi import status

from main import app
from app.models import User
from app.database import Base, get_db
from app.dependencies import get_password_hash
from app.schemas import UserCreate

client = TestClient(app)

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

def test_login_success(test_user):
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(test_user):
    response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401

def test_login_nonexistent_user():
    response = client.post(
        "/token",
        data={"username": "nonexistent@example.com", "password": "password"}
    )
    assert response.status_code == 401

def test_verify_token(test_user):
    # Obtenir un token
    login_response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Vérifier le token
    response = client.post(
        "/verify",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_admin"] == False

def test_verify_invalid_token():
    response = client.post(
        "/verify",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401

def test_get_current_user(test_user):
    # Obtenir un token
    login_response = client.post(
        "/token",
        data={"username": "test@example.com", "password": "testpassword"}
    )
    token = login_response.json()["access_token"]

    # Tester l'accès à une route protégée
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_inactive_user(test_db):
    # Créer un utilisateur inactif
    user = User(
        email="inactive@example.com",
        hashed_password=get_password_hash("password"),
        is_active=False
    )
    test_db.add(user)
    test_db.commit()

    # Tenter de se connecter
    response = client.post(
        "/token",
        data={"username": "inactive@example.com", "password": "password"}
    )
    assert response.status_code == 401

def test_admin_user(test_db):
    # Créer un utilisateur admin
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_admin=True
    )
    test_db.add(user)
    test_db.commit()

    # Se connecter
    login_response = client.post(
        "/token",
        data={"username": "admin@example.com", "password": "adminpassword"}
    )
    token = login_response.json()["access_token"]

    # Vérifier les informations
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@example.com"
    assert data["is_admin"] == True

def test_register_user(client):
    """Teste l'enregistrement d'un utilisateur."""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data

def test_register_existing_user(client, test_user):
    """Teste l'enregistrement d'un utilisateur existant."""
    user_data = {
        "email": test_user.email,
        "password": "newpassword123",
        "full_name": "New User"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_user(client, test_user):
    """Teste la connexion d'un utilisateur."""
    login_data = {
        "username": test_user.email,
        "password": "testpassword123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    """Teste la connexion avec des identifiants invalides."""
    login_data = {
        "username": "wrong@example.com",
        "password": "wrongpassword"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_token):
    """Teste la récupération de l'utilisateur courant."""
    response = client.get(
        "/me",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "password" not in data

def test_get_current_user_no_token(client):
    """Teste la récupération de l'utilisateur courant sans token."""
    response = client.get("/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user_invalid_token(client):
    """Teste la récupération de l'utilisateur courant avec un token invalide."""
    response = client.get(
        "/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_password(client, test_user, test_token):
    """Teste le changement de mot de passe."""
    password_data = {
        "current_password": "testpassword123",
        "new_password": "newpassword123"
    }
    response = client.post(
        "/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK

    # Vérifier que le nouveau mot de passe fonctionne
    login_data = {
        "username": test_user.email,
        "password": "newpassword123"
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == status.HTTP_200_OK

def test_change_password_wrong_current(client, test_token):
    """Teste le changement de mot de passe avec un mot de passe actuel incorrect."""
    password_data = {
        "current_password": "wrongpassword",
        "new_password": "newpassword123"
    }
    response = client.post(
        "/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_change_password_no_token(client):
    """Teste le changement de mot de passe sans token."""
    password_data = {
        "current_password": "testpassword123",
        "new_password": "newpassword123"
    }
    response = client.post("/change-password", json=password_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 