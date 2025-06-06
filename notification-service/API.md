# Documentation de l'API de Notifications

## Introduction

L'API de notifications permet de gérer l'envoi et le suivi des notifications dans l'application Écho Citoyen. Elle supporte plusieurs canaux de notification (email, Slack, SMS) et offre des fonctionnalités de suivi et de statistiques.

## Authentification

Toutes les requêtes à l'API nécessitent une authentification par JWT (JSON Web Token). Le token doit être inclus dans l'en-tête `Authorization` sous la forme :

```
Authorization: Bearer <votre_token>
```

## Endpoints

### Créer une notification

```http
POST /notifications
```

Crée et envoie une nouvelle notification.

#### Corps de la requête

```json
{
  "title": "Nouvelle alerte",
  "content": "Une nouvelle alerte a été détectée",
  "channel": "email",
  "recipient": "user@example.com",
  "priority": "high"
}
```

#### Réponse

```json
{
  "id": 1,
  "title": "Nouvelle alerte",
  "content": "Une nouvelle alerte a été détectée",
  "channel": "email",
  "recipient": "user@example.com",
  "priority": "high",
  "status": "pending",
  "created_at": "2024-01-20T10:00:00Z",
  "sent_at": null,
  "error_message": null
}
```

### Lister les notifications

```http
GET /notifications?skip=0&limit=100
```

Récupère la liste des notifications avec pagination.

#### Paramètres de requête

- `skip` (optionnel) : Nombre d'éléments à sauter (défaut : 0)
- `limit` (optionnel) : Nombre maximum d'éléments à retourner (défaut : 100)

#### Réponse

```json
[
  {
    "id": 1,
    "title": "Nouvelle alerte",
    "content": "Une nouvelle alerte a été détectée",
    "channel": "email",
    "recipient": "user@example.com",
    "priority": "high",
    "status": "sent",
    "created_at": "2024-01-20T10:00:00Z",
    "sent_at": "2024-01-20T10:00:05Z",
    "error_message": null
  }
]
```

### Obtenir une notification

```http
GET /notifications/{notification_id}
```

Récupère les détails d'une notification spécifique.

#### Réponse

```json
{
  "id": 1,
  "title": "Nouvelle alerte",
  "content": "Une nouvelle alerte a été détectée",
  "channel": "email",
  "recipient": "user@example.com",
  "priority": "high",
  "status": "sent",
  "created_at": "2024-01-20T10:00:00Z",
  "sent_at": "2024-01-20T10:00:05Z",
  "error_message": null
}
```

### Obtenir les statistiques

```http
GET /notifications/stats
```

Récupère les statistiques des notifications.

#### Réponse

```json
{
  "total_notifications": 100,
  "notifications_by_channel": {
    "email": 60,
    "slack": 30,
    "sms": 10
  },
  "notifications_by_priority": {
    "low": 20,
    "medium": 50,
    "high": 30
  },
  "notifications_by_status": {
    "pending": 5,
    "sent": 90,
    "failed": 5
  }
}
```

## Codes d'erreur

- `400` : Requête invalide
- `401` : Non authentifié
- `404` : Ressource non trouvée
- `422` : Données invalides

## Exemples d'utilisation

### Envoi d'une notification par email

```python
import requests

headers = {
    "Authorization": "Bearer <votre_token>",
    "Content-Type": "application/json"
}

data = {
    "title": "Nouvelle alerte",
    "content": "Une nouvelle alerte a été détectée",
    "channel": "email",
    "recipient": "user@example.com",
    "priority": "high"
}

response = requests.post(
    "https://api.echo-citoyen.fr/notifications",
    headers=headers,
    json=data
)

print(response.json())
```

### Récupération des statistiques

```python
import requests

headers = {
    "Authorization": "Bearer <votre_token>"
}

response = requests.get(
    "https://api.echo-citoyen.fr/notifications/stats",
    headers=headers
)

stats = response.json()
print(f"Total des notifications : {stats['total_notifications']}")
print(f"Notifications par canal : {stats['notifications_by_channel']}")
```

## Bonnes pratiques

1. **Gestion des erreurs** : Toujours vérifier les codes de réponse et gérer les erreurs appropriément.
2. **Rate limiting** : Respecter les limites de taux d'API (100 requêtes par minute par défaut).
3. **Validation** : Valider les données avant l'envoi pour éviter les erreurs 422.
4. **Sécurité** : Ne jamais exposer les tokens JWT dans le code client.
5. **Monitoring** : Surveiller les statistiques pour détecter les problèmes potentiels.

## Support

Pour toute question ou problème, contactez le support à support@echo-citoyen.fr. 