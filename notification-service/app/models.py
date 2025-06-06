"""Modèles SQLAlchemy pour la base de données."""

from datetime import datetime
from enum import Enum
from typing import Optional, List
from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, JSON, ARRAY, Table
from sqlalchemy.orm import relationship

from .database import Base


class NotificationChannel(str, Enum):
    """Canal de notification."""
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"


class NotificationPriority(str, Enum):
    """Priorité de la notification."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class NotificationStatus(str, Enum):
    """Statut de la notification."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"


# Table d'association pour les événements de webhook
webhook_events = Table(
    "webhook_events",
    Base.metadata,
    Column("webhook_id", Integer, ForeignKey("webhooks.id")),
    Column("event", String)
)

class User(Base):
    """Modèle pour les utilisateurs."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    notifications = relationship("Notification", back_populates="user")
    webhooks = relationship("Webhook", back_populates="user")
    templates = relationship("Template", back_populates="user")


class Notification(Base):
    """Modèle pour les notifications."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(SQLEnum(NotificationChannel), index=True)
    recipient = Column(String, index=True)
    subject = Column(String)
    content = Column(String)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING)
    notification_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    created_by = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="notifications")


class Webhook(Base):
    """Modèle pour les webhooks."""
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String)
    events = Column(JSON)  # Liste des événements
    secret = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="webhooks")


class Template(Base):
    """Modèle pour les templates."""
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subject = Column(String)
    content = Column(String)
    channel = Column(SQLEnum(NotificationChannel), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="templates") 