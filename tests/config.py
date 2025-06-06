from datetime import datetime, timedelta
from typing import Optional

# Configuration de la base de données de test
TEST_DATABASE_URL = "sqlite:///./test.db"

# Configuration JWT
SECRET_KEY = "test_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuration des services
SMTP_HOST = "smtp.test.com"
SMTP_PORT = 587
SMTP_USER = "test@test.com"
SMTP_PASSWORD = "test_password"

SMS_API_KEY = "test_sms_api_key"
SMS_API_SECRET = "test_sms_api_secret"

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/test/test/test"

# Configuration des limites
RATE_LIMIT_PER_MINUTE = 60
MAX_NOTIFICATIONS_PER_BATCH = 100

# Configuration des webhooks
WEBHOOK_SECRET = "test_webhook_secret"
WEBHOOK_TIMEOUT = 5  # secondes

# Configuration des templates
DEFAULT_TEMPLATE_LANGUAGE = "fr" 