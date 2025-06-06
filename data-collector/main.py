from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON, Text, Boolean, Enum, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import logging
from typing import List, Optional
from pydantic import BaseModel
import httpx
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration de la base de données
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@db:5432/echo_data")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Modèles de base de données
class DataEntry(Base):
    __tablename__ = "data_entries"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    category = Column(String, index=True)
    content = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Integer, default=0)
    sentiment_score = Column(Integer, nullable=True)
    keywords = Column(JSON, nullable=True)

# Modèles Pydantic
class DataEntryCreate(BaseModel):
    source: str
    category: str
    content: dict
    metadata: Optional[dict] = None

class DataEntryResponse(BaseModel):
    id: int
    source: str
    category: str
    content: dict
    metadata: Optional[dict]
    created_at: datetime
    processed: int
    sentiment_score: Optional[int]
    keywords: Optional[List[str]]

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ECHO Data Collector")

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

async def process_data(entry_id: int, db: Session):
    """Traitement asynchrone des données"""
    try:
        entry = db.query(DataEntry).filter(DataEntry.id == entry_id).first()
        if not entry:
            return

        # Appel au service NLP pour l'analyse
        nlp_service_url = os.getenv("NLP_SERVICE_URL", "http://nlp-engine:5000")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{nlp_service_url}/analyze",
                json={"text": json.dumps(entry.content)}
            )
            if response.status_code == 200:
                analysis = response.json()
                entry.sentiment_score = analysis.get("sentiment_score")
                entry.keywords = analysis.get("keywords")
                entry.processed = 1
                db.commit()

    except Exception as e:
        logger.error(f"Erreur lors du traitement des données: {e}")
        entry.processed = -1
        db.commit()

@app.post("/collect", response_model=DataEntryResponse)
async def collect_data(
    data: DataEntryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Collecte de nouvelles données"""
    db_entry = DataEntry(**data.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)

    # Lancement du traitement en arrière-plan
    background_tasks.add_task(process_data, db_entry.id, db)

    return db_entry

@app.get("/data", response_model=List[DataEntryResponse])
async def get_data(
    source: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Récupération des données collectées"""
    query = db.query(DataEntry)
    
    if source:
        query = query.filter(DataEntry.source == source)
    if category:
        query = query.filter(DataEntry.category == category)
    
    return query.order_by(DataEntry.created_at.desc()).limit(limit).all()

@app.get("/stats")
async def get_stats(
    db: Session = Depends(get_db),
    token: dict = Depends(verify_token)
):
    """Statistiques sur les données collectées"""
    total_entries = db.query(DataEntry).count()
    processed_entries = db.query(DataEntry).filter(DataEntry.processed == 1).count()
    error_entries = db.query(DataEntry).filter(DataEntry.processed == -1).count()
    
    sources = db.query(DataEntry.source, func.count(DataEntry.id)).group_by(DataEntry.source).all()
    categories = db.query(DataEntry.category, func.count(DataEntry.id)).group_by(DataEntry.category).all()
    
    return {
        "total_entries": total_entries,
        "processed_entries": processed_entries,
        "error_entries": error_entries,
        "sources": dict(sources),
        "categories": dict(categories)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5002) 