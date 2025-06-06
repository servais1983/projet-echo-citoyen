"""Routes pour l'authentification."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..dependencies import (
    get_current_user,
    get_db,
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(
    tags=["authentication"]
)


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur et retourne un token JWT."""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=schemas.User)
def register_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Enregistre un nouvel utilisateur."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Un utilisateur avec cet email existe déjà"
        )
    return crud.create_user(db=db, user=user)


@router.get("/me", response_model=schemas.User)
def read_users_me(
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les informations de l'utilisateur connecté."""
    return current_user 