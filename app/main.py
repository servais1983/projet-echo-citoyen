from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from app.routers import router
from .api.endpoints import chat
import time
from collections import defaultdict
from .core.security import generate_csrf_token, check_csrf_protection

app = FastAPI(title="Echo Citoyen API")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de sécurité
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Vérification CSRF pour les requêtes POST/PUT/DELETE
        try:
            check_csrf_protection(request)
        except Exception as e:
            return JSONResponse(
                status_code=403,
                content={"detail": str(e)}
            )
            
        response = await call_next(request)
        
        # En-têtes de sécurité de base
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Politique de sécurité du contenu renforcée
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self';"
        )
        
        # Protection contre le clickjacking
        response.headers["X-Frame-Options"] = "DENY"
        
        # Protection contre le MIME-type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Protection contre le XSS
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Protection contre le referrer leakage
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Protection contre le feature policy
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Middleware de sécurité des hôtes
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # À restreindre en production
)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 2, period: int = 1, enabled: bool = True):
        super().__init__(app)
        self.limit = limit
        self.period = period
        self.requests = defaultdict(list)
        self.enabled = enabled

    async def dispatch(self, request: Request, call_next):
        if not self.enabled or getattr(request.app.state, 'testing', False):
            return await call_next(request)
            
        client_ip = request.client.host
        now = time.time()
        
        # Nettoyage des anciennes requêtes
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < self.period]
        
        # Vérification de la limite
        if len(self.requests[client_ip]) >= self.limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Trop de requêtes. Veuillez réessayer plus tard."}
            )
            
        # Ajout de la nouvelle requête
        self.requests[client_ip].append(now)
        
        # Génération du token CSRF pour les requêtes POST/PUT/DELETE
        if request.method in ["POST", "PUT", "DELETE"]:
            csrf_token = generate_csrf_token()
            response = await call_next(request)
            response.set_cookie(
                key="csrf_token",
                value=csrf_token,
                httponly=True,
                secure=True,
                samesite="strict"
            )
            return response
            
        return await call_next(request)

# Ajout du middleware avec désactivation possible en test
enabled_rate_limit = not getattr(app.state, 'testing', False)
app.add_middleware(RateLimitMiddleware, limit=2, period=1, enabled=enabled_rate_limit)

# Inclusion du router principal
app.include_router(router)
app.include_router(chat.router, prefix="/api", tags=["chat"]) 