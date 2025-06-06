from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    """Crée un nouvel utilisateur."""
    db_user = crud.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà utilisé"
        )
    return crud.create_user(db=db, user=user)

@router.get("/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère un utilisateur par son ID."""
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    user = crud.get_user(db=db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    return user

@router.patch("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour un utilisateur."""
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    db_user = crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    
    # Vérification de l'unicité de l'email
    if user.email and user.email != db_user.email:
        existing_user = crud.get_user_by_email(db=db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email déjà utilisé"
            )
    
    return crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime un utilisateur."""
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    db_user = crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    crud.delete_user(db=db, user_id=user_id)

@router.get("/", response_model=List[schemas.User])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste les utilisateurs."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_users(db=db, skip=skip, limit=limit)

@router.post("/{user_id}/change-password", response_model=schemas.User)
def change_password(
    user_id: int,
    current_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Change le mot de passe d'un utilisateur."""
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    db_user = crud.get_user(db=db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur non trouvé")
    
    # Vérification du mot de passe actuel
    if not crud.verify_password(current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )
    
    return crud.update_user_password(db=db, user_id=user_id, new_password=new_password) 