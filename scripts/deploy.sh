#!/bin/bash

# Arrêter les conteneurs existants
docker-compose down

# Récupérer les dernières images
docker-compose pull

# Construire les images locales
docker-compose build

# Démarrer les services
docker-compose up -d

# Attendre que les services soient prêts
echo "Attente du démarrage des services..."
sleep 30

# Vérifier l'état des conteneurs
docker-compose ps

# Vérifier les logs pour les erreurs
docker-compose logs --tail=100

# Exécuter les migrations de base de données
docker-compose exec api alembic upgrade head

# Vérifier la santé des services
curl -f http://localhost:8000/health || exit 1
curl -f http://localhost:3000/health || exit 1

# Sauvegarder la base de données
docker-compose exec db pg_dump -U postgres echo_db > backup/backup-$(date +%Y%m%d).sql

echo "Déploiement terminé avec succès" 