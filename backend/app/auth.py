"""Hitelesítési modul az API végpontok védelmére."""

from fastapi import Header, HTTPException, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.config import settings

# Fejlécek támogatása: 'X-API-Key: ...' és 'Authorization: Bearer ...'
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
bearer_scheme = HTTPBearer(auto_error=False)


async def verify_api_key(
    api_key_header_val: Optional[str] = Security(api_key_header),
    bearer_auth: Optional[HTTPAuthorizationCredentials] = Security(bearer_scheme),
) -> str:
    """
    Ellenőrzi a kliens által küldött API kulcsot.
    Elfogadja mind az 'X-API-Key' fejlécet, mind az 'Authorization: Bearer <token>' fejlécet.
    """
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
