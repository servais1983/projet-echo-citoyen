from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
import httpx
import os
from typing import Dict, Any
import logging
from prometheus_client import Counter, Histogram
import time

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Métriques Prometheus
REQUEST_COUNT = Counter('http_requests_total', 'Total des requêtes HTTP', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'Latence des requêtes HTTP')

app = FastAPI(title="ECHO API Gateway")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# URLs des services
SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:5003"),
    "chatbot": os.getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:5000"),
    "nlp": os.getenv("NLP_SERVICE_URL", "http://nlp-engine:5000"),
    "dashboard": os.getenv("DASHBOARD_SERVICE_URL", "http://dashboard-service:3000"),
    "alert": os.getenv("ALERT_SERVICE_URL", "http://alert-system:5001"),
    "data": os.getenv("DATA_COLLECTOR_URL", "http://data-collector:5002")
}

async def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Vérifie le token JWT avec le service d'authentification"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['auth']}/verify",
                json={"token": token}
            )
            if response.status_code == 200:
                return response.json()
            raise HTTPException(status_code=401, detail="Token invalide")
        except Exception as e:
            logger.error(f"Erreur lors de la vérification du token: {e}")
            raise HTTPException(status_code=500, detail="Erreur de service")

@app.middleware("http")
async def monitor_requests(request, call_next):
    """Middleware pour monitorer les requêtes"""
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.observe(duration)
    
    return response

@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé"""
    return {"status": "healthy"}

@app.post("/chat")
async def chat_endpoint(
    message: Dict[str, Any],
    token: Dict[str, Any] = Depends(verify_token)
):
    """Endpoint pour le chat"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['chatbot']}/chat",
                json=message,
                headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au service chatbot: {e}")
            raise HTTPException(status_code=500, detail="Erreur de service")

@app.get("/dashboard")
async def dashboard_endpoint(token: Dict[str, Any] = Depends(verify_token)):
    """Endpoint pour le tableau de bord"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SERVICES['dashboard']}/data",
                headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au service dashboard: {e}")
            raise HTTPException(status_code=500, detail="Erreur de service")

@app.post("/alert")
async def alert_endpoint(
    alert: Dict[str, Any],
    token: Dict[str, Any] = Depends(verify_token)
):
    """Endpoint pour les alertes"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SERVICES['alert']}/alert",
                json=alert,
                headers={"Authorization": f"Bearer {token['access_token']}"}
            )
            return response.json()
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au service d'alerte: {e}")
            raise HTTPException(status_code=500, detail="Erreur de service")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 