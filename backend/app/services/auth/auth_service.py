from sqlalchemy.ext.asyncio.session import AsyncSession

from app.core.google_jwt import verify_google_id_token
from app.core.jwt import create_access_token
from app.schemas.auth import GoogleAuthRequest, AuthResponse
from app.services.auth.google_auth_service import exchange_code_for_tokens
from app.services.auth.user_service import get_or_create_user


async def authenticate_google_user(request: GoogleAuthRequest, db: AsyncSession) -> AuthResponse:
    token_data = await exchange_code_for_tokens(
        code=request.code,
        code_verifier=request.code_verifier
    )

    payload = await verify_google_id_token(token_data["id_token"])

    user = await get_or_create_user(
        db=db,
        email=payload["email"],
        prenom=payload["given_name"],
        nom=payload["family_name"],
        google_id=payload["sub"]
    )

    token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        token=token,
        profile=user
    )
