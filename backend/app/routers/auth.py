"""
Authentication helpers — Firebase token verification middleware.

Usage as a FastAPI dependency:
    @router.post("/protected")
    async def protected(uid: str = Depends(verify_token)):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.firebase import is_ready as firebase_is_ready, verify_id_token

_bearer_scheme = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> str:
    """Validate the Firebase ID token and return the user's UID.

    When Firebase is not configured, accepts any non-empty Bearer token
    and treats it as UID directly (dev-mode passthrough).
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )

    token = credentials.credentials

    if firebase_is_ready():
        try:
            decoded = verify_id_token(token)
            return decoded["uid"]
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Firebase token: {exc}",
            )
    else:
        # Dev-mode passthrough: treat token value as uid
        return token
