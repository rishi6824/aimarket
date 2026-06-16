"""
Chat Router — /api/chat
"""
from fastapi import APIRouter, HTTPException
from models import ChatRequest, ChatResponse
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agents.marketing_chat_agent import chat_with_agent
from services import supabase_client
import uuid

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """Chat with ARIA, the marketing AI assistant."""
    try:
        response = await chat_with_agent(req)

        # Persist messages to Supabase
        try:
            session_id = response.session_id
            await supabase_client.insert("chat_messages", {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "role": "user",
                "content": req.message,
            })
            await supabase_client.insert("chat_messages", {
                "id": str(uuid.uuid4()),
                "session_id": session_id,
                "role": "assistant",
                "content": response.reply,
            })
        except Exception:
            pass  # DB persistence failure shouldn't break chat

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """Fetch chat history for a session."""
    try:
        messages = await supabase_client.select("chat_messages", {"session_id": session_id}, limit=100)
        return {"session_id": session_id, "messages": list(reversed(messages))}
    except Exception as e:
        return {"session_id": session_id, "messages": [], "error": str(e)}
