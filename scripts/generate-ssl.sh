#!/bin/bash

# Créer le répertoire pour les certificats
mkdir -p certs

# Générer les certificats auto-signés pour le développement
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout certs/private.key \
  -out certs/certificate.crt \
  -subj "/C=FR/ST=IDF/L=Paris/O=ECHO/CN=localhost"

# Pour la production, utiliser Let's Encrypt
if [ "$ENVIRONMENT" = "production" ]; then
  certbot certonly --standalone \
    -d api.echo-citoyen.org \
    -d dashboard.echo-citoyen.org \
    -d auth.echo-citoyen.org
fi

echo "Certificats SSL générés avec succès" 