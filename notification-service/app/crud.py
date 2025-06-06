"""Opérations CRUD pour les modèles."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from . import models, schemas
from .dependencies import get_password_hash


def get_notification(db: Session, notification_id: int) -> Optional[models.Notification]:
    """Récupère une notification par son ID."""
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()


def get_notifications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[models.Notification]:
    """Récupère une liste de notifications avec filtres optionnels."""
    query = db.query(models.Notification)
    
    if filters:
        if filters.get("channel"):
            query = query.filter(models.Notification.channel == filters["channel"])
        if filters.get("priority"):
            query = query.filter(models.Notification.priority == filters["priority"])
        if filters.get("status"):
            query = query.filter(models.Notification.status == filters["status"])
    
    return query.offset(skip).limit(limit).all()


def create_notification(
    db: Session,
    notification: schemas.NotificationCreate,
    user_id: Optional[int] = None
) -> models.Notification:
    """Crée une nouvelle notification."""
    db_notification = models.Notification(
        **notification.model_dump(),
        created_by=user_id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(
    db: Session,
    notification_id: int,
    notification: schemas.NotificationUpdate
) -> Optional[models.Notification]:
    """Met à jour une notification existante."""
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    
    update_data = notification.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification


def delete_notification(db: Session, notification_id: int) -> bool:
    """Supprime une notification."""
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return False
    
    db.delete(db_notification)
    db.commit()
    return True


def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Récupère un utilisateur par son ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    """Récupère un utilisateur par son email."""
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[models.User]:
    """Récupère une liste d'utilisateurs."""
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Crée un nouvel utilisateur."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(
    db: Session,
    user_id: int,
    user: schemas.UserUpdate
) -> Optional[models.User]:
    """Met à jour un utilisateur existant."""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Supprime un utilisateur."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def get_webhook(db: Session, webhook_id: int) -> Optional[models.Webhook]:
    """Récupère un webhook par son ID."""
    return db.query(models.Webhook).filter(models.Webhook.id == webhook_id).first()


def get_webhooks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    event: Optional[str] = None
) -> List[models.Webhook]:
    """Récupère la liste des webhooks avec filtres optionnels."""
    query = db.query(models.Webhook)
    if user_id:
        query = query.filter(models.Webhook.user_id == user_id)
    if event:
        query = query.filter(models.Webhook.events.contains([event]))
    return query.offset(skip).limit(limit).all()


def create_webhook(db: Session, webhook: schemas.WebhookCreate, user_id: int) -> models.Webhook:
    """Crée un nouveau webhook."""
    db_webhook = models.Webhook(**webhook.model_dump(), user_id=user_id)
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook


def update_webhook(
    db: Session,
    webhook_id: int,
    webhook: schemas.WebhookUpdate
) -> Optional[models.Webhook]:
    """Met à jour un webhook existant."""
    db_webhook = get_webhook(db, webhook_id)
    if not db_webhook:
        return None

    update_data = webhook.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_webhook, field, value)

    db.commit()
    db.refresh(db_webhook)
    return db_webhook


def delete_webhook(db: Session, webhook_id: int) -> bool:
    """Supprime un webhook."""
    db_webhook = get_webhook(db, webhook_id)
    if not db_webhook:
        return False

    db.delete(db_webhook)
    db.commit()
    return True


def get_template(db: Session, template_id: int) -> Optional[models.Template]:
    """Récupère un template par son ID."""
    return db.query(models.Template).filter(models.Template.id == template_id).first()


def get_templates(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    channel: Optional[models.NotificationChannel] = None,
    user_id: Optional[int] = None
) -> List[models.Template]:
    """Récupère la liste des templates avec filtres optionnels."""
    query = db.query(models.Template)
    if channel:
        query = query.filter(models.Template.channel == channel)
    if user_id:
        query = query.filter(models.Template.user_id == user_id)
    return query.offset(skip).limit(limit).all()


def create_template(db: Session, template: schemas.TemplateCreate, user_id: int) -> models.Template:
    """Crée un nouveau template."""
    db_template = models.Template(**template.model_dump(), user_id=user_id)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


def update_template(
    db: Session,
    template_id: int,
    template: schemas.TemplateUpdate
) -> Optional[models.Template]:
    """Met à jour un template existant."""
    db_template = get_template(db, template_id)
    if not db_template:
        return None

    update_data = template.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)

    db.commit()
    db.refresh(db_template)
    return db_template


def delete_template(db: Session, template_id: int) -> bool:
    """Supprime un template."""
    db_template = get_template(db, template_id)
    if not db_template:
        return False

    db.delete(db_template)
    db.commit()
    return True


