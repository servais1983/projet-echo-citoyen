"""Modèles de données pour le service de notification."""

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLAlchemyEnum, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class NotificationChannel(str, Enum):
    """Canaux de notification disponibles."""
    EMAIL = "EMAIL"
    SMS = "SMS"
    PUSH = "PUSH"
    SLACK = "SLACK"


class NotificationPriority(str, Enum):
    """Priorités de notification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class NotificationStatus(str, Enum):
    """Statuts possibles d'une notification."""
    PENDING = "PENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    FAILED = "FAILED"


class User(Base):
    """Modèle d'utilisateur."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    notifications = relationship("Notification", back_populates="creator")


class Notification(Base):
    """Modèle de notification."""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    channel = Column(SQLAlchemyEnum(NotificationChannel), nullable=False)
    recipient = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    content = Column(String, nullable=False)
    priority = Column(SQLAlchemyEnum(NotificationPriority), nullable=False)
    status = Column(SQLAlchemyEnum(NotificationStatus), nullable=False, default=NotificationStatus.PENDING)
    notification_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    is_read = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)
    created_by = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="notifications") 