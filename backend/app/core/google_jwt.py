from jose import jwt
import httpx
from fastapi import HTTPException
from starlette import status

from app.core.config import settings

GOOGLE_JWK_URL = settings.jwk_uri


async def verify_google_id_token(id_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        jwks = (await client.get(GOOGLE_JWK_URL)).json()

    try:
        payload = jwt.decode(
            token=id_token,
            key=jwks,
            algorithms=["RS256"],
            audience=settings.google_client_id,
            options={
                "verify_iss": False,  # désactive la vérif d'issuer
                "verify_at_hash": False
            } # pour simplifier
        )
        return payload

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="id_token Google invalide"
        )
