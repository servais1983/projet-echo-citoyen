from locust import HttpUser, task, between
import random
import json

class NotificationUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Authentification au démarrage"""
        response = self.client.post(
            "/token",
            data={"username": "test@example.com", "password": "testpassword"}
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def send_email_notification(self):
        """Envoi de notification par email"""
        notification = {
            "title": "Test Email",
            "content": "Test content",
            "channel": "email",
            "recipient": "recipient@example.com",
            "priority": random.choice(["low", "medium", "high"])
        }
        self.client.post(
            "/notifications/",
            json=notification,
            headers=self.headers
        )

    @task(2)
    def send_slack_notification(self):
        """Envoi de notification Slack"""
        notification = {
            "title": "Test Slack",
            "content": "Test content",
            "channel": "slack",
            "recipient": "#test-channel",
            "priority": random.choice(["low", "medium", "high"])
        }
        self.client.post(
            "/notifications/",
            json=notification,
            headers=self.headers
        )

    @task(1)
    def send_sms_notification(self):
        """Envoi de notification SMS"""
        notification = {
            "title": "Test SMS",
            "content": "Test content",
            "channel": "sms",
            "recipient": "+33612345678",
            "priority": random.choice(["low", "medium", "high"])
        }
        self.client.post(
            "/notifications/",
            json=notification,
            headers=self.headers
        )

    @task(2)
    def get_notifications(self):
        """Récupération de la liste des notifications"""
        self.client.get(
            "/notifications/",
            headers=self.headers
        )

    @task(1)
    def get_stats(self):
        """Récupération des statistiques"""
        self.client.get(
            "/notifications/stats",
            headers=self.headers
        )

    @task(1)
    def send_batch_notifications(self):
        """Envoi d'un lot de notifications"""
        batch = {
            "notifications": [
                {
                    "title": f"Test Batch {i}",
                    "content": "Test content",
                    "channel": random.choice(["email", "slack", "sms"]),
                    "recipient": "recipient@example.com",
                    "priority": random.choice(["low", "medium", "high"])
                }
                for i in range(5)
            ]
        }
        self.client.post(
            "/notifications/batch",
            json=batch,
            headers=self.headers
        ) 