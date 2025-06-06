from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from .config import settings
from .logging import log_security_event

class SessionManager:
    def __init__(self):
        """Initialise le gestionnaire de sessions."""
        self.active_sessions: Dict[str, Dict] = {}

    def create_session(self, user_id: int, device_info: Dict) -> str:
        """Crée une nouvelle session utilisateur."""
        session_id = jwt.encode(
            {
                "user_id": user_id,
                "device_info": device_info,
                "created_at": datetime.utcnow().isoformat(),
                "exp": datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

        self.active_sessions[session_id] = {
            "user_id": user_id,
            "device_info": device_info,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "is_valid": True
        }

        log_security_event(
            "session_created",
            f"New session created for user {user_id}",
            "INFO"
        )
        return session_id

    def validate_session(self, session_id: str) -> bool:
        """Valide une session existante."""
        try:
            if session_id not in self.active_sessions:
                return False

            session = self.active_sessions[session_id]
            if not session["is_valid"]:
                return False

            # Vérification de l'expiration
            if datetime.utcnow() - session["created_at"] > timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
                self.invalidate_session(session_id)
                return False

            # Mise à jour de la dernière activité
            session["last_activity"] = datetime.utcnow()
            return True

        except Exception as e:
            log_security_event(
                "session_validation_error",
                str(e),
                "ERROR"
            )
            return False

    def invalidate_session(self, session_id: str) -> bool:
        """Invalide une session."""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["is_valid"] = False
            log_security_event(
                "session_invalidated",
                f"Session {session_id} invalidated",
                "INFO"
            )
            return True
        return False

    def invalidate_all_user_sessions(self, user_id: int) -> int:
        """Invalide toutes les sessions d'un utilisateur."""
        count = 0
        for session_id, session in self.active_sessions.items():
            if session["user_id"] == user_id and session["is_valid"]:
                session["is_valid"] = False
                count += 1

        log_security_event(
            "user_sessions_invalidated",
            f"Invalidated {count} sessions for user {user_id}",
            "INFO"
        )
        return count

    def get_active_sessions(self, user_id: int) -> list:
        """Récupère toutes les sessions actives d'un utilisateur."""
        return [
            {
                "session_id": session_id,
                "device_info": session["device_info"],
                "created_at": session["created_at"],
                "last_activity": session["last_activity"]
            }
            for session_id, session in self.active_sessions.items()
            if session["user_id"] == user_id and session["is_valid"]
        ]

    def cleanup_expired_sessions(self) -> int:
        """Nettoie les sessions expirées."""
        count = 0
        now = datetime.utcnow()
        for session_id, session in list(self.active_sessions.items()):
            if now - session["created_at"] > timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES):
                del self.active_sessions[session_id]
                count += 1

        if count > 0:
            log_security_event(
                "sessions_cleanup",
                f"Cleaned up {count} expired sessions",
                "INFO"
            )
        return count

# Instance globale du gestionnaire de sessions
session_manager = SessionManager() 