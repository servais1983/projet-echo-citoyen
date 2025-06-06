from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from .config import settings

class Encryption:
    def __init__(self):
        """Initialise le système de chiffrement."""
        self.key = self._derive_key(settings.ENCRYPTION_KEY)
        self.cipher_suite = Fernet(self.key)

    def _derive_key(self, password: str) -> bytes:
        """Dérive une clé de chiffrement à partir du mot de passe."""
        salt = b'echo_citoyen_salt'  # À remplacer par un sel unique et sécurisé
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """Chiffre une chaîne de caractères."""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"Erreur lors du chiffrement: {str(e)}")

    def decrypt(self, encrypted_data: str) -> str:
        """Déchiffre une chaîne de caractères chiffrée."""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Erreur lors du déchiffrement: {str(e)}")

    def encrypt_dict(self, data: dict) -> dict:
        """Chiffre les valeurs sensibles d'un dictionnaire."""
        encrypted_dict = {}
        for key, value in data.items():
            if isinstance(value, str) and key in settings.SENSITIVE_FIELDS:
                encrypted_dict[key] = self.encrypt(value)
            else:
                encrypted_dict[key] = value
        return encrypted_dict

    def decrypt_dict(self, data: dict) -> dict:
        """Déchiffre les valeurs sensibles d'un dictionnaire."""
        decrypted_dict = {}
        for key, value in data.items():
            if isinstance(value, str) and key in settings.SENSITIVE_FIELDS:
                decrypted_dict[key] = self.decrypt(value)
            else:
                decrypted_dict[key] = value
        return decrypted_dict

# Instance globale du système de chiffrement
encryption = Encryption() 