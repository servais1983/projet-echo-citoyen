"""Service d'envoi d'emails."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional
from ..models import Notification

def send_email(notification: Notification) -> bool:
    """Envoie un email."""
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("SMTP_USERNAME")
        msg['To'] = notification.recipient
        msg['Subject'] = notification.subject

        body = f"""
        {notification.content}
        
        Pour plus d'informations, visitez le dashboard ECHO Citoyen.
        """
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(os.getenv("SMTP_SERVER", "smtp.gmail.com"), int(os.getenv("SMTP_PORT", "587"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        return True
    except Exception:
        return False 