import re
from typing import Any, Dict, List, Optional
from .logging import log_security_event

class InputValidator:
    def __init__(self):
        """Initialise le validateur d'entrées."""
        # Patterns pour la validation
        self.patterns = {
            "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
            "url": r"^https?:\/\/([\w\d\-]+\.)+[\w\d\-]+(\/[\w\d\-\.\/]*)?$",
            "phone": r"^\+?[0-9]{8,15}$",
            "postal_code": r"^[0-9]{4}$",  # Code postal belge
            "niss": r"^[0-9]{11}$",  # Numéro de sécurité sociale belge
            "iban": r"^BE[0-9]{14}$"  # IBAN belge
        }

    def sanitize_string(self, value: str) -> str:
        """Nettoie une chaîne de caractères."""
        # Suppression des caractères dangereux
        value = re.sub(r'[<>]', '', value)
        # Échappement des caractères spéciaux
        value = re.sub(r'[&]', '&amp;', value)
        value = re.sub(r'["]', '&quot;', value)
        value = re.sub(r"[']", '&#x27;', value)
        return value

    def validate_email(self, email: str) -> bool:
        """Valide une adresse email."""
        if not re.match(self.patterns["email"], email):
            log_security_event(
                "invalid_email",
                f"Invalid email format: {email}",
                "WARNING"
            )
            return False
        return True

    def validate_url(self, url: str) -> bool:
        """Valide une URL."""
        if not re.match(self.patterns["url"], url):
            log_security_event(
                "invalid_url",
                f"Invalid URL format: {url}",
                "WARNING"
            )
            return False
        return True

    def validate_phone(self, phone: str) -> bool:
        """Valide un numéro de téléphone."""
        if not re.match(self.patterns["phone"], phone):
            log_security_event(
                "invalid_phone",
                f"Invalid phone format: {phone}",
                "WARNING"
            )
            return False
        return True

    def validate_postal_code(self, postal_code: str) -> bool:
        """Valide un code postal belge."""
        if not re.match(self.patterns["postal_code"], postal_code):
            log_security_event(
                "invalid_postal_code",
                f"Invalid postal code format: {postal_code}",
                "WARNING"
            )
            return False
        return True

    def validate_niss(self, niss: str) -> bool:
        """Valide un numéro de sécurité sociale belge."""
        if not re.match(self.patterns["niss"], niss):
            log_security_event(
                "invalid_niss",
                f"Invalid NISS format: {niss}",
                "WARNING"
            )
            return False
        return True

    def validate_iban(self, iban: str) -> bool:
        """Valide un numéro IBAN belge."""
        if not re.match(self.patterns["iban"], iban):
            log_security_event(
                "invalid_iban",
                f"Invalid IBAN format: {iban}",
                "WARNING"
            )
            return False
        return True

    def validate_dict(self, data: Dict[str, Any], rules: Dict[str, str]) -> Dict[str, List[str]]:
        """Valide un dictionnaire selon des règles spécifiées."""
        errors = {}
        for field, rule in rules.items():
            if field not in data:
                errors[field] = ["Champ requis"]
                continue

            value = data[field]
            if rule in self.patterns:
                if not re.match(self.patterns[rule], str(value)):
                    errors[field] = [f"Format invalide pour {rule}"]
            elif rule == "required" and not value:
                errors[field] = ["Champ requis"]
            elif rule == "string" and not isinstance(value, str):
                errors[field] = ["Doit être une chaîne de caractères"]
            elif rule == "integer" and not isinstance(value, int):
                errors[field] = ["Doit être un nombre entier"]
            elif rule == "float" and not isinstance(value, float):
                errors[field] = ["Doit être un nombre décimal"]

        if errors:
            log_security_event(
                "validation_errors",
                f"Validation errors: {errors}",
                "WARNING"
            )

        return errors

    def sanitize_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Nettoie toutes les chaînes de caractères dans un dictionnaire."""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = self.sanitize_string(value)
            elif isinstance(value, dict):
                sanitized[key] = self.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [
                    self.sanitize_dict(item) if isinstance(item, dict)
                    else self.sanitize_string(item) if isinstance(item, str)
                    else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        return sanitized

# Instance globale du validateur d'entrées
input_validator = InputValidator() 