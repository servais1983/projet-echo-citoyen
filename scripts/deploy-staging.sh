#!/bin/bash

# Configurer l'environnement de staging
export ENVIRONMENT=staging
export COMPOSE_PROJECT_NAME=echo-staging

# Arrêter les conteneurs existants
docker-compose -f docker-compose.staging.yml down

# Récupérer les dernières images
docker-compose -f docker-compose.staging.yml pull

# Construire les images locales
docker-compose -f docker-compose.staging.yml build

# Démarrer les services
docker-compose -f docker-compose.staging.yml up -d

# Attendre que les services soient prêts
echo "Attente du démarrage des services..."
sleep 30

# Vérifier l'état des conteneurs
docker-compose -f docker-compose.staging.yml ps

# Exécuter les migrations de base de données
docker-compose -f docker-compose.staging.yml exec api alembic upgrade head

# Exécuter les tests d'intégration
./scripts/run-integration-tests.sh

# Vérifier la santé des services
curl -f http://staging-api.echo-citoyen.org/health || exit 1
curl -f http://staging-dashboard.echo-citoyen.org/health || exit 1

echo "Déploiement sur staging terminé avec succès" 