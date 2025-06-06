"""Service d'envoi de SMS."""

from twilio.rest import Client
import os
from typing import Optional
from ..models import Notification

def send_sms(notification: Notification) -> bool:
    """Envoie un SMS."""
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )

        message = client.messages.create(
            body=f"{notification.subject}\n{notification.content}",
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=notification.recipient
        )
        return True
    except Exception:
        return False 