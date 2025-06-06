"""Point d'entrée principal de l'application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from .routers import auth, users, notifications, webhooks, templates, stats
from .database import engine, Base

# Création des tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Notifications",
    description="API pour la gestion des notifications",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration des hôtes de confiance
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Compression GZIP
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Inclusion des routers
app.include_router(auth.router, prefix="")
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(templates.router, prefix="/templates", tags=["templates"])
app.include_router(stats.router, prefix="/stats", tags=["stats"])

@app.get("/")
def read_root():
    """Route racine."""
    return {"message": "Bienvenue sur l'API de Notifications"}

@app.get("/health")
def health_check():
    """Vérifie l'état de l'API."""
    return {"status": "ok"} 