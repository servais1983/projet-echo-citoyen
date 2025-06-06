import hmac
import hashlib
import time
from typing import Optional, Dict, Any
from .config import settings
from .logging import log_security_event

class WebhookSecurity:
    def __init__(self):
        """Initialise le système de sécurité des webhooks."""
        self.secret = settings.WEBHOOK_SECRET.encode()

    def generate_signature(self, payload: str, timestamp: Optional[int] = None) -> str:
        """Génère une signature HMAC pour le payload."""
        if timestamp is None:
            timestamp = int(time.time())
        
        message = f"{timestamp}.{payload}"
        signature = hmac.new(
            self.secret,
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return f"t={timestamp},v1={signature}"

    def verify_signature(self, payload: str, signature: str, max_age: int = 300) -> bool:
        """Vérifie la signature d'un webhook."""
        try:
            # Extraction du timestamp et de la signature
            parts = dict(part.split("=") for part in signature.split(","))
            timestamp = int(parts["t"])
            received_signature = parts["v1"]

            # Vérification de l'âge de la signature
            if time.time() - timestamp > max_age:
                log_security_event(
                    "webhook_signature_expired",
                    f"Signature expired: {time.time() - timestamp}s old",
                    "WARNING"
                )
                return False

            # Calcul de la signature attendue
            expected_signature = self.generate_signature(payload, timestamp)
            expected_parts = dict(part.split("=") for part in expected_signature.split(","))

            # Comparaison des signatures
            if not hmac.compare_digest(received_signature, expected_parts["v1"]):
                log_security_event(
                    "webhook_signature_mismatch",
                    "Invalid signature",
                    "WARNING"
                )
                return False

            return True

        except Exception as e:
            log_security_event(
                "webhook_signature_error",
                str(e),
                "ERROR"
            )
            return False

    def secure_webhook_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Sécurise un payload de webhook en ajoutant des métadonnées de sécurité."""
        timestamp = int(time.time())
        payload_str = str(payload)
        signature = self.generate_signature(payload_str, timestamp)

        return {
            "payload": payload,
            "security": {
                "timestamp": timestamp,
                "signature": signature
            }
        }

    def validate_webhook_request(self, headers: Dict[str, str], body: str) -> bool:
        """Valide une requête webhook entrante."""
        # Vérification des en-têtes requis
        required_headers = ["X-Webhook-Signature", "X-Webhook-Timestamp"]
        if not all(header in headers for header in required_headers):
            log_security_event(
                "webhook_missing_headers",
                f"Missing headers: {required_headers}",
                "WARNING"
            )
            return False

        # Vérification de la signature
        signature = headers["X-Webhook-Signature"]
        if not self.verify_signature(body, signature):
            return False

        return True

# Instance globale du système de sécurité des webhooks
webhook_security = WebhookSecurity() 