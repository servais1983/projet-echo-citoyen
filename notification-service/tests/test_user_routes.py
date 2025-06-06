"""Tests pour les routes d'utilisateur."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserUpdate


def test_create_user_route(client):
    """Teste la création d'un utilisateur via l'API."""
    user_data = {
        "email": "newuser@example.com",
        "password": "newpassword123",
        "full_name": "New User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "password" not in data


def test_get_user_route(client, test_token, test_user):
    """Teste la récupération d'un utilisateur via l'API."""
    response = client.get(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["full_name"] == test_user.full_name
    assert "password" not in data


def test_update_user_route(client, test_token, test_user):
    """Teste la mise à jour d'un utilisateur via l'API."""
    update_data = {
        "email": "updated@example.com",
        "full_name": "Updated Name"
    }
    response = client.put(
        f"/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == update_data["email"]
    assert data["full_name"] == update_data["full_name"]


def test_delete_user_route(client, test_token, test_user):
    """Teste la suppression d'un utilisateur via l'API."""
    response = client.delete(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    response = client.get(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_users_route(client, test_token, test_user):
    """Teste la liste des utilisateurs via l'API."""
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(user["id"] == test_user.id for user in data)


def test_create_user_invalid_data(client):
    """Teste la création d'un utilisateur avec des données invalides."""
    user_data = {
        "email": "invalid-email",
        "password": "short",
        "full_name": "Test User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_nonexistent_user(client, test_token):
    """Teste la récupération d'un utilisateur inexistant."""
    response = client.get(
        "/users/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_nonexistent_user(client, test_token):
    """Teste la mise à jour d'un utilisateur inexistant."""
    update_data = {
        "email": "updated@example.com",
        "full_name": "Updated Name"
    }
    response = client.put(
        "/users/999999",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_user(client, test_token):
    """Teste la suppression d'un utilisateur inexistant."""
    response = client.delete(
        "/users/999999",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_duplicate_user(client, test_user):
    """Teste la création d'un utilisateur avec un email déjà utilisé."""
    user_data = {
        "email": test_user.email,
        "password": "newpassword123",
        "full_name": "New User"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_user_duplicate_email(client, test_token, test_user):
    """Teste la mise à jour d'un utilisateur avec un email déjà utilisé."""
    # Créer un autre utilisateur
    other_user = User(
        email="other@example.com",
        hashed_password="hashedpassword123",
        full_name="Other User"
    )
    test_db.add(other_user)
    test_db.commit()

    # Essayer de mettre à jour l'utilisateur de test avec l'email de l'autre utilisateur
    update_data = {
        "email": other_user.email,
        "full_name": "Updated Name"
    }
    response = client.put(
        f"/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST 