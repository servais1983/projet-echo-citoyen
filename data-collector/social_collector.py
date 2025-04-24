"""
Module de collecte de données depuis les réseaux sociaux pour le projet ECHO.
Ce module surveille les réseaux sociaux pour collecter les mentions pertinentes
concernant les services publics, l'infrastructure urbaine et autres sujets d'intérêt citoyen.
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

import tweepy
from textblob import TextBlob
import requests
from pymongo import MongoClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration des API (à charger depuis des variables d'environnement)
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY", "")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET", "")
TWITTER_ACCESS_TOKEN = os.environ.get("TWITTER_ACCESS_TOKEN", "")
TWITTER_ACCESS_SECRET = os.environ.get("TWITTER_ACCESS_SECRET", "")

# URL des services internes
NLP_SERVICE_URL = os.environ.get("NLP_SERVICE_URL", "http://nlp-engine:5000")
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")

class SocialCollector:
    """
    Collecteur de données des réseaux sociaux pour surveiller les mentions
    pertinentes pour les services publics et les autorités locales.
    """
    
    def __init__(self):
        """
        Initialise le collecteur avec les configurations API nécessaires
        et la connexion à la base de données.
        """
        # Initialisation de l'API Twitter
        self.auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        self.auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET)
        self.twitter_api = tweepy.API(self.auth, wait_on_rate_limit=True)
        
        # Connexion à MongoDB
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client.echo_project
        self.social_mentions = self.db.social_mentions
        
        logger.info("SocialCollector initialisé avec succès")
        
        # Liste des mots-clés pertinents par catégorie
        self.keywords = self._load_keywords("data/keywords.json")
    
    def _load_keywords(self, file_path: str) -> Dict[str, List[str]]:
        """
        Charge les mots-clés à surveiller depuis un fichier JSON.
        
        Args:
            file_path: Chemin vers le fichier JSON de mots-clés
            
        Returns:
            Dictionnaire de mots-clés par catégorie
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                keywords = json.load(f)
            logger.info(f"Mots-clés chargés depuis {file_path}")
            return keywords
        except FileNotFoundError:
            logger.warning(f"Fichier de mots-clés non trouvé: {file_path}")
            # Mots-clés par défaut
            return {
                "infrastructure": ["voirie", "route", "éclairage", "trottoir", "nid-de-poule", "travaux"],
                "environnement": ["déchets", "pollution", "recyclage", "ordures", "espace vert"],
                "securite": ["accident", "insécurité", "police", "danger", "incendie"],
                "administration": ["mairie", "documents", "formulaire", "carte identité", "passeport"],
                "transport": ["bus", "métro", "transport", "retard", "ligne"]
            }
    
    def _clean_text(self, text: str) -> str:
        """
        Nettoie le texte des tweets (suppression des URLs, mentions, etc.).
        
        Args:
            text: Texte brut du tweet
            
        Returns:
            Texte nettoyé
        """
        import re
        # Suppression des URLs
        text = re.sub(r'https?://\S+', '', text)
        # Suppression des mentions
        text = re.sub(r'@\w+', '', text)
        # Suppression des hashtags
        text = re.sub(r'#\w+', '', text)
        # Suppression des caractères spéciaux et emojis
        text = re.sub(r'[^\w\s.,!?]', '', text)
        # Suppression des espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _store_in_db(self, text: str, metadata: Dict[str, Any], source: str) -> str:
        """
        Stocke une mention dans la base de données.
        
        Args:
            text: Texte de la mention
            metadata: Métadonnées associées (langue, sentiment, etc.)
            source: Source de la mention (Twitter, Facebook, etc.)
            
        Returns:
            ID de l'entrée créée dans la base de données
        """
        # Analyse de sentiment basique avec TextBlob
        blob = TextBlob(text)
        sentiment_score = blob.sentiment.polarity
        
        # Détermination du sentiment
        if sentiment_score > 0.1:
            sentiment = "positive"
        elif sentiment_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Catégorisation basique par mots-clés
        categories = []
        for category, terms in self.keywords.items():
            for term in terms:
                if term.lower() in text.lower():
                    categories.append(category)
                    break
        
        # Création du document
        document = {
            "text": text,
            "source": source,
            "timestamp": datetime.now(),
            "metadata": metadata,
            "sentiment": {
                "score": sentiment_score,
                "label": sentiment
            },
            "categories": list(set(categories)),  # Suppression des doublons
            "processed": False,
            "nlp_analysis": None,
            "priority": self._calculate_priority(text, sentiment, categories)
        }
        
        # Insertion dans la base de données
        result = self.social_mentions.insert_one(document)
        logger.debug(f"Mention stockée avec ID: {result.inserted_id}")
        
        # Envoyer pour analyse NLP si priorité élevée
        if document["priority"] >= 3:
            self._send_to_nlp(text, str(result.inserted_id))
        
        return str(result.inserted_id)
    
    def _calculate_priority(self, text: str, sentiment: str, categories: List[str]) -> int:
        """
        Calcule la priorité d'une mention (1-5, 5 étant la plus haute).
        
        Args:
            text: Texte de la mention
            sentiment: Étiquette de sentiment (positive, negative, neutral)
            categories: Liste des catégories détectées
            
        Returns:
            Score de priorité de 1 à 5
        """
        priority = 1  # Priorité par défaut
        
        # Augmenter la priorité pour les sentiments négatifs
        if sentiment == "negative":
            priority += 1
        
        # Augmenter la priorité pour certaines catégories critiques
        critical_categories = ["securite", "sante"]
        if any(cat in critical_categories for cat in categories):
            priority += 1
        
        # Augmenter la priorité pour les mots d'urgence
        emergency_terms = ["urgent", "immédiat", "danger", "aide", "catastrophe", "accident"]
        if any(term in text.lower() for term in emergency_terms):
            priority += 1
        
        # Limiter à 5
        return min(priority, 5)
    
    def _send_to_nlp(self, text: str, doc_id: str) -> None:
        """
        Envoie une mention au service NLP pour analyse approfondie.
        
        Args:
            text: Texte à analyser
            doc_id: ID du document dans la base de données
        """
        try:
            payload = {
                "text": text,
                "doc_id": doc_id
            }
            
            response = requests.post(
                f"{NLP_SERVICE_URL}/analyze",
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Mention envoyée avec succès au service NLP: {doc_id}")
            else:
                logger.error(f"Erreur lors de l'envoi au service NLP: {response.status_code}")
                
        except requests.RequestException as e:
            logger.error(f"Erreur de connexion au service NLP: {e}")
    
    def stream_tweets(self, keywords: Optional[List[str]] = None, locations: Optional[List[float]] = None) -> None:
        """
        Lance une écoute en continu des tweets contenant les mots-clés spécifiés
        ou provenant des zones géographiques indiquées.
        
        Args:
            keywords: Liste de mots-clés à surveiller
            locations: Coordonnées géographiques à surveiller [lon1, lat1, lon2, lat2]
        """
        if not keywords:
            # Si aucun mot-clé spécifié, utiliser tous les mots-clés de toutes les catégories
            keywords = []
            for terms in self.keywords.values():
                keywords.extend(terms)
        
        logger.info(f"Démarrage de l'écoute Twitter avec {len(keywords)} mots-clés")
        
        # Définition de la classe d'écoute
        class CustomStream(tweepy.StreamingClient):
            def __init__(self, bearer_token, parent):
                super().__init__(bearer_token)
                self.parent = parent
            
            def on_tweet(self, tweet):
                # Filtrer les retweets
                if getattr(tweet, 'retweeted', False) or 'RT @' in tweet.text:
                    return
                
                # Nettoyer le texte
                clean_text = self.parent._clean_text(tweet.text)
                
                # Extraire les métadonnées pertinentes
                metadata = {
                    "tweet_id": tweet.id,
                    "user_id": tweet.author_id,
                    "created_at": tweet.created_at,
                    "lang": getattr(tweet, 'lang', 'unknown'),
                    "geo": getattr(tweet, 'geo', None),
                }
                
                # Stocker dans la base de données
                self.parent._store_in_db(clean_text, metadata, "twitter")
                
            def on_error(self, status):
                logger.error(f"Erreur Twitter stream: {status}")
                if status == 420:  # Rate limit
                    logger.warning("Rate limit atteint, pause de l'écoute")
                    return False
        
        # Lancement de l'écoute
        stream = CustomStream(bearer_token=TWITTER_API_SECRET, parent=self)
        
        # Ajout des règles
        for keyword in keywords:
            stream.add_rules(tweepy.StreamRule(keyword))
        
        # Démarrage du stream
        stream.filter(tweet_fields=['author_id', 'created_at', 'geo', 'lang'])
    
    def search_historical_tweets(self, query: str, count: int = 100) -> List[Dict[str, Any]]:
        """
        Recherche dans l'historique des tweets avec une requête spécifique.
        
        Args:
            query: Requête de recherche
            count: Nombre maximum de tweets à récupérer
            
        Returns:
            Liste de tweets correspondant aux critères
        """
        logger.info(f"Recherche Twitter pour: {query}")
        
        collected_tweets = []
        try:
            for tweet in tweepy.Cursor(self.twitter_api.search_tweets, q=query, count=count, tweet_mode="extended").items(count):
                # Nettoyer le texte
                clean_text = self._clean_text(tweet.full_text)
                
                # Extraire les métadonnées
                metadata = {
                    "tweet_id": tweet.id,
                    "user_id": tweet.user.id,
                    "created_at": tweet.created_at,
                    "lang": tweet.lang,
                    "geo": tweet.geo if hasattr(tweet, 'geo') else None,
                }
                
                # Stocker dans la base de données
                doc_id = self._store_in_db(clean_text, metadata, "twitter")
                
                # Ajouter à la liste des résultats
                collected_tweets.append({
                    "id": doc_id,
                    "text": clean_text,
                    "metadata": metadata
                })
            
            logger.info(f"Collecté {len(collected_tweets)} tweets pour la requête: {query}")
            return collected_tweets
            
        except tweepy.TweepyException as e:
            logger.error(f"Erreur lors de la recherche Twitter: {e}")
            return []
    
    def collect_facebook_mentions(self, page_ids: List[str], days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Collecte les mentions Facebook sur les pages spécifiées.
        
        Args:
            page_ids: Liste des IDs de pages Facebook à surveiller
            days_back: Nombre de jours en arrière à collecter
            
        Returns:
            Liste des mentions collectées
        """
        logger.info(f"Collecte des mentions Facebook sur {len(page_ids)} pages")
        
        # Note: Cette méthode nécessite l'API Facebook Graph, qui n'est pas implémentée ici
        # C'est une version simplifiée pour démonstration
        
        # Exemple de données simulées pour démonstration
        collected_mentions = []
        
        # Implémentation réelle nécessiterait l'API Facebook Graph
        # facebook = FacebookAPI(access_token)
        # for page_id in page_ids:
        #     posts = facebook.get_page_posts(page_id, limit=50)
        #     comments = facebook.get_page_comments(page_id, limit=100)
        #     ...
        
        return collected_mentions
    
    def start_collection(self, interval: int = 3600) -> None:
        """
        Lance la collecte continue des données sociales à intervalle régulier.
        
        Args:
            interval: Intervalle en secondes entre les collectes ponctuelles
        """
        logger.info(f"Démarrage de la collecte continue (intervalle: {interval}s)")
        
        # Démarrage du stream Twitter
        import threading
        twitter_thread = threading.Thread(
            target=self.stream_tweets,
            args=(),
            daemon=True
        )
        twitter_thread.start()
        
        # Boucle de collecte périodique
        try:
            while True:
                # Collecter les données de Facebook (exemple)
                pages = ["mairie_example", "servicePublic_example"]
                self.collect_facebook_mentions(pages)
                
                # Attendre l'intervalle
                logger.info(f"En attente du prochain cycle de collecte ({interval}s)")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            logger.info("Collecte arrêtée par l'utilisateur")
        except Exception as e:
            logger.error(f"Erreur lors de la collecte: {e}")

# Exemple d'utilisation
if __name__ == "__main__":
    # Initialisation du collecteur
    collector = SocialCollector()
    
    # Exemple de recherche ponctuelle
    print("=== RECHERCHE PONCTUELLE ===")
    results = collector.search_historical_tweets("mairie travaux", count=5)
    for idx, tweet in enumerate(results, 1):
        print(f"{idx}. {tweet['text']}")
    
    # Lancement de la collecte continue
    print("\n=== LANCEMENT DE LA COLLECTE CONTINUE ===")
    collector.start_collection(interval=300)  # 5 minutes d'intervalle
