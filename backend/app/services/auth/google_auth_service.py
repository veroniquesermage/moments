import httpx
from fastapi import HTTPException
from starlette import status

from app.core.config import settings

GOOGLE_TOKEN_ENDPOINT = settings.google_token_endpoint
GOOGLE_CLIENT_ID = settings.google_client_id
GOOGLE_CLIENT_SECRET = settings.google_client_secret
REDIRECT_URI = settings.google_redirect_uri

async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Échec lors de l'échange avec Google"
        )

    return response.json()
