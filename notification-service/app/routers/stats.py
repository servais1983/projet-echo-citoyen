"""Routes pour les statistiques."""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..dependencies import get_current_user, get_db

router = APIRouter()

@router.get("/notifications", response_model=schemas.NotificationStats)
def get_notification_stats(
    channel: str = None,
    priority: str = None,
    status: str = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications."""
    return crud.get_notification_stats(
        db,
        channel=channel,
        priority=priority,
        status=status,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/notifications/by-date", response_model=List[schemas.NotificationStatsByDate])
def get_notification_stats_by_date(
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par date."""
    return crud.get_notification_stats_by_date(db, start_date, end_date)

@router.get("/notifications/by-channel", response_model=List[schemas.NotificationStatsByChannel])
def get_notification_stats_by_channel(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par canal."""
    return crud.get_notification_stats_by_channel(db, start_date, end_date)

@router.get("/notifications/by-priority", response_model=List[schemas.NotificationStatsByPriority])
def get_notification_stats_by_priority(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par priorité."""
    return crud.get_notification_stats_by_priority(db, start_date, end_date)

@router.get("/notifications/by-status", response_model=List[schemas.NotificationStatsByStatus])
def get_notification_stats_by_status(
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications par statut."""
    return crud.get_notification_stats_by_status(db, start_date, end_date) 