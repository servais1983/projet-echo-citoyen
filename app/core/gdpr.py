from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .config import settings
from .logging import log_data_access
from app.models.user import User
from app.models.notification import Notification
from app.models.template import Template
from app.models.webhook import Webhook

class GDPRManager:
    def __init__(self, db: Session):
        self.db = db

    def export_user_data(self, user_id: int) -> Dict[str, Any]:
        """Exporte toutes les données d'un utilisateur."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Collecte des données
        data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            },
            "notifications": [
                {
                    "id": n.id,
                    "title": n.title,
                    "content": n.content,
                    "status": n.status,
                    "created_at": n.created_at
                }
                for n in user.notifications
            ],
            "templates": [
                {
                    "id": t.id,
                    "name": t.name,
                    "content": t.content,
                    "created_at": t.created_at
                }
                for t in user.templates
            ],
            "webhooks": [
                {
                    "id": w.id,
                    "url": w.url,
                    "state": w.state,
                    "created_at": w.created_at
                }
                for w in user.webhooks
            ]
        }

        log_data_access(user_id, "export", "user_data_export")
        return data

    def delete_user_data(self, user_id: int) -> bool:
        """Supprime toutes les données d'un utilisateur."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Suppression des données associées
        self.db.query(Notification).filter(Notification.user_id == user_id).delete()
        self.db.query(Template).filter(Template.user_id == user_id).delete()
        self.db.query(Webhook).filter(Webhook.user_id == user_id).delete()
        self.db.delete(user)
        self.db.commit()

        log_data_access(user_id, "delete", "user_data_deletion")
        return True

    def anonymize_user_data(self, user_id: int) -> bool:
        """Anonymise les données d'un utilisateur."""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("Utilisateur non trouvé")

        # Anonymisation des données
        user.email = f"deleted_{user.id}@deleted.com"
        user.is_active = False
        self.db.commit()

        log_data_access(user_id, "anonymize", "user_data_anonymization")
        return True

    def cleanup_expired_data(self) -> Dict[str, int]:
        """Nettoie les données expirées selon la politique de conservation."""
        now = datetime.utcnow()
        stats = {
            "notifications": 0,
            "templates": 0,
            "webhooks": 0
        }

        # Suppression des notifications expirées
        expired_notifications = self.db.query(Notification).filter(
            Notification.created_at < now - timedelta(days=settings.DATA_RETENTION_DAYS)
        ).all()
        for notification in expired_notifications:
            self.db.delete(notification)
            stats["notifications"] += 1

        # Suppression des templates inactifs
        expired_templates = self.db.query(Template).filter(
            Template.updated_at < now - timedelta(days=settings.DATA_RETENTION_DAYS)
        ).all()
        for template in expired_templates:
            self.db.delete(template)
            stats["templates"] += 1

        # Suppression des webhooks inactifs
        expired_webhooks = self.db.query(Webhook).filter(
            Webhook.updated_at < now - timedelta(days=settings.DATA_RETENTION_DAYS)
        ).all()
        for webhook in expired_webhooks:
            self.db.delete(webhook)
            stats["webhooks"] += 1

        self.db.commit()
        return stats

    def get_data_retention_policy(self) -> Dict[str, Any]:
        """Retourne la politique de conservation des données."""
        return {
            "retention_period_days": settings.DATA_RETENTION_DAYS,
            "data_types": {
                "notifications": "Supprimées après la période de conservation",
                "templates": "Supprimés après la période de conservation",
                "webhooks": "Supprimés après la période de conservation",
                "user_data": "Anonymisées après la période de conservation"
            },
            "export_format": "JSON",
            "last_cleanup": datetime.utcnow()
        } 