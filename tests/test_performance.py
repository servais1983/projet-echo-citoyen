import pytest
import time
from fastapi import status
from app.core.config import settings

def test_notification_creation_performance(client, test_token):
    """Teste les performances de création de notifications."""
    start_time = time.time()
    
    # Création de 100 notifications
    for i in range(100):
        response = client.post(
            "/notifications/",
            json={
                "title": f"Test Notification {i}",
                "content": f"Test Content {i}",
                "channel": "email",
                "priority": "normal"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    end_time = time.time()
    duration = end_time - start_time
    
    # La création de 100 notifications ne devrait pas prendre plus de 10 secondes
    assert duration < 10.0

def test_notification_batch_creation_performance(client, test_token):
    """Teste les performances de création de notifications par lots."""
    start_time = time.time()
    
    # Création de 1000 notifications en un seul lot
    notifications = [
        {
            "title": f"Test Notification {i}",
            "content": f"Test Content {i}",
            "channel": "email",
            "priority": "normal"
        }
        for i in range(1000)
    ]
    
    response = client.post(
        "/notifications/batch",
        json={"notifications": notifications},
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    
    end_time = time.time()
    duration = end_time - start_time
    
    # La création de 1000 notifications en lot ne devrait pas prendre plus de 5 secondes
    assert duration < 5.0

def test_notification_listing_performance(client, test_token):
    """Teste les performances de récupération des notifications."""
    start_time = time.time()
    
    # Récupération de 1000 notifications
    response = client.get(
        "/notifications/?skip=0&limit=1000",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    end_time = time.time()
    duration = end_time - start_time
    
    # La récupération de 1000 notifications ne devrait pas prendre plus de 2 secondes
    assert duration < 2.0

def test_notification_filtering_performance(client, test_token):
    """Teste les performances du filtrage des notifications."""
    start_time = time.time()
    
    # Filtrage de 1000 notifications par statut
    response = client.get(
        "/notifications/?status=pending&skip=0&limit=1000",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Le filtrage de 1000 notifications ne devrait pas prendre plus de 2 secondes
    assert duration < 2.0

def test_template_rendering_performance(client, test_token):
    """Teste les performances du rendu des templates."""
    # Création d'un template
    template_response = client.post(
        "/templates/",
        json={
            "name": "Test Template",
            "content": "Hello {{name}}! This is a test notification.",
            "variables": ["name"]
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert template_response.status_code == status.HTTP_201_CREATED
    template_id = template_response.json()["id"]
    
    start_time = time.time()
    
    # Rendu de 100 notifications avec le template
    for i in range(100):
        response = client.post(
            f"/templates/{template_id}/render",
            json={"variables": {"name": f"User {i}"}},
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Le rendu de 100 notifications ne devrait pas prendre plus de 5 secondes
    assert duration < 5.0

def test_webhook_delivery_performance(client, test_token):
    """Teste les performances de la livraison des webhooks."""
    # Création d'un webhook
    webhook_response = client.post(
        "/webhooks/",
        json={
            "url": "https://example.com/webhook",
            "events": ["notification.created"]
        },
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert webhook_response.status_code == status.HTTP_201_CREATED
    webhook_id = webhook_response.json()["id"]
    
    start_time = time.time()
    
    # Livraison de 100 webhooks
    for i in range(100):
        response = client.post(
            f"/webhooks/{webhook_id}/deliver",
            json={
                "event": "notification.created",
                "data": {"notification_id": i}
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    end_time = time.time()
    duration = end_time - start_time
    
    # La livraison de 100 webhooks ne devrait pas prendre plus de 10 secondes
    assert duration < 10.0

def test_statistics_calculation_performance(client, test_token):
    """Teste les performances du calcul des statistiques."""
    start_time = time.time()
    
    # Calcul des statistiques pour 1000 notifications
    response = client.get(
        "/stats/notifications/",
        headers={"Authorization": f"Bearer {test_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Le calcul des statistiques ne devrait pas prendre plus de 2 secondes
    assert duration < 2.0

def test_concurrent_requests_performance(client, test_token):
    """Teste les performances avec des requêtes concurrentes."""
    import threading
    
    def make_request():
        response = client.get(
            "/notifications/",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_200_OK
    
    start_time = time.time()
    
    # Création de 10 threads pour faire des requêtes concurrentes
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Attente de la fin de tous les threads
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Les requêtes concurrentes ne devraient pas prendre plus de 5 secondes
    assert duration < 5.0

def test_memory_usage_performance(client, test_token):
    """Teste l'utilisation de la mémoire."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # Création de 1000 notifications
    for i in range(1000):
        response = client.post(
            "/notifications/",
            json={
                "title": f"Test Notification {i}",
                "content": f"Test Content {i}",
                "channel": "email",
                "priority": "normal"
            },
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # L'augmentation de la mémoire ne devrait pas dépasser 100 Mo
    assert memory_increase < 100 * 1024 * 1024  # 100 Mo en octets 