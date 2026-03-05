"""
Authentication helpers — Firebase token verification middleware.

Usage as a FastAPI dependency:
    @router.post("/protected")
    async def protected(uid: str = Depends(verify_token)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Firebase Admin imports (active once Phase 3 initialises the SDK)
# For now we provide a placeholder that extracts the user_id from the
# request body so Phase 2 endpoints work without Firebase set up.

_bearer_scheme = HTTPBearer(auto_error=False)

# Set to True once Firebase Admin SDK is initialised in firebase.py
_firebase_ready = False


def mark_firebase_ready():
    """Called from the lifespan handler after Firebase init succeeds."""
    global _firebase_ready
    _firebase_ready = True


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """Validate the Firebase ID token and return the user's UID.

    While Firebase is not yet configured (Phase 2 dev mode), this
    accepts any non-empty Bearer token and treats it as UID directly
    so that the endpoints can be tested easily.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )

    token = credentials.credentials

    if _firebase_ready:
        # Real verification with Firebase Admin SDK
        try:
            from firebase_admin import auth as fb_auth  # type: ignore

            decoded = fb_auth.verify_id_token(token)
            return decoded["uid"]
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Firebase token: {exc}",
            )
    else:
        # Dev-mode passthrough: treat token value as uid
        return token
