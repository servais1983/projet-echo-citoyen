import pytest
from unittest.mock import Mock, patch
from echo_chatbot import EchoChatbot

@pytest.fixture
def chatbot():
    return EchoChatbot()

@pytest.fixture
def mock_nlp_service():
    with patch('requests.post') as mock_post:
        mock_post.return_value.json.return_value = {
            "intent": "greeting",
            "confidence": 0.95,
            "entities": {}
        }
        mock_post.return_value.status_code = 200
        yield mock_post

def test_chatbot_initialization(chatbot):
    """Test l'initialisation du chatbot"""
    assert chatbot is not None
    assert hasattr(chatbot, 'conversation_generator')
    assert hasattr(chatbot, 'stt')

def test_create_conversation(chatbot):
    """Test la création d'une nouvelle conversation"""
    user_id = "test_user"
    conversation_id = chatbot.create_conversation(user_id)
    
    assert conversation_id in chatbot.conversations
    assert chatbot.conversations[conversation_id]["user_id"] == user_id
    assert "messages" in chatbot.conversations[conversation_id]
    assert "context" in chatbot.conversations[conversation_id]

def test_add_message(chatbot):
    """Test l'ajout d'un message à une conversation"""
    user_id = "test_user"
    conversation_id = chatbot.create_conversation(user_id)
    message = "Bonjour"
    
    chatbot.add_message(conversation_id, message, "user")
    
    assert len(chatbot.conversations[conversation_id]["messages"]) == 1
    assert chatbot.conversations[conversation_id]["messages"][0]["content"] == message
    assert chatbot.conversations[conversation_id]["messages"][0]["sender"] == "user"

def test_process_user_message(chatbot, mock_nlp_service):
    """Test le traitement d'un message utilisateur"""
    user_id = "test_user"
    message = "Bonjour"
    
    response = chatbot.process_user_message(user_id, message)
    
    assert response is not None
    assert "conversation_id" in response
    assert "response" in response
    assert "status" in response
    assert response["status"] == "success"

def test_check_urgency(chatbot):
    """Test la détection d'urgence"""
    # Test avec une demande non urgente
    non_urgent = {
        "intent": "information",
        "confidence": 0.8,
        "category": "general"
    }
    assert not chatbot.check_urgency(non_urgent)
    
    # Test avec une demande urgente
    urgent = {
        "intent": "urgence",
        "confidence": 0.9,
        "category": "securite"
    }
    assert chatbot.check_urgency(urgent)

@pytest.mark.asyncio
async def test_voice_to_text(chatbot):
    """Test la conversion voix vers texte"""
    with patch('speech_recognition.Recognizer.recognize_google') as mock_recognize:
        mock_recognize.return_value = "Bonjour"
        result = chatbot.voice_to_text("test_audio.wav")
        assert result == "Bonjour"

def test_text_to_voice(chatbot):
    """Test la conversion texte vers voix"""
    with patch('gtts.gTTS.save') as mock_save:
        result = chatbot.text_to_voice("Bonjour")
        assert result == "response.mp3"
        mock_save.assert_called_once() 