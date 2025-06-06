"""Routes pour la gestion des webhooks."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import hmac
import hashlib

from .. import models, schemas, crud
from ..dependencies import get_current_user, get_db

router = APIRouter()

@router.post("/", response_model=schemas.Webhook)
def create_webhook(
    webhook: schemas.WebhookCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée un nouveau webhook."""
    return crud.create_webhook(db=db, webhook=webhook, user_id=current_user.id)

@router.get("/{webhook_id}", response_model=schemas.Webhook)
def read_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère un webhook par son ID."""
    db_webhook = crud.get_webhook(db, webhook_id=webhook_id)
    if db_webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook non trouvé"
        )
    return db_webhook

@router.put("/{webhook_id}", response_model=schemas.Webhook)
def update_webhook(
    webhook_id: int,
    webhook: schemas.WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour un webhook."""
    db_webhook = crud.update_webhook(db, webhook_id=webhook_id, webhook=webhook)
    if db_webhook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook non trouvé"
        )
    return db_webhook

@router.delete("/{webhook_id}", response_model=schemas.Webhook)
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime un webhook."""
    db_webhook = crud.delete_webhook(db, webhook_id=webhook_id)
    if not db_webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook non trouvé"
        )
    return db_webhook

@router.get("/", response_model=List[schemas.Webhook])
def list_webhooks(
    skip: int = 0,
    limit: int = 100,
    event: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste tous les webhooks."""
    webhooks = crud.get_webhooks(db, skip=skip, limit=limit, event=event)
    return webhooks

@router.post("/{webhook_id}/deliver", status_code=status.HTTP_200_OK)
async def deliver_webhook(
    webhook_id: int,
    event_data: schemas.WebhookEvent,
    x_webhook_signature: str = Header(None),
    db: Session = Depends(get_db)
):
    """Livraison d'un webhook."""
    webhook = crud.get_webhook(db, webhook_id=webhook_id)
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook non trouvé"
        )
    
    # Vérification de la signature
    if not x_webhook_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature manquante"
        )
    
    expected_signature = hmac.new(
        webhook.secret.encode(),
        event_data.model_dump_json().encode(),
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(x_webhook_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Signature invalide"
        )
    
    # Traitement du webhook
    return {"status": "success"} 