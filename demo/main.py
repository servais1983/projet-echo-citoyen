from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import spacy
from transformers import pipeline

app = FastAPI(title="ECHO Demo")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration de sécurité
SECRET_KEY = "demo_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
nlp = spacy.load("fr_core_news_md")
sentiment_analyzer = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")

# Modèles de données
class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Message(BaseModel):
    content: str
    category: Optional[str] = None
    sentiment: Optional[float] = None
    priority: Optional[int] = None

# Base de données simulée
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
    }
}

# Fonctions d'authentification
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Analyse de message
def analyze_message(message: str):
    # Analyse du sentiment
    sentiment = sentiment_analyzer(message)[0]
    
    # Analyse des catégories
    doc = nlp(message)
    categories = []
    if any(word in message.lower() for word in ["route", "nid de poule", "trou"]):
        categories.append("infrastructure")
    if any(word in message.lower() for word in ["éclairage", "lampadaire", "lumière"]):
        categories.append("éclairage")
    if any(word in message.lower() for word in ["déchet", "poubelle", "ordures"]):
        categories.append("propreté")
    
    # Calcul de la priorité
    priority = 1
    if sentiment["label"] in ["1 star", "2 stars"]:
        priority = 3
    elif sentiment["label"] == "3 stars":
        priority = 2
    
    return {
        "category": categories[0] if categories else "autre",
        "sentiment": float(sentiment["score"]),
        "priority": priority
    }

# Routes
@app.post("/token", response_model=Token)
async def login_for_access_token(username: str, password: str):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Identifiants incorrects",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/analyze", response_model=Message)
async def analyze_message_endpoint(message: Message):
    analysis = analyze_message(message.content)
    return Message(
        content=message.content,
        category=analysis["category"],
        sentiment=analysis["sentiment"],
        priority=analysis["priority"]
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 