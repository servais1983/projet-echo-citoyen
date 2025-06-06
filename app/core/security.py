from datetime import datetime, timedelta
from typing import Optional, Any, Callable
from jose import JWTError, jwt
from passlib.context import CryptContext
import re
from functools import wraps
from fastapi import Request, HTTPException, Depends
import time
from collections import defaultdict
import secrets
import unicodedata

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Stockage des requêtes par IP
request_counts = defaultdict(list)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe correspond au hash."""
    if not plain_password or not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Génère un hash sécurisé du mot de passe."""
    if not password:
        raise ValueError("Le mot de passe ne peut pas être vide")
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crée un token JWT avec des données et une durée d'expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Ajout d'un jti (JWT ID) unique pour chaque token
    to_encode.update({
        "exp": expire,
        "jti": secrets.token_hex(16),
        "iat": datetime.utcnow()
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Vérifie et décode un token JWT."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_aud": False,
                "verify_iss": False,
                "require": ["exp", "iat", "jti"],
                "verify_exp": True
            }
        )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=401,
            detail="Token invalide ou expiré"
        )

def sanitize_input(text: str) -> str:
    """Nettoie et sécurise les entrées utilisateur."""
    if not isinstance(text, str):
        return str(text)
    
    # Normalisation Unicode
    text = unicodedata.normalize('NFKC', text)
    
    # Supprimer les caractères de contrôle et les caractères Unicode spéciaux
    text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' and char not in ['\u2028', '\u2029'])
    
    # Supprimer les mots-clés JavaScript courants avant l'échappement
    js_keywords = ['alert', 'script', 'eval', 'function', 'onload', 'onerror', 'onclick']
    for keyword in js_keywords:
        text = re.sub(rf'\b{keyword}\b', '', text, flags=re.IGNORECASE)
    
    # Supprimer les balises HTML
    text = re.sub(r'<[^>]*>', '', text)
    
    # Échapper les caractères spéciaux
    text = text.replace("&", "&amp;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    
    return text

def rate_limit(limit: int, period: int):
    """Décorateur pour limiter le nombre de requêtes par période."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request = next((arg for arg in args if isinstance(arg, Request)), None)
            if not request:
                request = kwargs.get('request')
            
            if not request or getattr(request.app.state, 'testing', False):
                return await func(*args, **kwargs)

            client_ip = request.client.host
            current_time = time.time()
            
            # Nettoyer les anciennes requêtes
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if current_time - req_time < period
            ]
            
            # Vérifier la limite
            if len(request_counts[client_ip]) >= limit:
                raise HTTPException(
                    status_code=429,
                    detail="Trop de requêtes. Veuillez réessayer plus tard."
                )
            
            # Ajouter la nouvelle requête
            request_counts[client_ip].append(current_time)
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

async def get_current_user(request: Request) -> Any:
    """Récupère l'utilisateur courant depuis le token JWT."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Token manquant ou invalide"
        )
    
    token = auth_header.split(" ")[1]
    try:
        payload = verify_token(token)
        # Vérification explicite de l'expiration
        exp = payload.get("exp")
        if not exp or datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=401,
                detail="Token expiré"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )
    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Erreur d'authentification"
        )

def generate_csrf_token() -> str:
    """Génère un token CSRF."""
    return secrets.token_hex(32)

def verify_csrf_token(request: Request, token: str) -> bool:
    """Vérifie le token CSRF."""
    stored_token = request.cookies.get("csrf_token")
    if not stored_token or not token:
        return False
    return secrets.compare_digest(stored_token, token)

def check_csrf_protection(request: Request) -> None:
    """Vérifie la protection CSRF pour les requêtes POST/PUT/DELETE."""
    if request.method in ["POST", "PUT", "DELETE"]:
        csrf_token = request.headers.get("X-CSRF-Token")
        if not csrf_token or not verify_csrf_token(request, csrf_token):
            raise HTTPException(
                status_code=403,
                detail="Token CSRF manquant ou invalide"
            ) 