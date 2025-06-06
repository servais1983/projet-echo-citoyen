"""Schémas Pydantic pour la validation des données."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict

from .models import NotificationChannel, NotificationPriority, NotificationStatus


class Token(BaseModel):
    """Schéma pour le token JWT."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schéma pour les données du token."""
    email: str | None = None


class UserBase(BaseModel):
    """Schéma de base pour les utilisateurs."""
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur."""
    password: str


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur."""
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = None
    is_active: bool | None = None
    is_admin: bool | None = None


class User(UserBase):
    """Schéma pour un utilisateur."""
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class UserInDB(User):
    """Schéma pour un utilisateur en base de données."""
    hashed_password: str


class NotificationBase(BaseModel):
    """Schéma de base pour les notifications."""
    channel: NotificationChannel
    recipient: str
    subject: str
    content: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    notification_metadata: Dict[str, Any] | None = None


class NotificationCreate(NotificationBase):
    """Schéma pour la création d'une notification."""
    pass


class NotificationUpdate(BaseModel):
    """Schéma pour la mise à jour d'une notification."""
    channel: NotificationChannel | None = None
    recipient: str | None = None
    subject: str | None = None
    content: str | None = None
    priority: NotificationPriority | None = None
    status: NotificationStatus | None = None
    notification_metadata: Dict[str, Any] | None = None


class Notification(NotificationBase):
    """Schéma pour une notification."""
    id: int
    status: NotificationStatus
    created_at: datetime
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    created_by: int | None = None

    model_config = ConfigDict(from_attributes=True)


class NotificationResponse(Notification):
    """Schéma pour la réponse d'une notification."""
    pass


class NotificationInDB(Notification):
    """Schéma pour une notification en base de données."""
    pass


class NotificationStats(BaseModel):
    """Schéma pour les statistiques des notifications."""
    total_notifications: int
    notifications_by_channel: Dict[str, int]
    notifications_by_priority: Dict[str, int]
    notifications_by_status: Dict[str, int]


class NotificationStatsByDate(BaseModel):
    """Schéma pour les statistiques des notifications par date."""
    date: datetime
    count: int
    channel: str
    priority: str
    status: str


class NotificationStatsByChannel(BaseModel):
    """Schéma pour les statistiques des notifications par canal."""
    channel: str
    count: int
    success_rate: float
    average_delivery_time: float


class NotificationStatsByPriority(BaseModel):
    """Schéma pour les statistiques des notifications par priorité."""
    priority: str
    count: int
    success_rate: float
    average_delivery_time: float


class NotificationStatsByStatus(BaseModel):
    """Schéma pour les statistiques des notifications par statut."""
    status: str
    count: int
    percentage: float


class WebhookBase(BaseModel):
    """Schéma de base pour un webhook."""
    url: str
    events: List[str]
    secret: str
    is_active: bool = True


class WebhookCreate(WebhookBase):
    """Schéma pour la création d'un webhook."""
    pass


class WebhookUpdate(BaseModel):
    """Schéma pour la mise à jour d'un webhook."""
    url: str | None = None
    events: List[str] | None = None
    secret: str | None = None
    is_active: bool | None = None


class Webhook(WebhookBase):
    """Schéma pour un webhook."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class WebhookEvent(BaseModel):
    """Schéma pour un événement de webhook."""
    event: str
    data: Dict[str, Any]


class TemplateBase(BaseModel):
    """Schéma de base pour un template."""
    name: str
    subject: str
    content: str
    channel: NotificationChannel


class TemplateCreate(TemplateBase):
    """Schéma pour la création d'un template."""
    pass


class TemplateUpdate(BaseModel):
    """Schéma pour la mise à jour d'un template."""
    name: str | None = None
    subject: str | None = None
    content: str | None = None
    channel: NotificationChannel | None = None


class Template(TemplateBase):
    """Schéma pour un template."""
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class TemplatePreviewData(BaseModel):
    """Schéma pour les données de prévisualisation d'un template."""
    data: Dict[str, Any]


class TemplatePreview(BaseModel):
    """Schéma pour la prévisualisation d'un template."""
    subject: str
    content: str 