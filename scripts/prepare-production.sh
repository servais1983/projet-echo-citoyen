#!/bin/bash

# Vérifier les prérequis
command -v docker >/dev/null 2>&1 || { echo "Docker est requis"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose est requis"; exit 1; }

# Créer les répertoires nécessaires
mkdir -p logs
mkdir -p data
mkdir -p backup

# Configurer les permissions
chmod 600 .env
chmod 600 secrets/*
chmod 700 scripts/*

# Vérifier l'espace disque
DISK_SPACE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_SPACE" -gt 80 ]; then
    echo "Attention: Espace disque faible ($DISK_SPACE%)"
    exit 1
fi

# Vérifier la mémoire disponible
MEM_AVAIL=$(free -m | awk 'NR==2 {print $7}')
if [ "$MEM_AVAIL" -lt 2048 ]; then
    echo "Attention: Mémoire disponible insuffisante ($MEM_AVAIL MB)"
    exit 1
fi

# Configurer le système
sysctl -w net.core.somaxconn=65535
sysctl -w vm.max_map_count=262144

# Créer les utilisateurs système
useradd -r -s /bin/false echo-app
useradd -r -s /bin/false echo-monitor

# Configurer les limites système
cat > /etc/security/limits.d/echo.conf << EOL
echo-app soft nofile 65535
echo-app hard nofile 65535
echo-monitor soft nofile 65535
echo-monitor hard nofile 65535
EOL

echo "Environnement de production préparé avec succès" 