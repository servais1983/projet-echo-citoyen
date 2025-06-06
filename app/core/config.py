from pydantic import BaseSettings
from typing import List
import os
from datetime import timedelta

class Settings(BaseSettings):
    PROJECT_NAME: str = "Echo Citoyen"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Base de données
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    
    # Sécurité
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")  # Doit être défini dans les variables d'environnement
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Réduit à 15 minutes pour plus de sécurité
    
    # CORS et Hôtes
    ALLOWED_ORIGINS: List[str] = [
        "https://*.belgium.be",
        "https://*.fgov.be",
        "https://*.gov.be"
    ]
    ALLOWED_HOSTS: List[str] = [
        "*.belgium.be",
        "*.fgov.be",
        "*.gov.be"
    ]
    
    # Chiffrement
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "")  # Doit être défini dans les variables d'environnement
    
    # RGPD
    DATA_RETENTION_DAYS: int = 365  # Conservation des données pendant 1 an
    
    # Journalisation
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # Sécurité des webhooks
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")  # Doit être défini dans les variables d'environnement
    
    # Sécurité des mots de passe
    PASSWORD_MIN_LENGTH: int = 12
    PASSWORD_HISTORY_SIZE: int = 5  # Nombre de mots de passe précédents à conserver
    PASSWORD_EXPIRY_DAYS: int = 90  # Expiration des mots de passe après 90 jours
    
    # Sécurité des sessions
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_SESSIONS_PER_USER: int = 5
    SESSION_CLEANUP_INTERVAL_MINUTES: int = 60
    
    # Protection contre les attaques
    RATE_LIMIT_REQUESTS: int = 100  # Nombre maximum de requêtes par minute
    RATE_LIMIT_WINDOW_MINUTES: int = 1
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_TIMEOUT_MINUTES: int = 15
    
    # Champs sensibles à chiffrer
    SENSITIVE_FIELDS: List[str] = [
        "email",
        "phone",
        "niss",
        "iban",
        "address"
    ]
    
    # Headers de sécurité
    SECURITY_HEADERS: dict = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; frame-ancestors 'none'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
    }
    
    class Config:
        case_sensitive = True

settings = Settings() 