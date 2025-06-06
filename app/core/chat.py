from typing import Dict, List, Any, Optional
from datetime import datetime
import re
import asyncio
from .logging import log_security_event
from .security import sanitize_input

class ChatMessage:
    __slots__ = ['content', 'sender', 'type', 'timestamp', 'id']

    def __init__(self, content: str, sender: str, type: str = "text"):
        self.content = content
        self.sender = sender
        self.type = type
        self.timestamp = datetime.now()
        self.id = f"{self.timestamp.timestamp()}_{sender}"

class ChatBot:
    def __init__(self):
        """Initialise le chatbot."""
        self.name = "Echo"
        self.avatar = "🤖"  # Emoji robot par défaut
        self.welcome_messages = [
            "Bonjour ! Je suis Echo, votre assistant virtuel. Comment puis-je vous aider aujourd'hui ?",
            "Salut ! Je suis là pour vous aider. Que souhaitez-vous faire ?",
            "Bienvenue ! Je suis Echo, votre guide dans Echo Citoyen. Que puis-je faire pour vous ?"
        ]
        self.typing_speed = 0.05  # Vitesse de "frappe" en secondes
        self._patterns = {
            r"bonjour|salut|hello|hi": "Bonjour ! Comment puis-je vous aider ?",
            r"aide|help|assistance": "Je peux vous aider avec :\n- La gestion des notifications\n- La configuration des webhooks\n- Les statistiques\nQue souhaitez-vous faire ?",
            r"merci|thanks": "Je vous en prie ! N'hésitez pas si vous avez d'autres questions.",
            r"bye|au revoir|à bientôt": "Au revoir ! N'hésitez pas à revenir si vous avez besoin d'aide.",
            r"statistiques|stats": "Je peux vous montrer les statistiques de vos notifications. Voulez-vous voir les statistiques globales ou par type ?",
            r"webhook|webhooks": "Je peux vous aider à configurer vos webhooks. Voulez-vous créer un nouveau webhook ou modifier un existant ?",
            r"notification|notifications": "Je peux vous aider à gérer vos notifications. Voulez-vous créer une nouvelle notification ou consulter l'historique ?"
        }
        self._compiled_patterns = {re.compile(pattern): response for pattern, response in self._patterns.items()}
        self.history: List[ChatMessage] = []
        self.max_history_size = 100
        self._is_typing = False
        self._typing_task = None

    def get_welcome_message(self) -> ChatMessage:
        """Retourne un message de bienvenue aléatoire."""
        import random
        return ChatMessage(
            content=random.choice(self.welcome_messages),
            sender=self.name,
            type="welcome"
        )

    async def process_message(self, message: str) -> List[ChatMessage]:
        """Traite un message utilisateur et retourne la réponse."""
        if not message or len(message) > 1000:
            raise ValueError("Message invalide")

        # Ajout du message utilisateur
        user_message = ChatMessage(content=message, sender="user")
        self.history.append(user_message)
        
        # Simulation de la frappe
        self._is_typing = True
        if self._typing_task:
            self._typing_task.cancel()
        
        # Calcul du temps de frappe basé sur la longueur de la réponse
        response = self._generate_response(message)
        typing_duration = min(len(response) * self.typing_speed, 2.0)  # Max 2 secondes
        
        # Attente simulée
        await asyncio.sleep(typing_duration)
        
        # Ajout de la réponse du bot
        bot_message = ChatMessage(content=response, sender=self.name)
        self.history.append(bot_message)
        self._is_typing = False
        
        return [user_message, bot_message]

    def _generate_response(self, message: str) -> str:
        """Génère une réponse appropriée au message de l'utilisateur."""
        message = message.lower().strip()

        for pattern, response in self._compiled_patterns.items():
            if pattern.search(message):
                return response

        return "Je ne suis pas sûr de comprendre. Pouvez-vous reformuler votre question ?"

    def get_history(self) -> List[ChatMessage]:
        """Retourne l'historique des messages."""
        return self.history

    def clear_history(self) -> None:
        """Efface l'historique des messages."""
        self.history = []
        self._is_typing = False
        if self._typing_task:
            self._typing_task.cancel()
        log_security_event(
            "chat_history_cleared",
            "Chat history has been cleared",
            "INFO"
        )

    def get_typing_indicator(self) -> Dict[str, Any]:
        """Retourne les informations pour l'indicateur de frappe."""
        return {
            "is_typing": self.is_typing(),
            "sender": self.name,
            "duration": self.typing_speed
        }

    def is_typing(self) -> bool:
        """Retourne l'état actuel de l'indicateur de frappe."""
        return self._is_typing

# Instance globale du chatbot
chatbot = ChatBot() 