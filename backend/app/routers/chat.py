"""
Chat endpoint — POST /chat

Accepts a user message, runs the RAG pipeline, and returns
the advisor response with source citations.
"""

from fastapi import APIRouter, Depends
from app.models.schemas import ChatRequest, ChatResponse
from app.models.firebase import append_chat_message, get_chat_history
from app.services import rag
from app.routers.auth import verify_token

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat(body: ChatRequest, uid: str = Depends(verify_token)):
    """Ask the Faculty Advisor a curriculum question.

    Persists the user message and advisor response to Firestore.
    """
    mode = body.mode
    if mode == "auto":
        mode = await rag.analyze_intent(body.message)

    if mode == "assessment":
        # Get history before appending the current message
        history = get_chat_history(uid)
        
        # Save user message
        append_chat_message(uid, role="user", content=body.message)
        
        result = await rag.assess_student(body.message, history)
        
        # Save advisor response
        append_chat_message(
            uid,
            role="assistant",
            content=result["response"],
            sources=result["sources"],
        )
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            roadmap_id=result.get("roadmap_id")
        )

    # Save user message
    append_chat_message(uid, role="user", content=body.message)

    result = await rag.ask(body.message)

    # Save advisor response
    append_chat_message(
        uid,
        role="assistant",
        content=result["response"],
        sources=result["sources"],
    )

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
    )
