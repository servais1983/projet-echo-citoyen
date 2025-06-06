#!/bin/bash

# Configurer l'environnement de test
export TESTING=1
export INTEGRATION_TEST=1

# Attendre que les services soient prêts
echo "Attente du démarrage des services..."
sleep 30

# Exécuter les tests d'intégration
pytest tests/integration/ \
    --verbose \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    --junitxml=test-results/integration.xml

# Vérifier le résultat des tests
if [ $? -eq 0 ]; then
    echo "✅ Tests d'intégration réussis"
    exit 0
else
    echo "❌ Tests d'intégration échoués"
    exit 1
fi 