def get_notification_stats(
    db: Session,
    channel: Optional[models.NotificationChannel] = None,
    priority: Optional[models.NotificationPriority] = None,
    status: Optional[models.NotificationStatus] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """Récupère les statistiques des notifications avec filtres optionnels."""
    query = db.query(models.Notification)
    
    if channel:
        query = query.filter(models.Notification.channel == channel)
    if priority:
        query = query.filter(models.Notification.priority == priority)
    if status:
        query = query.filter(models.Notification.status == status)
    if start_date:
        query = query.filter(models.Notification.created_at >= start_date)
    if end_date:
        query = query.filter(models.Notification.created_at <= end_date)
    
    total = query.count()
    
    stats_by_channel = {}
    for channel in models.NotificationChannel:
        count = query.filter(models.Notification.channel == channel).count()
        stats_by_channel[channel.value] = count
    
    stats_by_priority = {}
    for priority in models.NotificationPriority:
        count = query.filter(models.Notification.priority == priority).count()
        stats_by_priority[priority.value] = count
    
    stats_by_status = {}
    for status in models.NotificationStatus:
        count = query.filter(models.Notification.status == status).count()
        stats_by_status[status.value] = count
    
    return {
        "total_notifications": total,
        "notifications_by_channel": stats_by_channel,
        "notifications_by_priority": stats_by_priority,
        "notifications_by_status": stats_by_status
    }


def get_notification_stats_by_date(
    db: Session,
    start_date: datetime,
    end_date: datetime
) -> List[Dict[str, Any]]:
    """Récupère les statistiques des notifications par date."""
    query = db.query(
        func.date(models.Notification.created_at).label("date"),
        models.Notification.channel,
        models.Notification.priority,
        models.Notification.status,
        func.count(models.Notification.id).label("count")
    ).filter(
        models.Notification.created_at.between(start_date, end_date)
    ).group_by(
        func.date(models.Notification.created_at),
        models.Notification.channel,
        models.Notification.priority,
        models.Notification.status
    ).all()
    
    return [
        {
            "date": row.date,
            "channel": row.channel.value,
            "priority": row.priority.value,
            "status": row.status.value,
            "count": row.count
        }
        for row in query
    ]


def get_notification_stats_by_channel(db: Session) -> List[Dict[str, Any]]:
    """Récupère les statistiques des notifications par canal."""
    stats = []
    for channel in models.NotificationChannel:
        query = db.query(models.Notification).filter(models.Notification.channel == channel)
        total = query.count()
        success = query.filter(models.Notification.status == models.NotificationStatus.DELIVERED).count()
        success_rate = (success / total * 100) if total > 0 else 0
        
        avg_delivery_time = db.query(
            func.avg(
                func.extract('epoch', models.Notification.delivered_at) -
                func.extract('epoch', models.Notification.created_at)
            )
        ).filter(
            models.Notification.channel == channel,
            models.Notification.status == models.NotificationStatus.DELIVERED
        ).scalar() or 0
        
        stats.append({
            "channel": channel.value,
            "count": total,
            "success_rate": round(success_rate, 2),
            "average_delivery_time": round(avg_delivery_time, 2)
        })
    
    return stats


def get_notification_stats_by_priority(db: Session) -> List[Dict[str, Any]]:
    """Récupère les statistiques des notifications par priorité."""
    stats = []
    for priority in models.NotificationPriority:
        query = db.query(models.Notification).filter(models.Notification.priority == priority)
        total = query.count()
        success = query.filter(models.Notification.status == models.NotificationStatus.DELIVERED).count()
        success_rate = (success / total * 100) if total > 0 else 0
        
        avg_delivery_time = db.query(
            func.avg(
                func.extract('epoch', models.Notification.delivered_at) -
                func.extract('epoch', models.Notification.created_at)
            )
        ).filter(
            models.Notification.priority == priority,
            models.Notification.status == models.NotificationStatus.DELIVERED
        ).scalar() or 0
        
        stats.append({
            "priority": priority.value,
            "count": total,
            "success_rate": round(success_rate, 2),
            "average_delivery_time": round(avg_delivery_time, 2)
        })
    
    return stats


def get_notification_stats_by_status(db: Session) -> List[Dict[str, Any]]:
    """Récupère les statistiques des notifications par statut."""
    total = db.query(models.Notification).count()
    stats = []
    
    for status in models.NotificationStatus:
        count = db.query(models.Notification).filter(models.Notification.status == status).count()
        percentage = (count / total * 100) if total > 0 else 0
        
        stats.append({
            "status": status.value,
            "count": count,
            "percentage": round(percentage, 2)
        })
    
    return stats 