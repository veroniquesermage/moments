from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.google_jwt import verify_google_id_token
from app.core.jwt import create_access_token
from app.core.logger import logger
from app.models import RefreshToken, User
from app.schemas import UserSchema
from app.schemas.auth import GoogleAuthRequest, AuthResponse, CompleteProfileRequest
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

        user, is_new_user = await UserService.get_or_create_user(
            db=db,
            email=payload["email"],
            prenom=payload.get("given_name", ""),
            nom=payload.get("family_name", ""),
            google_id=payload["sub"]
        )

        return await AuthService.create_tokens(db, user, request.remember_me, is_new_user)

    @staticmethod
    async def create_tokens(db: AsyncSession, user: UserSchema, remember_me: bool, is_new_user=False) -> JSONResponse:

        jti = str(uuid4())
        refresh_payload = {
            "sub": str(user.id),
            "jti": jti,
            "remember_me": remember_me
        }

        refresh_token_stored: RefreshToken = await RefreshTokenService.store_refresh_token(db, user.id, jti)
        refresh_token = RefreshTokenService.create_refresh_token(refresh_payload, refresh_token_stored.expires_at)

        access_token_duration = now_paris() + timedelta(minutes=30)
        access_token = create_access_token(data={"sub": str(user.id)}, expires_at=access_token_duration)

        # Création de la réponse JSON avec cookies
        content = jsonable_encoder(AuthResponse(profile=user, is_new_user=is_new_user))
        response = JSONResponse(content=content)
        if remember_me:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=settings.is_prod,
                samesite="strict",
                max_age=60 * 60 * 24 * 30
            )
        else:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                secure=settings.is_prod,
                samesite="strict"
            )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=False,
            secure=settings.is_prod,
            samesite="lax",
            max_age=60
        )

        return response

    @staticmethod
    async def refresh_access_token(db: AsyncSession,
                                   request: Request
                                   ) -> JSONResponse:

        token = request.cookies.get("refresh_token")

        payload = RefreshTokenService.decode_refresh_token(token)
        user_id: int = int(payload.get("sub"))
        jti: str = payload.get("jti")
        remember_me: bool = payload.get("remember_me")

        if await RefreshTokenService.is_refresh_token_valid(db, jti, user_id):
            user = await UserService.get_user_by_id(db, int(user_id))
            await RefreshTokenService.revoke_refresh_token(db, jti, user_id)

            return await AuthService.create_tokens(
                db, UserSchema.model_validate(user), remember_me
            )
        else:
            logger.info(f"Refresh invalide pour le jti {jti} et l'utilisateur {user_id}")
            raise HTTPException(status_code=401, detail="Refresh token invalide.")

    @staticmethod
    async def logout(db: AsyncSession, request: Request) -> JSONResponse:
        token = request.cookies.get("refresh_token")
        if token:
            try:
                payload = RefreshTokenService.decode_refresh_token(token)
                user_id: int = int(payload.get("sub"))
                jti: str = payload.get("jti")
                await RefreshTokenService.revoke_refresh_token(db, jti, user_id)
            except Exception:
                pass

        response = JSONResponse(content={"message": "Déconnexion réussie"})
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        return response

    @staticmethod
    async def complete_profile( db: AsyncSession, current_user: User, request: CompleteProfileRequest) -> UserSchema:

        logger.info(f"Completion du nouvel utilisateur {current_user.id}")
        return await UserService.complete_user(db, current_user.id, request)


