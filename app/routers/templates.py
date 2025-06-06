from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from .. import crud, models, schemas
from ..dependencies import get_db, get_current_user

router = APIRouter()

@router.post("/", response_model=schemas.Template, status_code=status.HTTP_201_CREATED)
def create_template(
    template: schemas.TemplateCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée un nouveau template."""
    return crud.create_template(db=db, template=template, user_id=current_user.id)

@router.get("/{template_id}", response_model=schemas.Template)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère un template par son ID."""
    template = crud.get_template(db=db, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this template")
    return template

@router.put("/{template_id}", response_model=schemas.Template)
def update_template(
    template_id: int,
    template: schemas.TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Met à jour un template."""
    db_template = crud.get_template(db=db, template_id=template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    if db_template.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to update this template")
    return crud.update_template(db=db, template_id=template_id, template=template)

@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Supprime un template."""
    db_template = crud.get_template(db=db, template_id=template_id)
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    if db_template.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this template")
    crud.delete_template(db=db, template_id=template_id)
    return None

@router.get("/", response_model=List[schemas.Template])
def list_templates(
    skip: int = 0,
    limit: int = 100,
    channel: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Liste les templates avec filtres optionnels."""
    if current_user.is_admin:
        return crud.get_templates(db=db, skip=skip, limit=limit, channel=channel)
    return crud.get_user_templates(db=db, user_id=current_user.id, skip=skip, limit=limit, channel=channel)

@router.post("/{template_id}/preview", response_model=dict)
def preview_template(
    template_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Prévisualise un template avec des données."""
    template = crud.get_template(db=db, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to preview this template")
    
    try:
        subject = template.subject.format(**data)
        content = template.content.format(**data)
        return {"subject": subject, "content": content}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required data: {str(e)}")

@router.get("/{template_id}/usage", response_model=dict)
def get_template_usage(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques d'utilisation d'un template."""
    template = crud.get_template(db=db, template_id=template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    if template.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this template's usage")
    return crud.get_template_usage(db=db, template_id=template_id) 