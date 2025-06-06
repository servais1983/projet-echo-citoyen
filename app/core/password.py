import re
import bcrypt
from typing import Tuple
from .logging import log_security_event

class PasswordManager:
    def __init__(self):
        """Initialise le gestionnaire de mots de passe."""
        # Règles de complexité des mots de passe
        self.rules = {
            "min_length": 12,
            "require_uppercase": True,
            "require_lowercase": True,
            "require_digit": True,
            "require_special": True,
            "max_repeated_chars": 3,
            "common_passwords": self._load_common_passwords()
        }

    def _load_common_passwords(self) -> set:
        """Charge la liste des mots de passe courants."""
        # Liste des mots de passe courants à éviter
        return {
            "password123", "admin123", "qwerty123",
            "welcome123", "letmein123", "12345678",
            "password", "admin", "qwerty"
        }

    def hash_password(self, password: str) -> str:
        """Hache un mot de passe avec bcrypt."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        """Vérifie un mot de passe contre son hash."""
        return bcrypt.checkpw(password.encode(), hashed.encode())

    def validate_password_strength(self, password: str) -> Tuple[bool, list]:
        """Valide la force d'un mot de passe."""
        errors = []

        # Vérification de la longueur minimale
        if len(password) < self.rules["min_length"]:
            errors.append(f"Le mot de passe doit contenir au moins {self.rules['min_length']} caractères")

        # Vérification des majuscules
        if self.rules["require_uppercase"] and not re.search(r"[A-Z]", password):
            errors.append("Le mot de passe doit contenir au moins une majuscule")

        # Vérification des minuscules
        if self.rules["require_lowercase"] and not re.search(r"[a-z]", password):
            errors.append("Le mot de passe doit contenir au moins une minuscule")

        # Vérification des chiffres
        if self.rules["require_digit"] and not re.search(r"\d", password):
            errors.append("Le mot de passe doit contenir au moins un chiffre")

        # Vérification des caractères spéciaux
        if self.rules["require_special"] and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors.append("Le mot de passe doit contenir au moins un caractère spécial")

        # Vérification des caractères répétés
        if re.search(r"(.)\1{" + str(self.rules["max_repeated_chars"]) + r",}", password):
            errors.append(f"Le mot de passe ne doit pas contenir plus de {self.rules['max_repeated_chars']} caractères identiques consécutifs")

        # Vérification des mots de passe courants
        if password.lower() in self.rules["common_passwords"]:
            errors.append("Ce mot de passe est trop courant")

        # Vérification de la complexité
        if len(set(password)) < len(password) * 0.7:
            errors.append("Le mot de passe doit être plus varié")

        is_valid = len(errors) == 0
        if not is_valid:
            log_security_event(
                "weak_password",
                f"Password validation failed: {errors}",
                "WARNING"
            )

        return is_valid, errors

    def generate_secure_password(self) -> str:
        """Génère un mot de passe sécurisé."""
        import secrets
        import string

        # Définition des caractères possibles
        chars = {
            "lowercase": string.ascii_lowercase,
            "uppercase": string.ascii_uppercase,
            "digits": string.digits,
            "special": "!@#$%^&*(),.?\":{}|<>"
        }

        # Génération du mot de passe
        password = []
        # Au moins un caractère de chaque type
        password.append(secrets.choice(chars["lowercase"]))
        password.append(secrets.choice(chars["uppercase"]))
        password.append(secrets.choice(chars["digits"]))
        password.append(secrets.choice(chars["special"]))

        # Compléter jusqu'à la longueur minimale
        all_chars = "".join(chars.values())
        password.extend(secrets.choice(all_chars) for _ in range(self.rules["min_length"] - 4))

        # Mélanger le mot de passe
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        return "".join(password_list)

    def check_password_history(self, new_password: str, password_history: list) -> bool:
        """Vérifie si le mot de passe n'a pas été utilisé récemment."""
        for old_hash in password_history:
            if self.verify_password(new_password, old_hash):
                log_security_event(
                    "password_reuse",
                    "Password has been used recently",
                    "WARNING"
                )
                return False
        return True

# Instance globale du gestionnaire de mots de passe
password_manager = PasswordManager() 