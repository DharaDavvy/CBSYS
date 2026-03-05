"""
Firebase Admin SDK initialisation & Firestore helpers.
"""

import os
import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from google.api_core.exceptions import PermissionDenied, GoogleAPICallError

from app.config import FIREBASE_CREDENTIALS

# ── Module-level singletons ──────────────────────────────────────────
_db = None
_firebase_initialised = False


def init_firebase() -> None:
    """Initialise the Firebase Admin SDK (call once at startup).

    Requires FIREBASE_CREDENTIALS env var pointing at the
    service-account JSON file.
    """
    global _db, _firebase_initialised

    if _firebase_initialised:
        return

    if not FIREBASE_CREDENTIALS or not os.path.isfile(FIREBASE_CREDENTIALS):
        print(
            "[Firebase] WARNING: FIREBASE_CREDENTIALS not set or file not found — "
            "Firebase features disabled"
        )
        return

    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)
    _db = firestore.client()
    _firebase_initialised = True
    print("[Firebase] Admin SDK initialised successfully")


def is_ready() -> bool:
    """Return True if Firebase was initialised."""
    return _firebase_initialised


def get_db():
    """Return the Firestore client (or None if not initialised)."""
    return _db


# ── Auth helpers ─────────────────────────────────────────────────────

def verify_id_token(token: str) -> dict:
    """Verify a Firebase ID token and return the decoded claims."""
    return auth.verify_id_token(token)


def matric_to_email(matric: str) -> str:
    """Convert a matriculation number to a synthetic Firebase email.

    Example:
        CSC/2024/001 → csc-2024-001@faculty.local
    """
    return matric.strip().lower().replace("/", "-") + "@faculty.local"


# ── Firestore: Users ────────────────────────────────────────────────

def save_user(uid: str, data: dict) -> None:
    """Create or update the users/{uid} document."""
    if not _db:
        return
    try:
        _db.collection("users").document(uid).set(data, merge=True)
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] save_user failed: {e}")


def get_user(uid: str) -> dict | None:
    """Return the users/{uid} document or None."""
    if not _db:
        return None
    try:
        doc: DocumentSnapshot = _db.collection("users").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] get_user failed: {e}")
        return None


# ── Firestore: Profiles ─────────────────────────────────────────────

def save_profile(uid: str, data: dict) -> None:
    """Create or update the profiles/{uid} document."""
    if not _db:
        return
    try:
        _db.collection("profiles").document(uid).set(data, merge=True)
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] save_profile failed: {e}")


def get_profile(uid: str) -> dict | None:
    """Return the profiles/{uid} document or None."""
    if not _db:
        return None
    try:
        doc: DocumentSnapshot = _db.collection("profiles").document(uid).get()
        return doc.to_dict() if doc.exists else None
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] get_profile failed: {e}")
        return None


# ── Firestore: Transcripts ──────────────────────────────────────────

def save_transcript(uid: str, courses: list[dict]) -> None:
    """Overwrite the transcripts/{uid} document with a courses array."""
    if not _db:
        return
    try:
        _db.collection("transcripts").document(uid).set({"courses": courses})
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] save_transcript failed: {e}")


def get_transcript(uid: str) -> list[dict]:
    """Return the courses array from transcripts/{uid}, or []."""
    if not _db:
        return []
    try:
        doc: DocumentSnapshot = _db.collection("transcripts").document(uid).get()
        return doc.to_dict().get("courses", []) if doc.exists else []
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] get_transcript failed: {e}")
        return []


# ── Firestore: Chat Histories ───────────────────────────────────────

def append_chat_message(uid: str, role: str, content: str, sources: list[str] | None = None) -> None:
    """Append a message to the chatHistories/{uid} document.

    Uses Firestore arrayUnion so messages accumulate.
    """
    if not _db:
        return
    from google.cloud.firestore_v1 import ArrayUnion
    from datetime import datetime, timezone

    message = {
        "role": role,
        "content": content,
        "sources": sources or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        ref = _db.collection("chatHistories").document(uid)
        ref.set({"messages": ArrayUnion([message])}, merge=True)
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] append_chat_message failed: {e}")


def get_chat_history(uid: str) -> list[dict]:
    """Return the full message list from chatHistories/{uid}."""
    if not _db:
        return []
    try:
        doc: DocumentSnapshot = _db.collection("chatHistories").document(uid).get()
        return doc.to_dict().get("messages", []) if doc.exists else []
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] get_chat_history failed: {e}")
        return []


def clear_chat_history(uid: str) -> None:
    """Delete all messages in chatHistories/{uid}."""
    if not _db:
        return
    try:
        _db.collection("chatHistories").document(uid).delete()
    except (PermissionDenied, GoogleAPICallError) as e:
        print(f"[Firestore] clear_chat_history failed: {e}")
