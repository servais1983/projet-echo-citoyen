# Documentation des API ECHO Citoyen

## Vue d'ensemble

Le projet ECHO Citoyen expose plusieurs API REST documentées avec OpenAPI (Swagger). Cette documentation décrit comment accéder et utiliser ces API.

## Services disponibles

### 1. Service d'Authentification (`auth-service`)
- Port : 5003
- Documentation : `auth-service/openapi.yaml`
- Endpoints principaux :
  - `/register` : Création de compte
  - `/token` : Authentification
  - `/verify` : Vérification de token
  - `/users/me` : Informations utilisateur

### 2. Service d'Alertes (`alert-system`)
- Port : 5001
- Documentation : `alert-system/openapi.yaml`
- Endpoints principaux :
  - `/alerts` : Gestion des alertes
  - `/alerts/stats` : Statistiques
  - `/alerts/{id}/resolve` : Résolution d'alerte

### 3. Service de Collecte de Données (`data-collector`)
- Port : 5002
- Documentation : `data-collector/openapi.yaml`
- Endpoints principaux :
  - `/sources` : Gestion des sources
  - `/tasks` : Gestion des tâches
  - `/stats` : Statistiques de collecte

### 4. Service NLP (`nlp-service`)
- Port : 5004
- Documentation : `nlp-service/openapi.yaml`
- Endpoints principaux :
  - `/analyze/sentiment` : Analyse de sentiment
  - `/analyze/entities` : Extraction d'entités
  - `/analyze/topics` : Extraction de sujets
  - `/analyze/batch` : Analyse par lot

## Utilisation de la documentation

### Visualisation avec Swagger UI

1. Installer Swagger UI :
   ```bash
   docker run -p 8080:8080 -e SWAGGER_JSON=/api/openapi.yaml -v $(pwd):/api swaggerapi/swagger-ui
   ```

2. Accéder à l'interface :
   - Ouvrir `http://localhost:8080` dans votre navigateur
   - Sélectionner le fichier OpenAPI à visualiser

### Génération de code client

#### Python

1. Installer le générateur :
   ```bash
   pip install openapi-generator-cli
   ```

2. Générer le client :
   ```bash
   openapi-generator generate -i auth-service/openapi.yaml -g python -o clients/python/auth
   ```

#### JavaScript/TypeScript

1. Installer le générateur :
   ```bash
   npm install @openapitools/openapi-generator-cli -g
   ```

2. Générer le client :
   ```bash
   openapi-generator-cli generate -i auth-service/openapi.yaml -g typescript-fetch -o clients/typescript/auth
   ```

## Authentification

Toutes les API utilisent l'authentification JWT :

1. Obtenir un token :
   ```bash
   curl -X POST http://localhost:5003/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=user@example.com&password=password"
   ```

2. Utiliser le token :
   ```bash
   curl -X GET http://localhost:5001/alerts \
     -H "Authorization: Bearer <token>"
   ```

## Exemples d'utilisation

### Créer une alerte

```python
import requests

# Authentification
auth_response = requests.post(
    "http://localhost:5003/token",
    data={"username": "user@example.com", "password": "password"}
)
token = auth_response.json()["access_token"]

# Créer une alerte
headers = {"Authorization": f"Bearer {token}"}
alert_data = {
    "title": "Nouvelle alerte",
    "description": "Description de l'alerte",
    "severity": "high",
    "category": "security"
}
response = requests.post(
    "http://localhost:5001/alerts",
    json=alert_data,
    headers=headers
)
```

### Analyser un texte

```python
import requests

# Authentification
auth_response = requests.post(
    "http://localhost:5003/token",
    data={"username": "user@example.com", "password": "password"}
)
token = auth_response.json()["access_token"]

# Analyser un texte
headers = {"Authorization": f"Bearer {token}"}
text_data = {
    "text": "Le service fonctionne très bien aujourd'hui.",
    "language": "fr"
}
response = requests.post(
    "http://localhost:5004/analyze/sentiment",
    json=text_data,
    headers=headers
)
```

## Bonnes pratiques

1. **Gestion des erreurs**
   - Toujours vérifier les codes de réponse HTTP
   - Gérer les erreurs 401 (non authentifié) et 403 (non autorisé)
   - Implémenter une logique de retry pour les erreurs 5xx

2. **Performance**
   - Utiliser le batch processing quand possible
   - Mettre en cache les tokens JWT
   - Implémenter le rate limiting côté client

3. **Sécurité**
   - Ne jamais stocker les tokens en clair
   - Utiliser HTTPS en production
   - Valider les données avant envoi

## Support

Pour toute question ou problème :
1. Consulter la documentation OpenAPI
2. Vérifier les logs des services
3. Contacter l'équipe de développement 