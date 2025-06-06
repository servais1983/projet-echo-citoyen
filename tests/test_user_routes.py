import pytest
from fastapi import status
from datetime import datetime, timedelta

def test_create_user(client, test_token):
    user_data = {
        "email": "newuser@example.com",
        "full_name": "New User",
        "password": "testpassword123",
        "is_active": True
    }
    
    response = client.post(
        "/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["is_active"] == user_data["is_active"]
    assert "password" not in data

def test_get_user(client, test_token, test_user):
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

def test_update_user(client, test_token, test_user):
    update_data = {
        "full_name": "Updated User",
        "is_active": False
    }
    
    response = client.patch(
        f"/users/{test_user.id}",
        json=update_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["full_name"] == update_data["full_name"]
    assert data["is_active"] == update_data["is_active"]

def test_delete_user(client, test_token, test_user):
    response = client.delete(
        f"/users/{test_user.id}",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_list_users(client, test_token):
    response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

def test_filter_users(client, test_token):
    params = {
        "is_active": True,
        "search": "test"
    }
    
    response = client.get(
        "/users/",
        params=params,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    for user in data:
        assert user["is_active"] is True
        assert "test" in user["email"].lower() or "test" in user["full_name"].lower()

def test_invalid_email(client, test_token):
    user_data = {
        "email": "invalid_email",
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    response = client.post(
        "/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_user_validation(client, test_token):
    user_data = {
        "email": "test@example.com",
        "full_name": "",
        "password": ""
    }
    
    response = client.post(
        "/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_duplicate_email(client, test_token, test_user):
    user_data = {
        "email": test_user.email,
        "full_name": "Test User",
        "password": "testpassword123"
    }
    
    response = client.post(
        "/users/",
        json=user_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_change_password(client, test_token, test_user):
    password_data = {
        "current_password": "testpassword123",
        "new_password": "newpassword123"
    }
    
    response = client.post(
        f"/users/{test_user.id}/change-password",
        json=password_data,
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK

def test_user_stats(client, test_token, test_user):
    response = client.get(
        f"/users/{test_user.id}/stats",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "total_notifications" in data
    assert "success_rate" in data
    assert "last_activity" in data 