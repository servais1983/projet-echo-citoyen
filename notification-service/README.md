# Service de Notifications

Service de gestion et d'envoi de notifications via différents canaux (email, Slack, SMS).

## Prérequis

- Docker et Docker Compose
- Git
- Accès au registry Docker
- Variables d'environnement configurées

## Structure du Projet

```
notification-service/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   └── services/
├── config/
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   └── grafana/
├── scripts/
│   ├── deploy.sh
│   └── rollback.sh
├── tests/
│   ├── unit/
│   ├── integration/
│   └── performance/
├── docker-compose.dev.yml
├── docker-compose.staging.yml
├── docker-compose.prod.yml
└── README.md
```

## Configuration des Variables d'Environnement

Créez un fichier `.env.<environment>` pour chaque environnement (dev, staging, prod) avec les variables suivantes :

```bash
# Base de données
POSTGRES_PASSWORD=your_secure_password

# SMTP
SMTP_USER=your_smtp_user
SMTP_PASSWORD=your_smtp_password

# Slack
SLACK_WEBHOOK_URL=your_webhook_url

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_phone_number

# JWT
JWT_SECRET_KEY=your_secret_key

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=your_secure_password
GRAFANA_SMTP_USER=your_smtp_user
GRAFANA_SMTP_PASSWORD=your_smtp_password
```

## Déploiement

### Développement

```bash
# Démarrage des services
docker-compose -f docker-compose.dev.yml up -d

# Vérification des logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Staging

```bash
# Déploiement
./scripts/deploy.sh staging

# Rollback si nécessaire
./scripts/rollback.sh staging <version>
```

### Production

```bash
# Déploiement
./scripts/deploy.sh prod

# Rollback si nécessaire
./scripts/rollback.sh prod <version>
```

## Monitoring

### Prometheus

- URL: http://localhost:9090
- Configuration: `config/prometheus.yml`
- Règles d'alerte: `config/alert_rules.yml`

### Grafana

- URL: http://localhost:3000
- Identifiants par défaut:
  - Utilisateur: admin
  - Mot de passe: admin
- Dashboards: Provisionnés automatiquement

## Tests

### Tests Unitaires

```bash
pytest tests/unit/
```

### Tests d'Intégration

```bash
pytest tests/integration/
```

### Tests de Performance

```bash
# Installation de Locust
pip install locust

# Lancement des tests
locust -f tests/performance/locustfile.py
```

## Sécurité

- Tous les secrets sont gérés via des variables d'environnement
- Les conteneurs sont exécutés avec des privilèges minimaux
- Les healthchecks sont configurés pour tous les services
- Les ressources sont limitées pour éviter les attaques DoS

## Maintenance

### Nettoyage des Logs

```bash
# Nettoyage des logs plus anciens que 30 jours
find ./logs -name "*.log" -mtime +30 -delete
```

### Sauvegarde de la Base de Données

```bash
# Sauvegarde
docker exec notification-db-prod pg_dump -U postgres notifications_prod > backup.sql

# Restauration
cat backup.sql | docker exec -i notification-db-prod psql -U postgres notifications_prod
```

## Support

Pour toute question ou problème, veuillez contacter l'équipe de support à support@example.com. 