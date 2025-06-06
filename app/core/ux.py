from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .config import settings
from .logging import log_security_event
from .session import session_manager
from .password import password_manager

class UXManager:
    def __init__(self):
        """Initialise le gestionnaire d'expérience utilisateur."""
        self.login_attempts: Dict[str, Dict] = {}
        self.remembered_devices: Dict[int, Dict] = {}

    def handle_login_attempt(self, email: str, success: bool) -> Dict[str, Any]:
        """Gère une tentative de connexion avec une approche progressive."""
        now = datetime.utcnow()
        
        if email not in self.login_attempts:
            self.login_attempts[email] = {
                "attempts": 0,
                "last_attempt": now,
                "locked_until": None
            }

        attempt_data = self.login_attempts[email]
        
        if success:
            # Réinitialisation des tentatives en cas de succès
            attempt_data["attempts"] = 0
            attempt_data["locked_until"] = None
            return {"status": "success", "message": "Connexion réussie"}

        # Incrémentation des tentatives
        attempt_data["attempts"] += 1
        attempt_data["last_attempt"] = now

        # Calcul du délai d'attente progressif
        if attempt_data["attempts"] >= settings.MAX_LOGIN_ATTEMPTS:
            wait_time = min(
                settings.LOGIN_TIMEOUT_MINUTES * (attempt_data["attempts"] - settings.MAX_LOGIN_ATTEMPTS + 1),
                60  # Maximum 60 minutes
            )
            attempt_data["locked_until"] = now + timedelta(minutes=wait_time)
            
            return {
                "status": "locked",
                "message": f"Compte temporairement verrouillé. Réessayez dans {wait_time} minutes.",
                "wait_time": wait_time
            }

        remaining_attempts = settings.MAX_LOGIN_ATTEMPTS - attempt_data["attempts"]
        return {
            "status": "failed",
            "message": f"Identifiants incorrects. Il vous reste {remaining_attempts} tentative(s).",
            "remaining_attempts": remaining_attempts
        }

    def remember_device(self, user_id: int, device_info: Dict[str, Any]) -> str:
        """Mémorise un appareil de confiance."""
        if user_id not in self.remembered_devices:
            self.remembered_devices[user_id] = {}

        device_id = f"{device_info.get('browser', '')}_{device_info.get('os', '')}"
        self.remembered_devices[user_id][device_id] = {
            "info": device_info,
            "last_used": datetime.utcnow(),
            "trust_level": "high"
        }

        return device_id

    def is_trusted_device(self, user_id: int, device_info: Dict[str, Any]) -> bool:
        """Vérifie si un appareil est de confiance."""
        if user_id not in self.remembered_devices:
            return False

        device_id = f"{device_info.get('browser', '')}_{device_info.get('os', '')}"
        return device_id in self.remembered_devices[user_id]

    def get_security_level(self, user_id: int, device_info: Dict[str, Any]) -> str:
        """Détermine le niveau de sécurité requis en fonction du contexte."""
        if self.is_trusted_device(user_id, device_info):
            return "standard"
        return "enhanced"

    def suggest_password_change(self, user_id: int, last_change: datetime) -> bool:
        """Suggère un changement de mot de passe si nécessaire."""
        if not last_change:
            return True

        days_since_change = (datetime.utcnow() - last_change).days
        return days_since_change >= settings.PASSWORD_EXPIRY_DAYS

    def get_session_duration(self, user_id: int, device_info: Dict[str, Any]) -> int:
        """Détermine la durée de session en fonction du contexte."""
        if self.is_trusted_device(user_id, device_info):
            return settings.SESSION_TIMEOUT_MINUTES * 2
        return settings.SESSION_TIMEOUT_MINUTES

    def cleanup_old_data(self):
        """Nettoie les anciennes données pour maintenir les performances."""
        now = datetime.utcnow()
        
        # Nettoyage des tentatives de connexion
        for email, data in list(self.login_attempts.items()):
            if data["locked_until"] and now > data["locked_until"]:
                del self.login_attempts[email]

        # Nettoyage des appareils mémorisés
        for user_id, devices in list(self.remembered_devices.items()):
            for device_id, device_data in list(devices.items()):
                if (now - device_data["last_used"]).days > 90:  # 3 mois
                    del devices[device_id]
            if not devices:
                del self.remembered_devices[user_id]

    def get_security_recommendations(self, user_id: int) -> Dict[str, Any]:
        """Fournit des recommandations de sécurité personnalisées."""
        active_sessions = session_manager.get_active_sessions(user_id)
        
        return {
            "active_sessions": len(active_sessions),
            "recommendations": [
                "Activez l'authentification à deux facteurs" if len(active_sessions) > 1 else None,
                "Vérifiez vos appareils connectés" if len(active_sessions) > 2 else None,
                "Mettez à jour votre mot de passe" if self.suggest_password_change(user_id, None) else None
            ]
        }

# Instance globale du gestionnaire d'expérience utilisateur
ux_manager = UXManager() 