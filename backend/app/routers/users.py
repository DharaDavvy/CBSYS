"""
User endpoints — profile, transcript, and chat-history management.

All routes require a valid Bearer token (Firebase or dev-mode).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.routers.auth import verify_token
from app.models import firebase as fb
from app.models.schemas import (
    UserCreate,
    UserResponse,
    ProfileUpdate,
    ProfileResponse,
    TranscriptUpdate,
    TranscriptResponse,
    ChatHistoryResponse,
    ChatMessageOut,
)

router = APIRouter(prefix="/users", tags=["Users"])


# ── User document ────────────────────────────────────────────────────

@router.post("/me", response_model=UserResponse)
async def create_or_update_user(body: UserCreate, uid: str = Depends(verify_token)):
    """Create or update the current user's basic info."""
    data = body.model_dump()
    fb.save_user(uid, data)
    return UserResponse(**data)


@router.get("/me", response_model=UserResponse)
async def get_current_user(uid: str = Depends(verify_token)):
    """Return the current user's basic info."""
    user = fb.get_user(uid)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserResponse(**user)


# ── Profile (interests, skills, target career) ──────────────────────

@router.put("/me/profile", response_model=ProfileResponse)
async def update_profile(body: ProfileUpdate, uid: str = Depends(verify_token)):
    """Create or update the current user's profile."""
    data = body.model_dump()
    fb.save_profile(uid, data)
    return ProfileResponse(**data)


@router.get("/me/profile", response_model=ProfileResponse)
async def get_profile(uid: str = Depends(verify_token)):
    """Return the current user's profile."""
    profile = fb.get_profile(uid)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return ProfileResponse(**profile)


# ── Transcript ───────────────────────────────────────────────────────

@router.put("/me/transcript", response_model=TranscriptResponse)
async def update_transcript(body: TranscriptUpdate, uid: str = Depends(verify_token)):
    """Upload or overwrite the current user's transcript."""
    courses = [c.model_dump() for c in body.courses]
    fb.save_transcript(uid, courses)
    return TranscriptResponse(courses=body.courses)


@router.get("/me/transcript", response_model=TranscriptResponse)
async def get_transcript(uid: str = Depends(verify_token)):
    """Return the current user's transcript."""
    courses = fb.get_transcript(uid)
    return TranscriptResponse(courses=courses)


# ── Chat History ─────────────────────────────────────────────────────

@router.get("/me/chat-history", response_model=ChatHistoryResponse)
async def get_chat_history(uid: str = Depends(verify_token)):
    """Return the full chat history for the current user."""
    messages = fb.get_chat_history(uid)
    return ChatHistoryResponse(
        messages=[ChatMessageOut(**m) for m in messages],
    )


@router.delete("/me/chat-history", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_history(uid: str = Depends(verify_token)):
    """Clear all chat history for the current user."""
    fb.clear_chat_history(uid)
