"""
Module principal du service de chatbot pour le projet ECHO.
Ce module gère les interactions conversationnelles avec les citoyens,
en utilisant des modèles de langage avancés et une logique de dialogue structurée.
"""

import os
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

import requests
import speech_recognition as sr
from transformers import pipeline
from gtts import gTTS

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URL des services internes
NLP_SERVICE_URL = os.environ.get("NLP_SERVICE_URL", "http://nlp-engine:5000")
ALERT_SERVICE_URL = os.environ.get("ALERT_SERVICE_URL", "http://alert-system:5001")
ADMIN_SERVICE_URL = os.environ.get("ADMIN_SERVICE_URL", "http://admin-service:5002")

class EchoChatbot:
    """
    Chatbot intelligent pour le projet ECHO, capable de comprendre et répondre
    aux demandes des citoyens en langage naturel et en mode vocal.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        Initialise le chatbot avec un modèle de génération de texte.
        
        Args:
            model_name: Nom du modèle de transformers à utiliser
        """
        self.conversation_generator = pipeline("conversational", model=model_name)
        self.stt = sr.Recognizer()
        
        # Initialisation du système de reconnaissance vocale
        self.stt.energy_threshold = 4000
        self.stt.dynamic_energy_threshold = True
        
        logger.info(f"Chatbot initialisé avec le modèle {model_name}")
        
        # Chargement des réponses prédéfinies
        self.load_predefined_responses()
        
        # Dictionnaire pour stocker les sessions de conversation
        self.conversations = {}
        
    def load_predefined_responses(self, file_path: str = "data/responses.json"):
        """
        Charge les réponses prédéfinies depuis un fichier JSON.
        
        Args:
            file_path: Chemin vers le fichier de réponses
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.predefined_responses = json.load(f)
            logger.info(f"Réponses prédéfinies chargées depuis {file_path}")
        except FileNotFoundError:
            logger.warning(f"Fichier de réponses non trouvé: {file_path}")
            # Réponses par défaut
            self.predefined_responses = {
                "greeting": [
                    "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
                    "Bienvenue sur ECHO. En quoi puis-je vous être utile ?"
                ],
                "farewell": [
                    "Merci d'avoir utilisé ECHO. À bientôt !",
                    "Au revoir ! N'hésitez pas à revenir si vous avez d'autres questions."
                ],
                "fallback": [
                    "Je suis désolé, je n'ai pas bien compris votre demande. Pourriez-vous la reformuler ?",
                    "Désolé, je ne peux pas traiter cette requête. Essayez de la formuler différemment."
                ]
            }
    
    def voice_to_text(self, audio_file: str) -> str:
        """
        Convertit un fichier audio en texte.
        
        Args:
            audio_file: Chemin vers le fichier audio
            
        Returns:
            Texte transcrit du fichier audio
        """
        logger.info(f"Conversion audio en texte: {audio_file}")
        
        try:
            with sr.AudioFile(audio_file) as source:
                audio_data = self.stt.record(source)
                text = self.stt.recognize_google(audio_data, language="fr-FR")
                logger.info(f"Texte reconnu: {text}")
                return text
        except sr.UnknownValueError:
            logger.warning("La reconnaissance vocale n'a pas pu comprendre l'audio")
            return ""
        except sr.RequestError as e:
            logger.error(f"Erreur lors de la requête au service de reconnaissance vocale: {e}")
            return ""
    
    def text_to_voice(self, text: str, output_file: str = "response.mp3", lang: str = "fr") -> str:
        """
        Convertit du texte en fichier audio.
        
        Args:
            text: Texte à convertir en audio
            output_file: Nom du fichier de sortie
            lang: Code de langue
            
        Returns:
            Chemin vers le fichier audio généré
        """
        logger.info(f"Conversion texte en audio: {text[:50]}...")
        
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_file)
            logger.info(f"Audio généré et sauvegardé dans {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Erreur lors de la génération audio: {e}")
            return ""
    
    def create_conversation(self, user_id: str) -> str:
        """
        Crée une nouvelle session de conversation.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Identifiant de la conversation
        """
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.conversations[conversation_id] = {
            "user_id": user_id,
            "created_at": timestamp,
            "last_updated": timestamp,
            "messages": [],
            "context": {}
        }
        
        logger.info(f"Nouvelle conversation créée: {conversation_id} pour l'utilisateur {user_id}")
        return conversation_id
    
    def add_message(self, conversation_id: str, message: str, sender: str) -> None:
        """
        Ajoute un message à une conversation existante.
        
        Args:
            conversation_id: Identifiant de la conversation
            message: Contenu du message
            sender: Expéditeur ("user" ou "bot")
        """
        if conversation_id not in self.conversations:
            logger.warning(f"Tentative d'ajout à une conversation inexistante: {conversation_id}")
            return
        
        timestamp = datetime.now().isoformat()
        
        self.conversations[conversation_id]["messages"].append({
            "content": message,
            "sender": sender,
            "timestamp": timestamp
        })
        
        self.conversations[conversation_id]["last_updated"] = timestamp
        logger.debug(f"Message ajouté à la conversation {conversation_id}")
    
    def classify_intent(self, message: str) -> Dict[str, Any]:
        """
        Classifie l'intention de l'utilisateur en utilisant le service NLP.
        
        Args:
            message: Message de l'utilisateur
            
        Returns:
            Dictionnaire contenant l'intention détectée et les entités
        """
        try:
            response = requests.post(
                f"{NLP_SERVICE_URL}/classify",
                json={"text": message}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la classification: {response.status_code}")
                return {"intent": "unknown", "confidence": 0, "entities": {}}
                
        except requests.RequestException as e:
            logger.error(f"Erreur de connexion au service NLP: {e}")
            return {"intent": "unknown", "confidence": 0, "entities": {}}
    
    def check_urgency(self, classification: Dict[str, Any]) -> bool:
        """
        Vérifie si une demande est urgente et doit être escaladée.
        
        Args:
            classification: Résultat de la classification d'intention
            
        Returns:
            True si la demande est urgente, False sinon
        """
        # Critères d'urgence
        urgent_intents = ["urgence", "danger", "accident", "incendie", "secours"]
        urgent_categories = ["securite", "sante"]
        high_urgency_threshold = 0.8
        
        # Vérification de l'intention
        if classification.get("intent") in urgent_intents:
            logger.info(f"Demande urgente détectée: {classification.get('intent')}")
            return True
        
        # Vérification de la catégorie
        if classification.get("category") in urgent_categories and classification.get("confidence", 0) > high_urgency_threshold:
            logger.info(f"Demande urgente détectée dans la catégorie: {classification.get('category')}")
            return True
            
        # Vérification du sentiment négatif intense
        if classification.get("sentiment", {}).get("label") == "negative" and classification.get("sentiment", {}).get("score", 0) > 0.9:
            logger.info("Sentiment très négatif détecté, possible urgence")
            return True
            
        return False
    
    def escalate_to_alert_system(self, message: str, classification: Dict[str, Any], user_data: Dict[str, Any]) -> str:
        """
        Escalade une demande urgente au système d'alerte.
        
        Args:
            message: Message de l'utilisateur
            classification: Résultat de la classification
            user_data: Données de l'utilisateur
            
        Returns:
            Identifiant du ticket d'urgence créé
        """
        try:
            payload = {
                "message": message,
                "classification": classification,
                "user": user_data,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{ALERT_SERVICE_URL}/alerts",
                json=payload
            )
            
            if response.status_code == 201:
                ticket_id = response.json().get("ticket_id")
                logger.info(f"Alerte créée avec succès: {ticket_id}")
                return ticket_id
            else:
                logger.error(f"Erreur lors de la création d'alerte: {response.status_code}")
                return ""
                
        except requests.RequestException as e:
            logger.error(f"Erreur de connexion au système d'alerte: {e}")
            return ""
    
    def generate_response(self, message: str, conversation_id: str) -> str:
        """
        Génère une réponse au message de l'utilisateur.
        
        Args:
            message: Message de l'utilisateur
            conversation_id: Identifiant de la conversation
            
        Returns:
            Réponse générée
        """
        # Vérification si la conversation existe
        if conversation_id not in self.conversations:
            logger.warning(f"Conversation non trouvée: {conversation_id}")
            return self.predefined_responses["fallback"][0]
        
        # Classification de l'intention
        classification = self.classify_intent(message)
        intent = classification.get("intent", "unknown")
        
        # Récupération du contexte de conversation
        context = self.conversations[conversation_id]["context"]
        past_messages = [msg for msg in self.conversations[conversation_id]["messages"] if msg["sender"] == "user"]
        past_user_inputs = [msg["content"] for msg in past_messages[-5:]] if past_messages else []
        
        # Vérification si c'est une demande urgente
        if self.check_urgency(classification):
            user_id = self.conversations[conversation_id]["user_id"]
            # Récupération des données utilisateur (dans un système réel)
            user_data = {"id": user_id}  # Simplifié pour l'exemple
            
            # Escalade au système d'alerte
            ticket_id = self.escalate_to_alert_system(message, classification, user_data)
            
            if ticket_id:
                context["alert_ticket"] = ticket_id
                return (
                    "Votre demande a été identifiée comme urgente et a été transmise "
                    f"aux services compétents. Numéro de suivi: {ticket_id}. "
                    "Un agent va vous contacter dans les plus brefs délais."
                )
        
        # Réponses basées sur l'intention pour les cas communs
        if intent == "greeting":
            return self.predefined_responses["greeting"][0]
        elif intent == "farewell":
            return self.predefined_responses["farewell"][0]
            
        # Génération de réponse par le modèle de langage pour les cas complexes
        try:
            response = self.conversation_generator(
                message,
                past_user_inputs=past_user_inputs,
                min_length=20,
                max_length=150
            )
            
            generated_text = response.generated_responses[-1]
            
            # Enrichissement de la réponse avec des informations contextuelles
            if classification.get("category") == "administration" and "form" in message.lower():
                generated_text += " Vous pouvez télécharger tous les formulaires nécessaires sur le site de la mairie."
                
            return generated_text
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de réponse: {e}")
            return self.predefined_responses["fallback"][0]
    
    def process_user_message(self, user_id: str, message: str, conversation_id: Optional[str] = None, is_voice: bool = False) -> Dict[str, Any]:
        """
        Traite un message utilisateur et génère une réponse.
        
        Args:
            user_id: Identifiant de l'utilisateur
            message: Message texte ou chemin vers un fichier audio
            conversation_id: Identifiant de conversation existante (optionnel)
            is_voice: Indique si le message est un fichier audio
            
        Returns:
            Dictionnaire contenant la réponse et les métadonnées
        """
        # Traitement du message vocal si nécessaire
        if is_voice:
            message = self.voice_to_text(message)
            if not message:
                return {
                    "status": "error",
                    "message": "Impossible de reconnaître le message vocal"
                }
        
        # Création ou récupération de la conversation
        if not conversation_id or conversation_id not in self.conversations:
            conversation_id = self.create_conversation(user_id)
        
        # Enregistrement du message utilisateur
        self.add_message(conversation_id, message, "user")
        
        # Génération de la réponse
        response_text = self.generate_response(message, conversation_id)
        
        # Enregistrement de la réponse du bot
        self.add_message(conversation_id, response_text, "bot")
        
        # Conversion en audio si demandé
        voice_response = None
        if is_voice:
            output_file = f"responses/{conversation_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            voice_response = self.text_to_voice(response_text, output_file)
        
        return {
            "status": "success",
            "conversation_id": conversation_id,
            "text_response": response_text,
            "voice_response": voice_response,
            "timestamp": datetime.now().isoformat()
        }

# Point d'entrée d'exemple
if __name__ == "__main__":
    # Initialisation du chatbot
    chatbot = EchoChatbot()
    
    # Exemples de messages utilisateur
    test_messages = [
        "Bonjour, je voudrais signaler un lampadaire cassé dans ma rue",
        "J'ai besoin de formulaires pour la carte d'identité",
        "Il y a un incendie dans l'immeuble à côté !",
        "Merci pour votre aide, au revoir"
    ]
    
    # Test du chatbot avec les messages
    user_id = "test_user_123"
    conversation_id = None
    
    print("=== DEMO DU CHATBOT ECHO ===")
    for message in test_messages:
        print(f"\nUtilisateur: {message}")
        
        result = chatbot.process_user_message(user_id, message, conversation_id)
        conversation_id = result["conversation_id"]
        
        print(f"ECHO: {result['text_response']}")
        print("-" * 50)
