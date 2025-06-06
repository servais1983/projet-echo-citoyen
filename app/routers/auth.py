from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user, get_current_active_user, create_access_token
from ..core.config import settings

router = APIRouter()

@router.post("/login", response_model=schemas.Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur et retourne un token JWT."""
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login/json", response_model=schemas.Token)
def login_json(
    credentials: schemas.UserLogin,
    db: Session = Depends(get_db)
):
    """Authentifie un utilisateur avec des données JSON et retourne un token JWT."""
    user = crud.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Crée un nouvel utilisateur."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/change-password", response_model=schemas.User)
def change_password(
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Change le mot de passe de l'utilisateur."""
    if not crud.authenticate_user(db, current_user.email, current_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect current password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return crud.update_user(db=db, user_id=current_user.id, user=schemas.UserUpdate(password=new_password))

@router.get("/verify", response_model=schemas.User)
def verify_token(
    current_user: models.User = Depends(get_current_user)
):
    """Vérifie la validité du token et retourne l'utilisateur courant."""
    return current_user

@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_active_user)):
    """Récupère l'utilisateur courant."""
    return current_user 