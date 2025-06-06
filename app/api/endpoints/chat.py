from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List
from ...core.chat import chatbot
from ...core.security import get_current_user, rate_limit
from ...models import User

router = APIRouter()

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)

class ChatMessageResponse(BaseModel):
    content: str
    sender: str
    type: str
    timestamp: str

class ChatResponse(BaseModel):
    messages: List[ChatMessageResponse]

@router.post("/chat", response_model=ChatResponse)
@rate_limit(limit=5, period=60)
async def process_message(request: Request, message: ChatMessageRequest):
    """Traite un message et retourne la réponse."""
    try:
        messages = await chatbot.process_message(message.message)
        return ChatResponse(
            messages=[
                ChatMessageResponse(
                    content=msg.content,
                    sender=msg.sender,
                    type=msg.type,
                    timestamp=msg.timestamp.isoformat()
                )
                for msg in messages
            ]
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors du traitement du message")

@router.get("/chat/history", response_model=List[ChatMessageResponse])
@rate_limit(limit=30, period=60)
async def get_history(request: Request):
    """Récupère l'historique des messages."""
    try:
        messages = chatbot.get_history()
        return [
            ChatMessageResponse(
                content=msg.content,
                sender=msg.sender,
                type=msg.type,
                timestamp=msg.timestamp.isoformat()
            )
            for msg in messages
        ]
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de la récupération de l'historique"
        )

@router.delete("/chat/history")
@rate_limit(limit=10, period=60)
async def clear_history(request: Request):
    """Efface l'historique des messages."""
    try:
        chatbot.clear_history()
        return JSONResponse(
            content={"message": "Historique effacé"},
            status_code=200
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Une erreur est survenue lors de l'effacement de l'historique"
        ) 