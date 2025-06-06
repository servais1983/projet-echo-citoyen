import logging
import os
from datetime import datetime
from .config import settings

def setup_logging():
    """Configure la journalisation de l'application."""
    # Création du dossier de logs s'il n'existe pas
    os.makedirs("logs", exist_ok=True)
    
    # Configuration du logging
    logging.basicConfig(
        filename=settings.LOG_FILE,
        level=getattr(logging, settings.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Ajout d'un handler pour la console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Ajout du handler à la racine du logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)

def log_access(user_id: int, action: str, resource: str, status: str):
    """Journalise un accès à une ressource."""
    logging.info(
        f"Access Log - User: {user_id}, Action: {action}, "
        f"Resource: {resource}, Status: {status}"
    )

def log_security_event(event_type: str, details: str, severity: str = "INFO"):
    """Journalise un événement de sécurité."""
    logging.warning(
        f"Security Event - Type: {event_type}, Details: {details}, "
        f"Severity: {severity}"
    )

def log_data_access(user_id: int, data_type: str, action: str):
    """Journalise un accès aux données (conformité RGPD)."""
    logging.info(
        f"Data Access Log - User: {user_id}, Data Type: {data_type}, "
        f"Action: {action}, Timestamp: {datetime.utcnow()}"
    )

def log_error(error: Exception, context: dict = None):
    """Journalise une erreur avec son contexte."""
    logging.error(
        f"Error: {str(error)}, Context: {context if context else 'No context'}"
    ) 