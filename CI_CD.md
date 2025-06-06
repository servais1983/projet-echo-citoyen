# Configuration CI/CD pour ECHO Citoyen

## Vue d'ensemble

Le pipeline CI/CD est configuré avec GitHub Actions et comprend les étapes suivantes :

1. Tests unitaires et de couverture
2. Construction et publication des images Docker
3. Déploiement automatique sur le serveur de production

## Prérequis

### Secrets GitHub

Les secrets suivants doivent être configurés dans les paramètres GitHub du repository :

- `DOCKERHUB_USERNAME` : Nom d'utilisateur Docker Hub
- `DOCKERHUB_TOKEN` : Token d'accès Docker Hub
- `SSH_PRIVATE_KEY` : Clé SSH privée pour le déploiement
- `SERVER_HOST` : Adresse du serveur de production
- `SERVER_USER` : Utilisateur SSH pour le déploiement

### Serveur de Production

1. Installer Docker et Docker Compose
2. Créer le répertoire `/opt/echo-citoyen`
3. Copier les fichiers de configuration :
   - `docker-compose.yml`
   - `scripts/deploy.sh`
4. Rendre le script de déploiement exécutable :
   ```bash
   chmod +x /opt/echo-citoyen/scripts/deploy.sh
   ```

## Workflow

### Tests

- Exécute les tests unitaires pour chaque service
- Génère des rapports de couverture de code
- Télécharge les rapports sur Codecov

### Construction et Publication

- Construit les images Docker pour chaque service
- Publie les images sur Docker Hub
- Tag les images avec `latest`

### Déploiement

- Se connecte au serveur de production via SSH
- Exécute le script de déploiement
- Vérifie l'état des conteneurs et les logs

## Déploiement Manuel

Pour déployer manuellement :

1. Se connecter au serveur :
   ```bash
   ssh user@server
   ```

2. Naviguer vers le répertoire du projet :
   ```bash
   cd /opt/echo-citoyen
   ```

3. Exécuter le script de déploiement :
   ```bash
   ./scripts/deploy.sh
   ```

## Surveillance

- Les métriques de déploiement sont disponibles dans Grafana
- Les logs des conteneurs sont accessibles via Docker Compose
- Les alertes de déploiement sont envoyées via le système d'alertes

## Maintenance

### Mise à jour des dépendances

1. Mettre à jour les fichiers `requirements.txt`
2. Commiter les changements
3. Le pipeline CI/CD s'exécutera automatiquement

### Rollback

En cas de problème :

1. Se connecter au serveur
2. Restaurer la version précédente :
   ```bash
   cd /opt/echo-citoyen
   docker-compose down
   docker-compose up -d
   ``` 