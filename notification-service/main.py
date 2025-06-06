from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import os
from dotenv import load_dotenv

from app.database import SessionLocal, engine
from app import models
from app import schemas
from app.dependencies import get_db, get_current_user

# Chargement des variables d'environnement
load_dotenv()

# Création des tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="ECHO Notification Service")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des services externes
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_email_notification(notification: models.Notification):
    """Envoie une notification par email."""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        raise HTTPException(status_code=500, detail="Configuration SMTP manquante")

    msg = MIMEMultipart()
    msg['From'] = SMTP_USERNAME
    msg['To'] = notification.recipient
    msg['Subject'] = notification.title

    body = f"""
    {notification.content}
    
    Pour plus d'informations, visitez le dashboard ECHO Citoyen.
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'envoi d'email: {str(e)}")

def send_slack_notification(notification: models.Notification):
    """Envoie une notification sur Slack."""
    if not SLACK_WEBHOOK_URL:
        raise HTTPException(status_code=500, detail="Configuration Slack manquante")

    message = {
        "text": f"*{notification.title}*\n{notification.content}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{notification.title}*\n{notification.content}"
                }
            }
        ]
    }

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur d'envoi Slack: {str(e)}")

def process_notification(notification: models.Notification):
    """Traite une notification selon son type."""
    if notification.channel == "email":
        send_email_notification(notification)
    elif notification.channel == "slack":
        send_slack_notification(notification)
    elif notification.channel == "both":
        send_email_notification(notification)
        send_slack_notification(notification)

@app.post("/notifications/", response_model=schemas.NotificationResponse)
async def create_notification(
    notification: schemas.NotificationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Crée une nouvelle notification."""
    db_notification = models.Notification(
        title=notification.title,
        content=notification.content,
        channel=notification.channel,
        recipient=notification.recipient,
        priority=notification.priority,
        created_by=current_user.id
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)

    # Traitement asynchrone de la notification
    background_tasks.add_task(process_notification, db_notification)

    return db_notification

@app.get("/notifications/", response_model=List[schemas.NotificationResponse])
async def get_notifications(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère la liste des notifications."""
    notifications = db.query(models.Notification).offset(skip).limit(limit).all()
    return notifications

@app.get("/notifications/{notification_id}", response_model=schemas.NotificationResponse)
async def get_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère une notification spécifique."""
    notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification non trouvée")
    return notification

@app.get("/notifications/stats", response_model=schemas.NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Récupère les statistiques des notifications."""
    total = db.query(models.Notification).count()
    by_channel = {
        "email": db.query(models.Notification).filter(models.Notification.channel == "email").count(),
        "slack": db.query(models.Notification).filter(models.Notification.channel == "slack").count(),
        "both": db.query(models.Notification).filter(models.Notification.channel == "both").count()
    }
    by_priority = {
        "low": db.query(models.Notification).filter(models.Notification.priority == "low").count(),
        "medium": db.query(models.Notification).filter(models.Notification.priority == "medium").count(),
        "high": db.query(models.Notification).filter(models.Notification.priority == "high").count()
    }
    return {
        "total_notifications": total,
        "notifications_by_channel": by_channel,
        "notifications_by_priority": by_priority
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5005) 