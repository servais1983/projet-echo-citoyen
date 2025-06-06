"""Service d'envoi de messages Slack."""

import requests
import os
from typing import Optional
from ..models import Notification

def send_message(notification: Notification) -> bool:
    """Envoie un message Slack."""
    try:
        message = {
            "text": f"*{notification.subject}*\n{notification.content}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{notification.subject}*\n{notification.content}"
                    }
                }
            ]
        }

        response = requests.post(os.getenv("SLACK_WEBHOOK_URL"), json=message)
        response.raise_for_status()
        return True
    except Exception:
        return False 