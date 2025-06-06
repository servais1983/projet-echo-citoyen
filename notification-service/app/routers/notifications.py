"""Routes pour la gestion des notifications."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
    dependencies=[Depends(get_current_user)]
)


@router.post("/", response_model=schemas.Notification)
def create_notification(
    notification: schemas.NotificationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée une nouvelle notification."""
    return crud.create_notification(db=db, notification=notification, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Notification])
def read_notifications(
    skip: int = 0,
    limit: int = 100,
    channel: Optional[models.NotificationChannel] = None,
    priority: Optional[models.NotificationPriority] = None,
    status: Optional[models.NotificationStatus] = None,
    db: Session = Depends(get_db)
):
    """Récupère la liste des notifications avec filtres optionnels."""
    filters = {
        "channel": channel,
        "priority": priority,
        "status": status
    }
    return crud.get_notifications(db, skip=skip, limit=limit, filters=filters)


@router.get("/{notification_id}", response_model=schemas.Notification)
def read_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Récupère une notification spécifique."""
    db_notification = crud.get_notification(db, notification_id=notification_id)
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return db_notification


@router.put("/{notification_id}", response_model=schemas.Notification)
def update_notification(
    notification_id: int,
    notification: schemas.NotificationUpdate,
    db: Session = Depends(get_db)
):
    """Met à jour une notification."""
    db_notification = crud.update_notification(
        db, notification_id=notification_id, notification=notification
    )
    if db_notification is None:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return db_notification


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Supprime une notification."""
    success = crud.delete_notification(db, notification_id=notification_id)
    if not success:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return {"message": "Notification supprimée avec succès"}


@router.get("/stats", response_model=schemas.NotificationStats)
def get_notification_stats(
    db: Session = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    channel: Optional[models.NotificationChannel] = None,
    priority: Optional[models.NotificationPriority] = None,
    status: Optional[models.NotificationStatus] = None
):
    """Récupère les statistiques des notifications avec filtres optionnels."""
    return crud.get_notification_stats(
        db,
        start_date=start_date,
        end_date=end_date,
        channel=channel,
        priority=priority,
        status=status
    ) 