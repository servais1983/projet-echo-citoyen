import pytest
from fastapi import status
from app.core.config import settings

def test_api_version(client):
    """Teste la version de l'API."""
    response = client.get("/api/v1/version")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["version"] == settings.PROJECT_VERSION

def test_api_health(client):
    """Teste l'endpoint de santé de l'API."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "healthy"

def test_api_docs(client):
    """Teste la documentation de l'API."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK
    assert "swagger-ui" in response.text

def test_api_redoc(client):
    """Teste la documentation ReDoc de l'API."""
    response = client.get("/redoc")
    assert response.status_code == status.HTTP_200_OK
    assert "redoc" in response.text

def test_api_openapi(client):
    """Teste le schéma OpenAPI de l'API."""
    response = client.get("/openapi.json")
    assert response.status_code == status.HTTP_200_OK
    assert "openapi" in response.json()
    assert "info" in response.json()
    assert "paths" in response.json()

def test_api_not_found(client):
    """Teste la gestion des routes non trouvées."""
    response = client.get("/api/v1/not_found")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "detail" in response.json()

def test_api_method_not_allowed(client):
    """Teste la gestion des méthodes non autorisées."""
    response = client.put("/api/v1/health")
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert "detail" in response.json()

def test_api_validation_error(client):
    """Teste la gestion des erreurs de validation."""
    response = client.post(
        "/api/v1/notifications/",
        json={
            "title": "",  # Titre vide
            "content": "Test Content",
            "channel": "invalid_channel",  # Canal invalide
            "priority": "invalid_priority"  # Priorité invalide
        }
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()

def test_api_unauthorized(client):
    """Teste la gestion des accès non autorisés."""
    response = client.get("/api/v1/notifications/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()

def test_api_forbidden(client, test_token):
    """Teste la gestion des accès interdits."""
    # Tentative d'accès à une route admin avec un token utilisateur normal
    response = client.get(
        "/api/v1/stats/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "detail" in response.json()

def test_api_rate_limit(client):
    """Teste la limitation de taux de l'API."""
    # Envoi de 100 requêtes en succession rapide
    for _ in range(100):
        response = client.get("/api/v1/health")
    
    # La dernière requête devrait être bloquée
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert "detail" in response.json()

def test_api_cors(client):
    """Teste la configuration CORS de l'API."""
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_api_security_headers(client):
    """Teste les en-têtes de sécurité de l'API."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers

def test_api_error_handling(client):
    """Teste la gestion des erreurs de l'API."""
    # Simulation d'une erreur interne
    response = client.get("/api/v1/error")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "detail" in response.json()

def test_api_pagination(client, test_token):
    """Teste la pagination de l'API."""
    # Création de 50 notifications
    for i in range(50):
        response = client.post(
            "/api/v1/notifications/",
            json={
                "title": f"Test Notification {i}",
                "content": f"Test Content {i}",
                "channel": "email",
                "priority": "normal"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Test de la première page
    response = client.get(
        "/api/v1/notifications/?skip=0&limit=10",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10
    
    # Test de la deuxième page
    response = client.get(
        "/api/v1/notifications/?skip=10&limit=10",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 10

def test_api_filtering(client, test_token):
    """Teste le filtrage de l'API."""
    # Création de notifications avec différents statuts
    for status in ["pending", "sent", "failed"]:
        response = client.post(
            "/api/v1/notifications/",
            json={
                "title": f"Test Notification {status}",
                "content": f"Test Content {status}",
                "channel": "email",
                "priority": "normal",
                "status": status
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Test du filtrage par statut
    response = client.get(
        "/api/v1/notifications/?status=pending",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert all(notification["status"] == "pending" for notification in response.json())

def test_api_sorting(client, test_token):
    """Teste le tri de l'API."""
    # Création de notifications avec différentes dates
    for i in range(5):
        response = client.post(
            "/api/v1/notifications/",
            json={
                "title": f"Test Notification {i}",
                "content": f"Test Content {i}",
                "channel": "email",
                "priority": "normal"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Test du tri par date de création (décroissant)
    response = client.get(
        "/api/v1/notifications/?sort_by=created_at&sort_order=desc",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    notifications = response.json()
    assert len(notifications) > 1
    assert notifications[0]["created_at"] >= notifications[1]["created_at"]

def test_api_search(client, test_token):
    """Teste la recherche de l'API."""
    # Création de notifications avec différents titres
    for title in ["Test Notification", "Important Notification", "Urgent Notification"]:
        response = client.post(
            "/api/v1/notifications/",
            json={
                "title": title,
                "content": "Test Content",
                "channel": "email",
                "priority": "normal"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Test de la recherche par titre
    response = client.get(
        "/api/v1/notifications/?search=Important",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert all("Important" in notification["title"] for notification in response.json()) 