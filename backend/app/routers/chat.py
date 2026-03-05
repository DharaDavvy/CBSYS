"""
Chat endpoint — POST /chat

Accepts a user message, runs the RAG pipeline, and returns
the advisor response with source citations.
"""

from fastapi import APIRouter, Depends
from app.models.schemas import ChatRequest, ChatResponse
from app.services import rag
from app.routers.auth import verify_token

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, uid: str = Depends(verify_token)):
    """Ask the Faculty Advisor a curriculum question.

    The *uid* from the verified token is used for chat-history
    storage (Phase 3).  For now, the body.user_id field is also
    accepted for convenience during development.
    """
    result = await rag.ask(body.message)

    # TODO (Phase 3): persist exchange to Firestore chatHistories/{uid}

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
    )
