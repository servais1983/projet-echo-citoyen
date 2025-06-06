"""Tests pour les utilisateurs."""

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models import User
from app.dependencies import get_password_hash


@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.fixture
def test_token(client, test_user):
    response = client.post(
        "/token",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]


def test_create_user(client):
    """Teste la création d'un utilisateur."""
    response = client.post(
        "/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data


def test_read_user(client, test_user, test_token):
    """Teste la lecture d'un utilisateur."""
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


def test_update_user(client, test_user, test_token):
    """Teste la mise à jour d'un utilisateur."""
    response = client.put(
        f"/users/{test_user.id}",
        json={
            "full_name": "Updated Name",
            "email": "updated@example.com"
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["email"] == "updated@example.com"


def test_delete_user(client, test_user, test_token):
    """Teste la suppression d'un utilisateur."""
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


def test_list_users(client, test_user, test_token):
    """Teste la liste des utilisateurs."""
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) > 0
    assert any(user["id"] == test_user.id for user in data)


def test_authenticate_user(client, test_user):
    """Teste l'authentification d'un utilisateur."""
    response = client.post(
        "/token",
        data={
            "username": test_user.email,
            "password": "testpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_invalid_authentication(client):
    """Teste l'authentification avec des identifiants invalides."""
    response = client.post(
        "/token",
        data={
            "username": "wrong@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED 