from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from .core.security import verify_password
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_notification(db: Session, notification_id: int):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()

def get_notifications(db: Session, skip: int = 0, limit: int = 100, type: Optional[str] = None, status: Optional[str] = None):
    query = db.query(models.Notification)
    if type:
        query = query.filter(models.Notification.type == type)
    if status:
        query = query.filter(models.Notification.status == status)
    return query.offset(skip).limit(limit).all()

def create_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
    notification_data = notification.dict()
    if "user_id" in notification_data:
        del notification_data["user_id"]
    db_notification = models.Notification(**notification_data, user_id=user_id)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_template(db: Session, template_id: int):
    return db.query(models.Template).filter(models.Template.id == template_id).first()

def get_templates(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Template).offset(skip).limit(limit).all()

def create_template(db: Session, template: schemas.TemplateCreate, user_id: int):
    db_template = models.Template(**template.dict(), user_id=user_id)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

def get_webhook(db: Session, webhook_id: int):
    return db.query(models.Webhook).filter(models.Webhook.id == webhook_id).first()

def get_webhooks(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Webhook).offset(skip).limit(limit).all()

def create_webhook(db: Session, webhook: schemas.WebhookCreate, user_id: int):
    db_webhook = models.Webhook(**webhook.dict(), user_id=user_id)
    db.add(db_webhook)
    db.commit()
    db.refresh(db_webhook)
    return db_webhook

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def update_notification(db: Session, notification_id: int, notification: schemas.NotificationUpdate):
    db_notification = get_notification(db, notification_id)
    if not db_notification:
        return None
    
    update_data = notification.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notification, field, value)
    
    db.commit()
    db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: int):
    db_notification = get_notification(db, notification_id)
    if db_notification:
        db.delete(db_notification)
        db.commit()
    return None

def get_user_notifications(db: Session, user_id: int, skip: int = 0, limit: int = 100, type: Optional[str] = None, status: Optional[str] = None):
    query = db.query(models.Notification).filter(models.Notification.user_id == user_id)
    if type:
        query = query.filter(models.Notification.type == type)
    if status:
        query = query.filter(models.Notification.status == status)
    return query.offset(skip).limit(limit).all()

def create_notifications(db: Session, notifications: list[schemas.NotificationCreate], user_id: int):
    db_notifications = []
    for notification in notifications:
        db_notification = models.Notification(**notification.dict(), user_id=user_id)
        db.add(db_notification)
        db_notifications.append(db_notification)
    db.commit()
    for notification in db_notifications:
        db.refresh(notification)
    return db_notifications

def update_notifications(db: Session, notifications: list[schemas.NotificationUpdate]):
    updated_notifications = []
    for notification in notifications:
        db_notification = get_notification(db, notification.id)
        if db_notification:
            update_data = notification.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_notification, field, value)
            updated_notifications.append(db_notification)
    db.commit()
    for notification in updated_notifications:
        db.refresh(notification)
    return updated_notifications

def delete_notifications(db: Session, notification_ids: list[int]):
    for notification_id in notification_ids:
        db_notification = get_notification(db, notification_id)
        if db_notification:
            db.delete(db_notification)
    db.commit()
    return None

def update_template(db: Session, template_id: int, template: schemas.TemplateUpdate):
    db_template = get_template(db, template_id)
    if not db_template:
        return None
    
    update_data = template.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_template, field, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template

def delete_template(db: Session, template_id: int):
    db_template = get_template(db, template_id)
    if db_template:
        db.delete(db_template)
        db.commit()
    return None

def get_user_templates(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Template).filter(models.Template.user_id == user_id).offset(skip).limit(limit).all()

def get_template_usage(db: Session, template_id: int):
    template = get_template(db, template_id)
    if not template:
        return None
    
    usage_stats = {
        "total_uses": db.query(models.Notification).filter(models.Notification.template_id == template_id).count(),
        "by_channel": {},
        "by_status": {},
        "by_priority": {}
    }
    
    # Statistiques par canal
    for channel in models.NotificationChannel:
        count = db.query(models.Notification).filter(
            models.Notification.template_id == template_id,
            models.Notification.channel == channel
        ).count()
        usage_stats["by_channel"][channel.value] = count
    
    # Statistiques par statut
    for status in models.NotificationStatus:
        count = db.query(models.Notification).filter(
            models.Notification.template_id == template_id,
            models.Notification.status == status
        ).count()
        usage_stats["by_status"][status.value] = count
    
    # Statistiques par priorité
    for priority in models.NotificationPriority:
        count = db.query(models.Notification).filter(
            models.Notification.template_id == template_id,
            models.Notification.priority == priority
        ).count()
        usage_stats["by_priority"][priority.value] = count
    
    return usage_stats

