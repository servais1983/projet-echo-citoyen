#!/bin/bash

# Configuration
APP_NAME="notification-service"
DOCKER_REGISTRY="registry.example.com"
ENVIRONMENT=$1
VERSION=$(git describe --tags --always)

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Fonction pour afficher les messages
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Vérification des arguments
if [ -z "$ENVIRONMENT" ]; then
    error "Usage: $0 <environment>"
fi

# Vérification de l'environnement
if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
    error "Environment must be one of: dev, staging, prod"
fi

# Chargement des variables d'environnement
if [ -f ".env.$ENVIRONMENT" ]; then
    log "Loading environment variables from .env.$ENVIRONMENT"
    source ".env.$ENVIRONMENT"
else
    error "Environment file .env.$ENVIRONMENT not found"
fi

# Construction de l'image Docker
log "Building Docker image..."
docker build -t $DOCKER_REGISTRY/$APP_NAME:$VERSION . || error "Docker build failed"

# Exécution des tests
log "Running tests..."
docker run --rm $DOCKER_REGISTRY/$APP_NAME:$VERSION pytest || error "Tests failed"

# Tag de l'image pour l'environnement
log "Tagging image for $ENVIRONMENT..."
docker tag $DOCKER_REGISTRY/$APP_NAME:$VERSION $DOCKER_REGISTRY/$APP_NAME:$ENVIRONMENT || error "Docker tag failed"

# Push de l'image
log "Pushing image to registry..."
docker push $DOCKER_REGISTRY/$APP_NAME:$VERSION || error "Docker push failed"
docker push $DOCKER_REGISTRY/$APP_NAME:$ENVIRONMENT || error "Docker push failed"

# Déploiement sur l'environnement cible
log "Deploying to $ENVIRONMENT..."

case $ENVIRONMENT in
    "dev")
        # Déploiement sur le serveur de développement
        ssh dev-server "docker pull $DOCKER_REGISTRY/$APP_NAME:$ENVIRONMENT && \
                       docker-compose -f docker-compose.dev.yml up -d"
        ;;
    "staging")
        # Déploiement sur le serveur de staging
        ssh staging-server "docker pull $DOCKER_REGISTRY/$APP_NAME:$ENVIRONMENT && \
                          docker-compose -f docker-compose.staging.yml up -d"
        ;;
    "prod")
        # Déploiement sur le serveur de production
        ssh prod-server "docker pull $DOCKER_REGISTRY/$APP_NAME:$ENVIRONMENT && \
                        docker-compose -f docker-compose.prod.yml up -d"
        ;;
esac

# Vérification du déploiement
log "Checking deployment..."
sleep 10
curl -f http://localhost:5001/health || error "Deployment health check failed"

# Nettoyage des anciennes images
log "Cleaning up old images..."
docker image prune -f

log "Deployment completed successfully!" 