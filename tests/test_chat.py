import pytest
from fastapi.testclient import TestClient
from app.core.chat import ChatBot, ChatMessage
from app.main import app
import asyncio

client = TestClient(app)

def test_chat_message_creation():
    """Teste la création d'un message."""
    message = ChatMessage(content="Test message", sender="user")
    assert message.content == "Test message"
    assert message.sender == "user"
    assert message.type == "text"
    assert message.timestamp is not None

def test_chatbot_initialization():
    """Teste l'initialisation du chatbot."""
    bot = ChatBot()
    assert bot.name == "Echo"
    assert bot.avatar == "🤖"
    assert len(bot.welcome_messages) > 0
    assert len(bot._patterns) > 0
    assert len(bot._compiled_patterns) > 0
    assert not bot.is_typing()

def test_welcome_message():
    """Teste la génération du message de bienvenue."""
    bot = ChatBot()
    welcome = bot.get_welcome_message()
    assert isinstance(welcome, ChatMessage)
    assert welcome.sender == bot.name
    assert welcome.type == "welcome"
    assert welcome.content in bot.welcome_messages

@pytest.mark.asyncio
async def test_message_processing():
    """Teste le traitement des messages."""
    bot = ChatBot()
    messages = await bot.process_message("bonjour")
    assert len(messages) == 2
    assert messages[0].sender == "user"
    assert messages[1].sender == bot.name
    assert "bonjour" in messages[1].content.lower()

@pytest.mark.asyncio
async def test_response_generation():
    """Teste la génération des réponses."""
    bot = ChatBot()
    response = bot._generate_response("aide")
    assert "aide" in response.lower()
    assert "notification" in response.lower() or "webhook" in response.lower()

@pytest.mark.asyncio
async def test_conversation_history():
    """Teste la gestion de l'historique des conversations."""
    bot = ChatBot()
    await bot.process_message("bonjour")
    history = bot.get_history()
    assert len(history) == 2
    assert history[0].content == "bonjour"
    assert history[1].sender == bot.name

def test_history_clearing():
    """Teste l'effacement de l'historique."""
    bot = ChatBot()
    bot.history = [ChatMessage("test", "user")]
    bot.clear_history()
    assert len(bot.get_history()) == 0
    assert not bot.is_typing()

@pytest.mark.asyncio
async def test_typing_indicator():
    """Teste l'indicateur de frappe."""
    bot = ChatBot()
    assert not bot.is_typing()
    
    # Démarre le traitement d'un message
    task = asyncio.create_task(bot.process_message("test"))
    await asyncio.sleep(0.1)  # Laisse le temps à la tâche de démarrer
    
    # Vérifie que l'indicateur de frappe est actif
    assert bot.is_typing()
    
    # Attend la fin du traitement
    await task
    assert not bot.is_typing()

def test_api_chat_endpoint():
    """Teste l'endpoint de chat."""
    response = client.post("/api/chat", json={"message": "bonjour"})
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 2
    assert data["messages"][0]["sender"] == "user"
    assert data["messages"][1]["sender"] == "Echo"

def test_api_history_endpoint():
    """Teste l'endpoint d'historique."""
    response = client.get("/api/chat/history")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_api_clear_history():
    """Teste l'endpoint d'effacement de l'historique."""
    response = client.delete("/api/chat/history")
    assert response.status_code == 200
    assert response.json()["message"] == "Historique effacé"

def test_invalid_message():
    """Teste la gestion des messages invalides."""
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 422

def test_message_length_limit():
    """Teste la limite de longueur des messages."""
    long_message = "a" * 1001
    response = client.post("/api/chat", json={"message": long_message})
    assert response.status_code == 422

def test_rate_limiting():
    """Teste la limitation de débit."""
    for _ in range(6):  # Dépassement de la limite de 5 requêtes
        response = client.post("/api/chat", json={"message": "test"})
    assert response.status_code == 429 