def update_webhook(db: Session, webhook_id: int, webhook: schemas.WebhookUpdate):
    db_webhook = get_webhook(db, webhook_id)
    if not db_webhook:
        return None
    
    update_data = webhook.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_webhook, field, value)
    
    db.commit()
    db.refresh(db_webhook)
    return db_webhook

def delete_webhook(db: Session, webhook_id: int):
    db_webhook = get_webhook(db, webhook_id)
    if db_webhook:
        db.delete(db_webhook)
        db.commit()
    return None

def get_user_webhooks(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Webhook).filter(models.Webhook.user_id == user_id).offset(skip).limit(limit).all()

def get_webhook_stats(db: Session, webhook_id: int):
    webhook = get_webhook(db, webhook_id)
    if not webhook:
        return None
    
    stats = {
        "total_deliveries": 0,
        "successful_deliveries": 0,
        "failed_deliveries": 0,
        "last_delivery": None,
        "average_response_time": 0
    }
    
    # TODO: Implémenter la logique de statistiques des webhooks
    
    return stats

def get_notification_stats(db: Session, start_date=None, end_date=None, channel=None, status=None, priority=None):
    query = db.query(models.Notification)
    
    if start_date:
        query = query.filter(models.Notification.created_at >= start_date)
    if end_date:
        query = query.filter(models.Notification.created_at <= end_date)
    if channel:
        query = query.filter(models.Notification.channel == channel)
    if status:
        query = query.filter(models.Notification.status == status)
    if priority:
        query = query.filter(models.Notification.priority == priority)
    
    stats = {
        "total": query.count(),
        "by_channel": {},
        "by_status": {},
        "by_priority": {}
    }
    
    # Statistiques par canal
    for channel in models.NotificationChannel:
        count = query.filter(models.Notification.channel == channel).count()
        stats["by_channel"][channel.value] = count
    
    # Statistiques par statut
    for status in models.NotificationStatus:
        count = query.filter(models.Notification.status == status).count()
        stats["by_status"][status.value] = count
    
    # Statistiques par priorité
    for priority in models.NotificationPriority:
        count = query.filter(models.Notification.priority == priority).count()
        stats["by_priority"][priority.value] = count
    
    return stats

def get_notification_stats_by_date(db: Session, start_date=None, end_date=None):
    query = db.query(models.Notification)
    
    if start_date:
        query = query.filter(models.Notification.created_at >= start_date)
    if end_date:
        query = query.filter(models.Notification.created_at <= end_date)
    
    # TODO: Implémenter la logique de statistiques par date
    
    return {}

def get_notification_stats_by_channel(db: Session):
    stats = {}
    for channel in models.NotificationChannel:
        count = db.query(models.Notification).filter(models.Notification.channel == channel).count()
        stats[channel.value] = count
    return stats

def get_notification_stats_by_priority(db: Session):
    stats = {}
    for priority in models.NotificationPriority:
        count = db.query(models.Notification).filter(models.Notification.priority == priority).count()
        stats[priority.value] = count
    return stats

def get_notification_stats_by_status(db: Session):
    stats = {}
    for status in models.NotificationStatus:
        count = db.query(models.Notification).filter(models.Notification.status == status).count()
        stats[status.value] = count
    return stats

def get_user_stats(db: Session):
    total_users = db.query(models.User).count()
    active_users = db.query(models.User).filter(models.User.is_active == True).count()
    admin_users = db.query(models.User).filter(models.User.is_admin == True).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "admin_users": admin_users,
        "inactive_users": total_users - active_users
    }

def get_template_stats(db: Session):
    total_templates = db.query(models.Template).count()
    templates_by_channel = {}
    
    for channel in models.NotificationChannel:
        count = db.query(models.Template).filter(models.Template.channel == channel).count()
        templates_by_channel[channel.value] = count
    
    return {
        "total_templates": total_templates,
        "templates_by_channel": templates_by_channel
    }

def get_webhook_stats(db: Session):
    total_webhooks = db.query(models.Webhook).count()
    active_webhooks = db.query(models.Webhook).filter(models.Webhook.is_active == True).count()
    
    return {
        "total_webhooks": total_webhooks,
        "active_webhooks": active_webhooks,
        "inactive_webhooks": total_webhooks - active_webhooks
    }

def update_user_password(db: Session, user_id: int, new_password: str):
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.hashed_password = pwd_context.hash(new_password)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return None 