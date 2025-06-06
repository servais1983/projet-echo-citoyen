from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import os
import logging
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Téléchargement des ressources NLTK nécessaires
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('vader_lexicon')

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="ECHO NLP Engine")

# Modèles Pydantic
class TextAnalysisRequest(BaseModel):
    text: str

class TextAnalysisResponse(BaseModel):
    sentiment_score: float
    keywords: List[str]
    entities: List[Dict[str, Any]]
    summary: str

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

def analyze_sentiment(text: str) -> float:
    """Analyse le sentiment du texte"""
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    return scores['compound']

def extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
    """Extrait les mots-clés du texte"""
    # Tokenization
    tokens = word_tokenize(text.lower())
    
    # Suppression des stopwords
    stop_words = set(stopwords.words('french'))
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    
    # Calcul de la fréquence
    fdist = FreqDist(filtered_tokens)
    
    # Retourne les mots les plus fréquents
    return [word for word, freq in fdist.most_common(num_keywords)]

def generate_summary(text: str, max_length: int = 200) -> str:
    """Génère un résumé du texte"""
    sentences = nltk.sent_tokenize(text)
    if not sentences:
        return ""
    
    # Version simple : retourne les premières phrases jusqu'à max_length
    summary = ""
    for sentence in sentences:
        if len(summary) + len(sentence) <= max_length:
            summary += sentence + " "
        else:
            break
    
    return summary.strip()

@app.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    token: dict = Depends(verify_token)
):
    """Analyse le texte fourni"""
    try:
        # Analyse du sentiment
        sentiment_score = analyze_sentiment(request.text)
        
        # Extraction des mots-clés
        keywords = extract_keywords(request.text)
        
        # Génération du résumé
        summary = generate_summary(request.text)
        
        # Pour l'instant, on retourne une liste vide pour les entités
        # À implémenter avec un modèle NER plus tard
        entities = []
        
        return TextAnalysisResponse(
            sentiment_score=sentiment_score,
            keywords=keywords,
            entities=entities,
            summary=summary
        )
    except Exception as e:
        logger.error(f"Erreur lors de l'analyse du texte: {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'analyse du texte")

@app.get("/health")
async def health_check():
    """Vérification de l'état du service"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000) 