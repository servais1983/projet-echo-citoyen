"""
Système de gestion des alertes et crises pour le projet ECHO.
Ce module détecte et gère les situations d'urgence signalées par les citoyens
ou identifiées par les analyses automatiques.
"""

import os
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest
import requests
from pymongo import MongoClient
import pandas as pd
from geopy.distance import geodesic

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration de la base de données
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

# Services d'intégration externe
NOTIFICATION_SERVICE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "http://notification-service:5003")
DASHBOARD_SERVICE_URL = os.environ.get("DASHBOARD_SERVICE_URL", "http://dashboard-service:5004")

class CrisisDetector:
    """
    Détecteur d'anomalies et gestionnaire de crises pour le projet ECHO.
    Ce service analyse les requêtes citoyennes pour identifier les situations d'urgence,
    les regrouper géographiquement et temporellement, et faciliter les interventions.
    """
    
    def __init__(self):
        """
        Initialise le détecteur de crises avec les modèles et connexions nécessaires.
        """
        # Connexion à MongoDB
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client.echo_project
        self.alerts = self.db.alerts
        self.reports = self.db.reports
        self.incidents = self.db.incidents
        
        # Initialisation du modèle d'anomalies
        self.anomaly_detector = IsolationForest(
            contamination=0.1,  # 10% des données considérées comme anomalies
            random_state=42,
            n_estimators=100
        )
        
        # Chargement des services d'urgence
        self.emergency_services = self._load_emergency_services("data/emergency_services.json")
        
        # Définition des niveaux d'alerte
        self.alert_levels = {
            1: "Information",      # Simple information, pas d'action immédiate requise
            2: "Attention",        # Situation à surveiller, pas d'urgence immédiate
            3: "Intervention",     # Intervention nécessaire mais pas critique
            4: "Urgence",          # Situation urgente nécessitant une action rapide
            5: "Critique"          # Situation critique, danger immédiat
        }
        
        logger.info("CrisisDetector initialisé avec succès")
    
    def _load_emergency_services(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Charge les informations sur les services d'urgence depuis un fichier JSON.
        
        Args:
            file_path: Chemin vers le fichier JSON des services d'urgence
            
        Returns:
            Dictionnaire des services d'urgence par catégorie
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                services = json.load(f)
            logger.info(f"Services d'urgence chargés depuis {file_path}")
            return services
        except FileNotFoundError:
            logger.warning(f"Fichier des services d'urgence non trouvé: {file_path}")
            # Services par défaut
            return {
                "securite": [
                    {"name": "Police Municipale", "phone": "17", "email": "police@ville.fr"},
                    {"name": "Gendarmerie", "phone": "17", "email": "gendarmerie@ville.fr"}
                ],
                "incendie": [
                    {"name": "Pompiers", "phone": "18", "email": "pompiers@ville.fr"}
                ],
                "sante": [
                    {"name": "SAMU", "phone": "15", "email": "samu@ville.fr"},
                    {"name": "Hôpital Central", "phone": "04.XX.XX.XX.XX", "email": "urgences@hopital.fr"}
                ],
                "infrastructure": [
                    {"name": "Services Techniques", "phone": "04.XX.XX.XX.XX", "email": "technique@ville.fr"},
                    {"name": "Voirie", "phone": "04.XX.XX.XX.XX", "email": "voirie@ville.fr"}
                ],
                "environnement": [
                    {"name": "Service Environnement", "phone": "04.XX.XX.XX.XX", "email": "environnement@ville.fr"}
                ]
            }
    
    def _text_to_vector(self, reports: List[Dict[str, Any]]) -> np.ndarray:
        """
        Convertit les textes des rapports en vecteurs numériques pour analyse.
        Dans une implémentation réelle, cela utiliserait un modèle d'embedding
        comme Word2Vec, BERT, etc.
        
        Args:
            reports: Liste des rapports à vectoriser
            
        Returns:
            Matrice de vecteurs numériques représentant les textes
        """
        # Simulation simple - en production, utiliser un modèle NLP réel
        # Exemple avec des caractéristiques basiques (longueur du texte, nombre de mots, etc.)
        features = []
        for report in reports:
            text = report.get("text", "")
            features.append([
                len(text),                         # Longueur du texte
                len(text.split()),                 # Nombre de mots
                text.count("!"),                   # Nombre de points d'exclamation
                text.count("?"),                   # Nombre de points d'interrogation
                report.get("priority", 1),         # Priorité déjà évaluée
                len(report.get("categories", [])), # Nombre de catégories associées
                1 if report.get("sentiment", {}).get("label") == "negative" else 0  # Sentiment négatif
            ])
        
        return np.array(features)
    
    def detect_anomalies(self, recent_reports: List[Dict[str, Any]], min_samples: int = 10) -> List[Dict[str, Any]]:
        """
        Détecte les rapports anormaux qui pourraient indiquer une situation d'urgence.
        
        Args:
            recent_reports: Liste des rapports récents à analyser
            min_samples: Nombre minimum d'échantillons pour l'analyse
            
        Returns:
            Liste des rapports considérés comme anomalies
        """
        if len(recent_reports) < min_samples:
            logger.warning(f"Trop peu d'échantillons pour l'analyse d'anomalies ({len(recent_reports)} < {min_samples})")
            # Si trop peu d'échantillons, retourner les rapports à haute priorité
            return [report for report in recent_reports if report.get("priority", 1) >= 4]
        
        # Conversion en vecteurs
        vectors = self._text_to_vector(recent_reports)
        
        # Ajustement du modèle et prédiction
        self.anomaly_detector.fit(vectors)
        predictions = self.anomaly_detector.predict(vectors)
        
        # Filtrer les anomalies (valeurs -1)
        anomalies = [report for report, pred in zip(recent_reports, predictions) if pred == -1]
        
        logger.info(f"Détecté {len(anomalies)} anomalies parmi {len(recent_reports)} rapports")
        return anomalies
    
    def cluster_by_location(self, reports: List[Dict[str, Any]], max_distance_km: float = 1.0) -> List[List[Dict[str, Any]]]:
        """
        Regroupe les rapports par proximité géographique.
        
        Args:
            reports: Liste des rapports à regrouper
            max_distance_km: Distance maximale en kilomètres pour considérer deux rapports comme proches
            
        Returns:
            Liste de clusters (groupes) de rapports
        """
        # Filtrer les rapports sans coordonnées
        geo_reports = [r for r in reports if r.get("location") and "lat" in r.get("location", {}) and "lng" in r.get("location", {})]
        
        if not geo_reports:
            logger.warning("Aucun rapport avec coordonnées géographiques")
            return []
        
        # Algorithme simple de clustering basé sur la distance
        clusters = []
        processed = set()
        
        for i, report in enumerate(geo_reports):
            if i in processed:
                continue
                
            cluster = [report]
            processed.add(i)
            
            report_loc = (report["location"]["lat"], report["location"]["lng"])
            
            # Chercher des rapports proches
            for j, other_report in enumerate(geo_reports):
                if j in processed:
                    continue
                    
                other_loc = (other_report["location"]["lat"], other_report["location"]["lng"])
                distance = geodesic(report_loc, other_loc).kilometers
                
                if distance <= max_distance_km:
                    cluster.append(other_report)
                    processed.add(j)
            
            clusters.append(cluster)
        
        logger.info(f"Créé {len(clusters)} clusters géographiques")
        return clusters
    
    def evaluate_incident_severity(self, reports: List[Dict[str, Any]]) -> int:
        """
        Évalue la sévérité d'un incident basé sur plusieurs rapports.
        
        Args:
            reports: Liste des rapports liés à l'incident
            
        Returns:
            Niveau de sévérité de 1 à 5
        """
        if not reports:
            return 1
        
        # Facteurs influençant la sévérité
        factors = {
            "num_reports": min(len(reports) / 2, 1),  # Nombre de rapports (plafonné à 1)
            "avg_priority": sum(r.get("priority", 1) for r in reports) / len(reports) / 5,  # Priorité moyenne
            "recency": 0,  # À calculer
            "negative_sentiment": len([r for r in reports if r.get("sentiment", {}).get("label") == "negative"]) / len(reports),
            "emergency_keywords": 0,  # À calculer
        }
        
        # Calcul de la récence (rapports plus récents = plus importants)
        now = datetime.now()
        avg_age_hours = sum((now - r.get("timestamp", now)).total_seconds() / 3600 for r in reports) / len(reports)
        factors["recency"] = max(0, 1 - (avg_age_hours / 24))  # 1 pour très récent, 0 pour > 24h
        
        # Vérification des mots-clés d'urgence
        emergency_keywords = ["urgent", "danger", "immédiat", "secours", "blessé", "feu", "accident"]
        keyword_count = 0
        for report in reports:
            text = report.get("text", "").lower()
            keyword_count += sum(1 for keyword in emergency_keywords if keyword in text)
        factors["emergency_keywords"] = min(keyword_count / (len(reports) * 2), 1)  # Plafonné à 1
        
        # Calcul du score final
        weights = {
            "num_reports": 0.15,
            "avg_priority": 0.3,
            "recency": 0.2,
            "negative_sentiment": 0.15,
            "emergency_keywords": 0.2
        }
        
        severity_score = sum(factors[key] * weights[key] for key in weights)
        
        # Conversion en niveau de 1 à 5
        severity_level = int(1 + severity_score * 4)
        
        logger.debug(f"Sévérité calculée: {severity_level} (score: {severity_score:.2f})")
        return severity_level
    
    def create_incident(self, reports: List[Dict[str, Any]], source_type: str) -> str:
        """
        Crée un nouvel incident à partir d'un groupe de rapports.
        
        Args:
            reports: Liste des rapports associés à l'incident
            source_type: Type de source (anomaly, geo_cluster, manual)
            
        Returns:
            ID de l'incident créé
        """
        # Génération d'un ID unique
        incident_id = str(uuid.uuid4())
        
        # Extraction des catégories les plus fréquentes
        all_categories = []
        for report in reports:
            all_categories.extend(report.get("categories", []))
            
        category_counts = {}
        for category in all_categories:
            category_counts[category] = category_counts.get(category, 0) + 1
            
        main_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        main_categories = [cat for cat, _ in main_categories]
        
        # Calcul du centre géographique moyen (si coordonnées disponibles)
        geo_reports = [r for r in reports if r.get("location") and "lat" in r.get("location", {}) and "lng" in r.get("location", {})]
        
        if geo_reports:
            avg_lat = sum(r["location"]["lat"] for r in geo_reports) / len(geo_reports)
            avg_lng = sum(r["location"]["lng"] for r in geo_reports) / len(geo_reports)
            location = {"lat": avg_lat, "lng": avg_lng}
        else:
            location = None
        
        # Génération d'un résumé (dans une implémentation réelle, utiliser un modèle NLP)
        # Exemple basique: prendre le texte du rapport le plus prioritaire
        if reports:
            sorted_reports = sorted(reports, key=lambda r: r.get("priority", 1), reverse=True)
            summary = sorted_reports[0].get("text", "")[:100] + "..."
        else:
            summary = "Incident détecté automatiquement"
        
        # Évaluation de la sévérité
        severity = self.evaluate_incident_severity(reports)
        
        # Création de l'incident
        incident = {
            "incident_id": incident_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "summary": summary,
            "description": f"Incident détecté via {source_type} impliquant {len(reports)} rapports",
            "severity": severity,
            "severity_label": self.alert_levels[severity],
            "categories": main_categories,
            "location": location,
            "status": "new",
            "assigned_to": None,
            "resolution": None,
            "reports": [r.get("_id", "") for r in reports],
            "report_count": len(reports),
            "source_type": source_type
        }
        
        # Stockage dans la base de données
        self.incidents.insert_one(incident)
        logger.info(f"Incident créé: {incident_id} (sévérité {severity})")
        
        # Mise à jour des rapports pour référencer l'incident
        for report in reports:
            report_id = report.get("_id")
            if report_id:
                self.reports.update_one(
                    {"_id": report_id},
                    {"$set": {"incident_id": incident_id, "processed": True}}
                )
        
        # Si l'incident est urgent (niveau 4+), déclencher une alerte
        if severity >= 4:
            self.trigger_alert(incident)
        
        return incident_id
    
    def trigger_alert(self, incident: Dict[str, Any]) -> str:
        """
        Déclenche une alerte pour un incident critique.
        
        Args:
            incident: Incident nécessitant une alerte
            
        Returns:
            ID de l'alerte créée
        """
        # Génération d'un ID unique pour l'alerte
        alert_id = str(uuid.uuid4())
        
        # Détermination des services d'urgence à contacter
        emergency_contacts = []
        for category in incident.get("categories", []):
            if category in self.emergency_services:
                emergency_contacts.extend(self.emergency_services[category])
        
        # Création de l'alerte
        alert = {
            "alert_id": alert_id,
            "incident_id": incident["incident_id"],
            "created_at": datetime.now(),
            "severity": incident["severity"],
            "summary": incident["summary"],
            "location": incident["location"],
            "emergency_contacts": emergency_contacts,
            "status": "created",
            "acknowledged_at": None,
            "resolved_at": None
        }
        
        # Stockage dans la base de données
        self.alerts.insert_one(alert)
        logger.info(f"Alerte créée: {alert_id} pour l'incident {incident['incident_id']}")
        
        # Notifications aux services concernés
        self._send_emergency_notifications(alert, emergency_contacts)
        
        # Mise à jour du tableau de bord
        self._update_dashboard(alert, incident)
        
        return alert_id
    
    def _send_emergency_notifications(self, alert: Dict[str, Any], contacts: List[Dict[str, Any]]) -> None:
        """
        Envoie des notifications aux services d'urgence concernés.
        
        Args:
            alert: Alerte à communiquer
            contacts: Liste des contacts à notifier
        """
        try:
            payload = {
                "alert_id": alert["alert_id"],
                "severity": alert["severity"],
                "summary": alert["summary"],
                "location": alert["location"],
                "contacts": contacts,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{NOTIFICATION_SERVICE_URL}/emergency",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Notifications d'urgence envoyées pour l'alerte {alert['alert_id']}")
                self.alerts.update_one(
                    {"alert_id": alert["alert_id"]},
                    {"$set": {"status": "notified"}}
                )
            else:
                logger.error(f"Erreur lors de l'envoi des notifications: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Erreur de connexion au service de notification: {e}")
    
    def _update_dashboard(self, alert: Dict[str, Any], incident: Dict[str, Any]) -> None:
        """
        Met à jour le tableau de bord avec la nouvelle alerte.
        
        Args:
            alert: Alerte déclenchée
            incident: Incident associé
        """
        try:
            payload = {
                "type": "new_alert",
                "alert_id": alert["alert_id"],
                "incident_id": incident["incident_id"],
                "severity": alert["severity"],
                "summary": alert["summary"],
                "location": alert["location"],
                "categories": incident.get("categories", []),
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{DASHBOARD_SERVICE_URL}/updates",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Tableau de bord mis à jour pour l'alerte {alert['alert_id']}")
            else:
                logger.error(f"Erreur lors de la mise à jour du tableau de bord: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Erreur de connexion au service de tableau de bord: {e}")
    
    def get_recent_reports(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Récupère les rapports récents non traités de la base de données.
        
        Args:
            hours_back: Nombre d'heures en arrière à considérer
            
        Returns:
            Liste des rapports récents
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        cursor = self.reports.find({
            "timestamp": {"$gte": cutoff_time},
            "processed": False
        })
        
        reports = list(cursor)
        logger.info(f"Récupéré {len(reports)} rapports récents non traités des dernières {hours_back}h")
        
        return reports
    
    def process_reports(self) -> None:
        """
        Traite les rapports récents pour détecter des situations critiques.
        Ce processus est typiquement exécuté périodiquement.
        """
        logger.info("Démarrage du traitement des rapports")
        
        # Récupération des rapports récents
        recent_reports = self.get_recent_reports(hours_back=24)
        
        if not recent_reports:
            logger.info("Aucun rapport récent à traiter")
            return
        
        # 1. Détection d'anomalies
        anomalies = self.detect_anomalies(recent_reports)
        if anomalies:
            logger.info(f"Création d'un incident à partir de {len(anomalies)} anomalies")
            self.create_incident(anomalies, "anomaly")
        
        # 2. Clustering géographique
        geo_clusters = self.cluster_by_location(recent_reports)
        for cluster in geo_clusters:
            if len(cluster) >= 3:  # Seuil minimal pour considérer un cluster
                logger.info(f"Création d'un incident à partir d'un cluster de {len(cluster)} rapports")
                self.create_incident(cluster, "geo_cluster")
        
        logger.info("Traitement des rapports terminé")
    
    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Marque une alerte comme prise en compte par un utilisateur.
        
        Args:
            alert_id: ID de l'alerte à reconnaître
            user_id: ID de l'utilisateur qui prend en charge l'alerte
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        result = self.alerts.update_one(
            {"alert_id": alert_id},
            {
                "$set": {
                    "status": "acknowledged",
                    "acknowledged_at": datetime.now(),
                    "acknowledged_by": user_id
                }
            }
        )
        
        success = result.modified_count > 0
        if success:
            logger.info(f"Alerte {alert_id} prise en compte par l'utilisateur {user_id}")
        else:
            logger.warning(f"Échec de la prise en compte de l'alerte {alert_id}")
        
        return success
    
    def resolve_alert(self, alert_id: str, resolution_notes: str) -> bool:
        """
        Marque une alerte comme résolue.
        
        Args:
            alert_id: ID de l'alerte à résoudre
            resolution_notes: Notes sur la résolution
            
        Returns:
            True si l'opération a réussi, False sinon
        """
        # Récupération de l'alerte
        alert = self.alerts.find_one({"alert_id": alert_id})
        if not alert:
            logger.warning(f"Alerte {alert_id} non trouvée")
            return False
        
        # Mise à jour de l'alerte
        result_alert = self.alerts.update_one(
            {"alert_id": alert_id},
            {
                "$set": {
                    "status": "resolved",
                    "resolved_at": datetime.now(),
                    "resolution_notes": resolution_notes
                }
            }
        )
        
        # Mise à jour de l'incident associé
        result_incident = self.incidents.update_one(
            {"incident_id": alert["incident_id"]},
            {
                "$set": {
                    "status": "resolved",
                    "resolution": resolution_notes,
                    "updated_at": datetime.now()
                }
            }
        )
        
        success = result_alert.modified_count > 0 and result_incident.modified_count > 0
        if success:
            logger.info(f"Alerte {alert_id} résolue")
        else:
            logger.warning(f"Échec de la résolution de l'alerte {alert_id}")
        
        return success

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation du détecteur
    detector = CrisisDetector()
    
    # Démonstration avec des exemples simulés
    print("=== DÉMONSTRATION DU DÉTECTEUR DE CRISES ===")
    
    # Simulation de rapports
    example_reports = [
        {
            "_id": "report1",
            "text": "Il y a un gros incendie dans l'immeuble au 15 rue des Lilas ! Urgent !",
            "timestamp": datetime.now(),
            "priority": 5,
            "categories": ["securite", "incendie"],
            "sentiment": {"label": "negative", "score": -0.9},
            "location": {"lat": 45.7578, "lng": 4.8320},
            "processed": False
        },
        {
            "_id": "report2",
            "text": "Je vois des flammes sortir du toit de l'immeuble rue des Lilas !",
            "timestamp": datetime.now() - timedelta(minutes=5),
            "priority": 4,
            "categories": ["securite", "incendie"],
            "sentiment": {"label": "negative", "score": -0.8},
            "location": {"lat": 45.7580, "lng": 4.8318},
            "processed": False
        },
        {
            "_id": "report3",
            "text": "Beaucoup de fumée noire venant de l'immeuble à côté du parc",
            "timestamp": datetime.now() - timedelta(minutes=10),
            "priority": 4,
            "categories": ["securite", "incendie"],
            "sentiment": {"label": "negative", "score": -0.7},
            "location": {"lat": 45.7575, "lng": 4.8325},
            "processed": False
        }
    ]
    
    # Démonstration du clustering géographique
    print("\n-> Clustering géographique des rapports")
    clusters = detector.cluster_by_location(example_reports)
    print(f"Clusters détectés: {len(clusters)}")
    print(f"Taille du premier cluster: {len(clusters[0])} rapports")
    
    # Démonstration de la création d'incident
    print("\n-> Création d'un incident à partir des rapports")
    incident_id = detector.create_incident(example_reports, "demo")
    print(f"Incident créé avec ID: {incident_id}")
    
    print("\n=== FIN DE LA DÉMONSTRATION ===")
