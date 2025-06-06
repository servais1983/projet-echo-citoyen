"""Configuration pour les tests."""

# Configuration de sécurité
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration de la base de données
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Configuration des services
EMAIL_SERVICE_ENABLED = True
SMS_SERVICE_ENABLED = True
PUSH_SERVICE_ENABLED = True
SLACK_SERVICE_ENABLED = True

# Configuration des limites
RATE_LIMIT_PER_MINUTE = 100
MAX_NOTIFICATIONS_PER_BATCH = 1000
MAX_WEBHOOK_RETRIES = 3
WEBHOOK_TIMEOUT = 5 