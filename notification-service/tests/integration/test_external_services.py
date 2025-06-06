import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app.services.email_service import send_email
from app.services.slack_service import send_message
from app.services.sms_service import send_sms
from app.models import Notification, NotificationChannel

class TestExternalServices:
    @pytest.fixture
    def mock_smtp(self):
        with patch('smtplib.SMTP') as mock:
            mock_instance = MagicMock()
            mock.return_value.__enter__.return_value = mock_instance
            yield mock_instance

    @pytest.fixture
    def mock_slack_webhook(self):
        with patch('requests.post') as mock:
            mock.return_value.status_code = 200
            yield mock

    @pytest.fixture
    def mock_twilio(self):
        with patch('twilio.rest.Client') as mock:
            mock_instance = MagicMock()
            mock.return_value = mock_instance
            yield mock_instance

    def test_email_service_success(self, mock_smtp):
        """Test de l'envoi d'email réussi"""
        notification = Notification(
            title="Test Email",
            content="Test content",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority="high"
        )
        
        result = send_email(notification)
        assert result is True
        
        # Vérifier que les méthodes SMTP ont été appelées correctement
        mock_smtp.sendmail.assert_called_once()
        mock_smtp.quit.assert_called_once()

    def test_email_service_failure(self, mock_smtp):
        """Test de l'échec d'envoi d'email"""
        mock_smtp.sendmail.side_effect = Exception("SMTP error")
        
        notification = Notification(
            title="Test Email",
            content="Test content",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority="high"
        )
        
        result = send_email(notification)
        assert result is False

    def test_slack_service_success(self, mock_slack_webhook):
        """Test de l'envoi de message Slack réussi"""
        notification = Notification(
            title="Test Slack",
            content="Test content",
            channel=NotificationChannel.SLACK,
            recipient="#test-channel",
            priority="medium"
        )
        
        result = send_message(notification)
        assert result is True
        
        # Vérifier que la requête a été envoyée avec les bons paramètres
        mock_slack_webhook.assert_called_once()
        call_args = mock_slack_webhook.call_args
        assert "text" in call_args[1]["json"]

    def test_slack_service_failure(self, mock_slack_webhook):
        """Test de l'échec d'envoi de message Slack"""
        mock_slack_webhook.return_value.status_code = 400
        
        notification = Notification(
            title="Test Slack",
            content="Test content",
            channel=NotificationChannel.SLACK,
            recipient="#test-channel",
            priority="medium"
        )
        
        result = send_message(notification)
        assert result is False

    def test_sms_service_success(self, mock_twilio):
        """Test de l'envoi de SMS réussi"""
        notification = Notification(
            title="Test SMS",
            content="Test content",
            channel=NotificationChannel.SMS,
            recipient="+33612345678",
            priority="high"
        )
        
        mock_twilio.messages.create.return_value.sid = "test_sid"
        
        result = send_sms(notification)
        assert result is True
        
        # Vérifier que le message a été créé avec les bons paramètres
        mock_twilio.messages.create.assert_called_once()
        call_args = mock_twilio.messages.create.call_args
        assert call_args[1]["to"] == "+33612345678"

    def test_sms_service_failure(self, mock_twilio):
        """Test de l'échec d'envoi de SMS"""
        mock_twilio.messages.create.side_effect = Exception("Twilio error")
        
        notification = Notification(
            title="Test SMS",
            content="Test content",
            channel=NotificationChannel.SMS,
            recipient="+33612345678",
            priority="high"
        )
        
        result = send_sms(notification)
        assert result is False

    def test_rate_limiting(self, mock_smtp):
        """Test de la limitation de taux pour les services externes"""
        notifications = [
            Notification(
                title=f"Test Email {i}",
                content="Test content",
                channel=NotificationChannel.EMAIL,
                recipient="test@example.com",
                priority="high"
            )
            for i in range(5)
        ]
        
        # Envoyer plusieurs notifications rapidement
        results = [send_email(notification) for notification in notifications]
        
        # Vérifier que toutes les notifications ont été envoyées
        assert all(results)
        
        # Vérifier que le nombre d'appels SMTP correspond au nombre de notifications
        assert mock_smtp.sendmail.call_count == 5

    def test_retry_mechanism(self, mock_smtp):
        """Test du mécanisme de réessai pour les services externes"""
        # Simuler un échec suivi d'un succès
        mock_smtp.sendmail.side_effect = [Exception("SMTP error"), None]
        
        notification = Notification(
            title="Test Email",
            content="Test content",
            channel=NotificationChannel.EMAIL,
            recipient="test@example.com",
            priority="high"
        )
        
        # Premier essai
        result1 = send_email(notification)
        assert result1 is False
        
        # Deuxième essai
        result2 = send_email(notification)
        assert result2 is True
        
        # Vérifier que sendmail a été appelé deux fois
        assert mock_smtp.sendmail.call_count == 2 