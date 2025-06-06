"""Routes pour la gestion des templates."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, crud
from ..dependencies import get_current_user, get_db

router = APIRouter()

@router.post("/", response_model=schemas.Template)
def create_template(
    template: schemas.TemplateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée un nouveau template."""
    return crud.create_template(db=db, template=template)

@router.get("/{template_id}", response_model=schemas.Template)
def read_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère un template par son ID."""
    db_template = crud.get_template(db, template_id=template_id)
    if db_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    return db_template

@router.put("/{template_id}", response_model=schemas.Template)
def update_template(
    template_id: int,
    template: schemas.TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour un template."""
    db_template = crud.update_template(db, template_id=template_id, template=template)
    if db_template is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    return db_template

@router.delete("/{template_id}", response_model=schemas.Template)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime un template."""
    db_template = crud.delete_template(db, template_id=template_id)
    if not db_template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    return db_template

@router.get("/", response_model=List[schemas.Template])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    channel: str = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste tous les templates."""
    templates = crud.get_templates(db, skip=skip, limit=limit, channel=channel)
    return templates

@router.post("/{template_id}/preview", response_model=schemas.TemplatePreview)
def preview_template(
    template_id: int,
    data: schemas.TemplatePreviewData,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Prévisualise un template avec des données."""
    template = crud.get_template(db, template_id=template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template non trouvé"
        )
    
    # Rendu du template
    rendered_content = template.render(data.model_dump())
    return {
        "subject": rendered_content.get("subject", ""),
        "content": rendered_content.get("content", "")
    } 