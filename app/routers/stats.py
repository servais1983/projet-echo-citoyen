from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter()

@router.get("/notifications", response_model=dict)
def get_notification_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    channel: Optional[models.NotificationChannel] = None,
    status: Optional[models.NotificationStatus] = None,
    priority: Optional[models.NotificationPriority] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de début doit être antérieure à la date de fin"
        )
    return crud.get_notification_stats(
        db=db,
        start_date=start_date,
        end_date=end_date,
        channel=channel,
        status=status,
        priority=priority
    )

@router.get("/users", response_model=dict)
def get_user_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des utilisateurs."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_user_stats(db=db)

@router.get("/templates", response_model=dict)
def get_template_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des templates."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_template_stats(db=db)

@router.get("/webhooks", response_model=dict)
def get_webhook_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des webhooks."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_webhook_stats(db=db)

@router.get("/notifications/date", response_model=dict)
def get_notification_stats_by_date(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par date."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="La date de début doit être antérieure à la date de fin"
        )
    return crud.get_notification_stats_by_date(db=db, start_date=start_date, end_date=end_date)

@router.get("/notifications/channel", response_model=dict)
def get_notification_stats_by_channel(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par canal."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_notification_stats_by_channel(db=db)

@router.get("/notifications/priority", response_model=dict)
def get_notification_stats_by_priority(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par priorité."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_notification_stats_by_priority(db=db)

@router.get("/notifications/status", response_model=dict)
def get_notification_stats_by_status(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par statut."""
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès non autorisé")
    return crud.get_notification_stats_by_status(db=db) 