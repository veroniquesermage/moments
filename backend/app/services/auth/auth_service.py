from datetime import timedelta
from uuid import uuid4

from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.google_jwt import verify_google_id_token
from app.core.jwt import create_access_token
from app.models import RefreshToken
from app.schemas.auth import GoogleAuthRequest, AuthResponse
from app.services.auth.google_auth_service import exchange_code_for_tokens
from app.services.auth.user_service import UserService
from app.services.refresh_token_service import RefreshTokenService
from app.utils.date_helper import now_paris


class AuthService:

    @staticmethod
    async def authenticate_google_user(request: GoogleAuthRequest, db: AsyncSession) -> JSONResponse:
        token_data = await exchange_code_for_tokens(
            code=request.code,
            code_verifier=request.code_verifier
        )

        payload = await verify_google_id_token(token_data["id_token"])

        user = await UserService.get_or_create_user(
            db=db,
            email=payload["email"],
            prenom=payload.get("given_name", ""),
            nom=payload.get("family_name", ""),
            google_id=payload["sub"]
        )

        # Création du refresh token
        jti = str(uuid4())
        refresh_payload = {
            "sub": str(user.id),
            "jti": jti
        }

        refresh_token_stored: RefreshToken = await RefreshTokenService.store_refresh_token(db, user.id, jti)
        refresh_token = RefreshTokenService.create_refresh_token(refresh_payload, refresh_token_stored.expires_at)
        refresh_expires = int(refresh_token_stored.expires_at.timestamp())

        # Création de l'access token
        if request.remember_me:
            access_expires_at = now_paris() + timedelta(days=30)
        else:
            access_expires_at = now_paris() + timedelta(minutes=15)

        access_token = create_access_token(data={"sub": str(user.id)}, expires_at=access_expires_at)

        # Création de la réponse JSON avec cookies
        content = jsonable_encoder(AuthResponse(profile=user))
        response = JSONResponse(content=content)

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=settings.is_prod,
            samesite="strict",
            expires=refresh_expires
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=False,
            secure=settings.is_prod,
            samesite="lax",
            expires=int(access_expires_at.timestamp())
        )

        return response
