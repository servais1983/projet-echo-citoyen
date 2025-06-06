from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import hmac
import hashlib
import json
import httpx
from fastapi import Request

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Webhook, status_code=status.HTTP_201_CREATED)
def create_webhook(
    webhook: schemas.WebhookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée un nouveau webhook."""
    return crud.create_webhook(db=db, webhook=webhook, user_id=current_user.id)

@router.get("/{webhook_id}", response_model=schemas.Webhook)
def get_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère un webhook par son ID."""
    webhook = crud.get_webhook(db=db, webhook_id=webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if webhook.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this webhook")
    return webhook

@router.put("/{webhook_id}", response_model=schemas.Webhook)
def update_webhook(
    webhook_id: int,
    webhook: schemas.WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour un webhook."""
    db_webhook = crud.get_webhook(db=db, webhook_id=webhook_id)
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if db_webhook.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this webhook")
    return crud.update_webhook(db=db, webhook_id=webhook_id, webhook=webhook)

@router.delete("/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime un webhook."""
    db_webhook = crud.get_webhook(db=db, webhook_id=webhook_id)
    if not db_webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if db_webhook.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this webhook")
    crud.delete_webhook(db=db, webhook_id=webhook_id)
    return None

@router.get("/", response_model=List[schemas.Webhook])
def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    event: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste les webhooks avec filtres optionnels."""
    if current_user.is_admin:
        return crud.get_webhooks(db=db, skip=skip, limit=limit, event=event)
    return crud.get_user_webhooks(db=db, user_id=current_user.id, skip=skip, limit=limit, event=event)

@router.post("/{webhook_id}/deliver", status_code=status.HTTP_200_OK)
def deliver_webhook(
    webhook_id: int,
    event: dict,
    signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Livraison d'un webhook."""
    webhook = crud.get_webhook(db=db, webhook_id=webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if not webhook.is_active:
        raise HTTPException(status_code=400, detail="Webhook is not active")
    if not signature:
        raise HTTPException(status_code=401, detail="Missing signature")
    if not verify_webhook_signature(webhook.secret, json.dumps(event).encode(), signature):
        raise HTTPException(status_code=401, detail="Invalid signature")
    return {"status": "success"}

@router.get("/{webhook_id}/stats", response_model=dict)
def get_webhook_stats(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques d'un webhook."""
    webhook = crud.get_webhook(db=db, webhook_id=webhook_id)
    if not webhook:
        raise HTTPException(status_code=404, detail="Webhook not found")
    if webhook.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this webhook's stats")
    return crud.get_webhook_stats(db=db, webhook_id=webhook_id) 