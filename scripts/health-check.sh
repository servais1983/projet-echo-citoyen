#!/bin/bash

# Vérifier les services
check_service() {
    local service=$1
    local url=$2
    local response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" = "200" ]; then
        echo "✅ $service est opérationnel"
        return 0
    else
        echo "❌ $service n'est pas opérationnel (code: $response)"
        return 1
    fi
}

# Vérifier les métriques
check_metrics() {
    local metric=$1
    local threshold=$2
    local value=$(curl -s "http://localhost:9090/api/v1/query?query=$metric" | jq -r '.data.result[0].value[1]')
    
    if (( $(echo "$value < $threshold" | bc -l) )); then
        echo "✅ $metric est dans les limites ($value < $threshold)"
        return 0
    else
        echo "❌ $metric dépasse le seuil ($value >= $threshold)"
        return 1
    fi
}

# Vérifier l'espace disque
check_disk() {
    local usage=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -lt 80 ]; then
        echo "✅ Espace disque suffisant ($usage%)"
        return 0
    else
        echo "❌ Espace disque faible ($usage%)"
        return 1
    fi
}

# Vérifier la mémoire
check_memory() {
    local usage=$(free | awk 'NR==2 {print $3/$2 * 100.0}')
    if (( $(echo "$usage < 80" | bc -l) )); then
        echo "✅ Mémoire suffisante ($usage%)"
        return 0
    else
        echo "❌ Mémoire faible ($usage%)"
        return 1
    fi
}

# Vérifier les services
echo "Vérification des services..."
check_service "API Gateway" "http://localhost:8000/health"
check_service "Dashboard" "http://localhost:3000/health"
check_service "Auth Service" "http://localhost:5003/health"
check_service "NLP Engine" "http://localhost:5000/health"

# Vérifier les métriques
echo -e "\nVérification des métriques..."
check_metrics "rate(http_requests_total{status=~\"5..\"}[5m])" "0.01"
check_metrics "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))" "0.5"

# Vérifier les ressources
echo -e "\nVérification des ressources..."
check_disk
check_memory

# Vérifier les logs pour les erreurs
echo -e "\nVérification des logs..."
docker-compose logs --tail=100 | grep -i "error\|exception\|fail" || echo "✅ Aucune erreur dans les logs récents"

echo -e "\nVérification de santé terminée" 