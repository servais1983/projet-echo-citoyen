from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Notification, status_code=status.HTTP_201_CREATED)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée une nouvelle notification."""
    return crud.create_notification(db=db, notification=notification, user_id=current_user.id)

@router.get("/{notification_id}", response_model=schemas.Notification)
def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère une notification par son ID."""
    notification = crud.get_notification(db=db, notification_id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this notification")
    return notification

@router.put("/{notification_id}", response_model=schemas.Notification)
def update_notification(
    notification_id: int,
    notification: schemas.NotificationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour une notification."""
    db_notification = crud.get_notification(db=db, notification_id=notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_notification.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this notification")
    return crud.update_notification(db=db, notification_id=notification_id, notification=notification)

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime une notification."""
    db_notification = crud.get_notification(db=db, notification_id=notification_id)
    if not db_notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if db_notification.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this notification")
    crud.delete_notification(db=db, notification_id=notification_id)
    return None

@router.get("/", response_model=List[schemas.Notification])
def list_notifications(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste les notifications avec filtres optionnels."""
    if current_user.is_admin:
        return crud.get_notifications(
            db=db,
            skip=skip,
            limit=limit,
            type=type,
            status=status
        )
    return crud.get_user_notifications(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        type=type,
        status=status
    )

@router.post("/batch", response_model=List[schemas.Notification], status_code=status.HTTP_201_CREATED)
def create_notifications(
    notifications: List[schemas.NotificationCreate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée plusieurs notifications en lot."""
    return crud.create_notifications(db=db, notifications=notifications, user_id=current_user.id)

@router.put("/batch", response_model=List[schemas.Notification])
def update_notifications(
    notifications: List[schemas.NotificationUpdate],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour plusieurs notifications en lot."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin users can update notifications in batch")
    return crud.update_notifications(db=db, notifications=notifications)

@router.delete("/batch", status_code=status.HTTP_204_NO_CONTENT)
def delete_notifications(
    notification_ids: List[int],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime plusieurs notifications en lot."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admin users can delete notifications in batch")
    crud.delete_notifications(db=db, notification_ids=notification_ids)
    return None 