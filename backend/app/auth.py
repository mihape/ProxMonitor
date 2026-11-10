from typing import Optional
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPAuthorizationCredentials, HTTPBearer
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    api_key_header_val: Optional[str] = Security(api_key_header),
    bearer_auth: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
    """API-kulcs hitelesítése 'X-API-Key' vagy 'Authorization: Bearer' fejlécből."""
    token_to_check = None

    if api_key_header_val:
        token_to_check = api_key_header_val.strip()
    elif bearer_auth and bearer_auth.credentials:
        token_to_check = bearer_auth.credentials.strip()

    if not token_to_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hitelesítés szükséges: Hiányzó API kulcs (X-API-Key vagy Authorization Bearer fejléc).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_to_check != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Érvénytelen API kulcs.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_to_check
