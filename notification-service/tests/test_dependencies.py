"""Tests pour les dépendances de l'application."""

import pytest
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt

from app.dependencies import (
    get_current_user,
    get_password_hash,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)
from app.models import User
from app.database import get_db


def test_password_hashing():
    """Teste le hachage des mots de passe."""
    password = "testpassword123"
    hashed_password = get_password_hash(password)
    assert hashed_password != password
    assert verify_password(password, hashed_password)
    assert not verify_password("wrongpassword", hashed_password)


def test_create_access_token():
    """Teste la création d'un token d'accès."""
    user_data = {"sub": "test@example.com"}
    token = create_access_token(user_data)
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.fixture
def test_user(test_db):
    user = User(
        email="test@example.com",
        hashed_password="hashedpassword123",
        is_active=True,
        is_admin=False
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user


@pytest.mark.asyncio
async def test_get_current_user_valid_token(test_user, test_db):
    """Teste la récupération d'un utilisateur avec un token valide."""
    token = create_access_token({"sub": test_user.email})
    user = await get_current_user(token, test_db)
    assert user.id == test_user.id
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_current_user_invalid_token(test_db):
    """Teste la récupération d'un utilisateur avec un token invalide."""
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user("invalid_token", test_db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token(test_user, test_db):
    """Teste la récupération d'un utilisateur avec un token expiré."""
    expire = datetime.utcnow() - timedelta(minutes=15)
    token = jwt.encode(
        {"sub": test_user.email, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, test_db)
    assert exc_info.value.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(test_db):
    """Teste la récupération d'un utilisateur inexistant."""
    token = create_access_token({"sub": "nonexistent@example.com"})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(token, test_db)
    assert exc_info.value.status_code == 401 