from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Boolean, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import logging
from typing import List, Optional
from pydantic import BaseModel
import httpx
import json
import enum

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./alerts.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Énumérations
class AlertSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(enum.Enum):
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

# Modèles de base de données
class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    severity = Column(Enum(AlertSeverity))
    status = Column(Enum(AlertStatus), default=AlertStatus.NEW)
    source = Column(String, index=True)
    category = Column(String, index=True)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    assigned_to = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

# Modèles Pydantic
class AlertCreate(BaseModel):
    title: str
    description: str
    severity: AlertSeverity
    source: str
    category: str
    metadata: Optional[dict] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    assigned_to: Optional[str] = None
    is_active: Optional[bool] = None

class AlertResponse(BaseModel):
    id: int
    title: str
    description: str
    severity: AlertSeverity
    status: AlertStatus
    source: str
    category: str
    metadata: Optional[dict]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    assigned_to: Optional[str]
    is_active: bool

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ECHO Alert System")

# Dépendances
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def verify_token(token: str = Depends(oauth2_scheme)):
    """Vérifie le token JWT avec le service d'authentification"""
    auth_service_url = os.getenv("AUTH_SERVICE_URL", "http://auth-service:5003")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{auth_service_url}/verify",
                json={"token": token}
            )
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=401, detail="Token invalide")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du token: {e}")
            raise HTTPException(status_code=500, detail="Erreur de service")

async def notify_alert(alert: Alert):
    """Notification des alertes"""
    # TODO: Implémenter l'envoi de notifications (email, SMS, etc.)
    logger.info(f"Nouvelle alerte créée: {alert.title}")

@app.post("/alerts", response_model=AlertResponse)
async def create_alert(
    alert: AlertCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Création d'une nouvelle alerte"""
    db_alert = Alert(**alert.dict())
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # Notification en arrière-plan
    background_tasks.add_task(notify_alert, db_alert)

    return db_alert

@app.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    status: Optional[AlertStatus] = None,
    severity: Optional[AlertSeverity] = None,
    source: Optional[str] = None,
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Récupération des alertes"""
    query = db.query(Alert)
    
    if status:
        query = query.filter(Alert.status == status)
    if severity:
        query = query.filter(Alert.severity == severity)
    if source:
        query = query.filter(Alert.source == source)
    if category:
        query = query.filter(Alert.category == category)
    if is_active is not None:
        query = query.filter(Alert.is_active == is_active)
    
    return query.order_by(Alert.created_at.desc()).limit(limit).all()

@app.patch("/alerts/{alert_id}", response_model=AlertResponse)
async def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Mise à jour d'une alerte"""
    db_alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not db_alert:
        raise HTTPException(status_code=404, detail="Alerte non trouvée")

    update_data = alert_update.dict(exclude_unset=True)
    if "status" in update_data:
        if update_data["status"] == AlertStatus.RESOLVED:
            update_data["resolved_at"] = datetime.utcnow()

    for key, value in update_data.items():
        setattr(db_alert, key, value)

    db.commit()
    db.refresh(db_alert)
    return db_alert

@app.get("/alerts/stats")
async def get_alert_stats(
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Statistiques sur les alertes"""
    total_alerts = db.query(Alert).count()
    active_alerts = db.query(Alert).filter(Alert.is_active == True).count()
    
    severity_stats = db.query(
        Alert.severity,
        func.count(Alert.id)
    ).group_by(Alert.severity).all()
    
    status_stats = db.query(
        Alert.status,
        func.count(Alert.id)
    ).group_by(Alert.status).all()
    
    return {
        "total_alerts": total_alerts,
        "active_alerts": active_alerts,
        "severity_distribution": dict(severity_stats),
        "status_distribution": dict(status_stats)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001) 