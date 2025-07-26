import asyncio
from datetime import timedelta, datetime
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import HTTPException, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio.session import AsyncSession
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.google_jwt import verify_google_id_token
from app.core.jwt import create_access_token
from app.core.logger import logger
from app.models import RefreshToken, User
from app.schemas.auth import GoogleAuthRequest, AuthResponse, CompleteProfileRequest, RegisterRequest
from app.schemas.auth.change_password import ChangePassword
from app.schemas.auth.login_request import LoginRequest
from app.schemas.auth.reset_password_payload import ResetPasswordPayload
from app.schemas.user import UserSchema
from app.services import UserGroupService
from app.services.auth.google_auth_service import exchange_code_for_tokens
from app.services.auth.login_attempt_service import LoginAttemptService
from app.services.auth.user_service import UserService
from app.services.mailing.mail_service import MailService
from app.services.token_service import TokenService
from app.utils.date_helper import now_paris, is_expired
from app.utils.password_utils import PasswordUtils


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

        refresh_token_stored: RefreshToken = await TokenService.store_refresh_token(db, user.id, jti)
        refresh_token = TokenService.create_refresh_token(refresh_payload, refresh_token_stored.expires_at)

        access_token_duration = now_paris() + timedelta(minutes=30)
        access_payload = {
            "sub": str(user.id),
            "exp": access_token_duration,
        }

        access_token = create_access_token(data=access_payload, expires_at=access_token_duration)

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

        payload = TokenService.decode_refresh_token(token)
        user_id: int = int(payload.get("sub"))
        jti: str = payload.get("jti")
        remember_me: bool = payload.get("remember_me")

        if await TokenService.is_refresh_token_valid(db, jti, user_id):
            user = await UserService.get_user_by_id(db, int(user_id))
            await TokenService.revoke_refresh_token(db, jti, user_id)

            return await AuthService.create_tokens(
                db, UserSchema.from_user(user), remember_me
            )
        else:
            logger.info(f"Refresh invalide pour le jti {jti} et l'utilisateur {user_id}")
            raise HTTPException(status_code=401, detail="Refresh token invalide.")

    @staticmethod
    async def logout(db: AsyncSession, request: Request) -> JSONResponse:
        token = request.cookies.get("refresh_token")
        if token:
            try:
                payload = TokenService.decode_refresh_token(token)
                user_id: int = int(payload.get("sub"))
                jti: str = payload.get("jti")
                await TokenService.revoke_refresh_token(db, jti, user_id)
            except Exception:
                pass

        response = JSONResponse(content={"message": "Déconnexion réussie"})
        response.delete_cookie(key="access_token", path="/")
        response.delete_cookie(key="refresh_token", path="/")
        return response

    @staticmethod
    async def complete_profile(
            db: AsyncSession,
            current_user: User,
            request: CompleteProfileRequest) -> UserSchema:

        logger.info(f"Completion du nouvel utilisateur {current_user.id}")
        return await UserService.complete_user(db, current_user.id, request)

    @staticmethod
    async def check_mail(db: AsyncSession, login_request: LoginRequest):
        mail_valid: bool = await UserService.ensure_mail_available(db, login_request.email)

        if mail_valid :
            password = PasswordUtils.hash_password(login_request.password)

            token = TokenService.generate_signup_token(login_request.email, password, login_request.remember_me)

            await MailService.send_validation_email(db, login_request.email, token)

    @staticmethod
    async def authenticate_credentials_user(request: RegisterRequest, db: AsyncSession) -> JSONResponse:
        try:
            token_data = TokenService.decode_signup_token(request.token)
        except Exception:
            raise HTTPException(status_code=401, detail="Token invalide.")

        expire: datetime = datetime.fromtimestamp(token_data["exp"], tz=ZoneInfo("Europe/Paris"))

        if is_expired(expire) :
            raise HTTPException(status_code=401, detail="Token expiré.")

        email = token_data["sub"]
        password = token_data["hashed_pw"]
        remember_me = token_data["remember_me"]
        user = await UserService.create_user(
            db=db,
            email=email,
            prenom=request.prenom,
            nom=request.nom,
            password=password
        )

        return await AuthService.create_tokens(db, user, remember_me, True)

    @staticmethod
    async def login_with_credentials( request: LoginRequest, db: AsyncSession) -> JSONResponse:

        if await LoginAttemptService.is_blocked(db, request.email):
            raise HTTPException(status_code=403, detail="Compte bloqué.")

        user = await AuthService.check_user(db, request.email)

        if user.password is None:
            raise HTTPException(status_code=409, detail="Cet adresse mail est bien en base mais avec un autre type de connexion.")

        matching_password: bool = PasswordUtils.verify_password(request.password, user.password)

        if not matching_password:
            await LoginAttemptService.increment_attempt(db, request.email)
            raise HTTPException(status_code=401, detail="Mauvais mot de passe.")

        await LoginAttemptService.reset_attempts(db, request.email)
        return await AuthService.create_tokens(db, UserSchema.from_user(user), request.remember_me, False)

    @staticmethod
    async def change_password(db: AsyncSession, current_user: User, request: ChangePassword):

        matching_old_password: bool = PasswordUtils.verify_password(request.old_password, current_user.password)

        if not matching_old_password:
            raise HTTPException(status_code=401, detail="Mauvais mot de passe.")

        password_hash = PasswordUtils.hash_password(request.new_password)

        await UserService.change_password(db, current_user.email, password_hash)

    @staticmethod
    async def request_password_reset(db: AsyncSession, mail: str):
        await AuthService.check_user(db, mail)

        token: str = TokenService.generate_password_token(mail)

        await MailService.send_token_password(db, mail, token)

    @staticmethod
    async def verify_reset_token(db: AsyncSession, token: str) -> str :

        try:
            token_data = TokenService.decode_password_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Token invalide.")

        expire: datetime = datetime.fromtimestamp(token_data["exp"], tz=ZoneInfo("Europe/Paris"))

        if is_expired(expire) :
            raise HTTPException(status_code=401, detail="Token expiré.")

        return token_data['sub']

    @staticmethod
    async def reset_password( db: AsyncSession, request: ResetPasswordPayload) -> JSONResponse:

        try:
            token_data = TokenService.decode_password_token(request.token)
        except Exception:
            raise HTTPException(status_code=401, detail="Token invalide.")

        new_password = PasswordUtils.hash_password(request.new_password)
        user: UserSchema = await UserService.reset_password(db, token_data['sub'], new_password)

        return await AuthService.create_tokens(db, user, False, False)

    @staticmethod
    async def check_user(db: AsyncSession, mail: str) -> User:
        user: User = await UserService.get_user_by_mail(db, mail)
        if not user:
            await asyncio.sleep(1)  # Pour égaliser avec le temps de vérif du hash
            raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

        return user

    @staticmethod
    async def switch_to_tiers(db: AsyncSession, user_tiers_id: int, current_user: User, group_id: int) -> JSONResponse:
        user_tiers: User = await UserService.get_user_by_id(db, user_tiers_id)

        if not user_tiers.gere_par == current_user.id :
            raise HTTPException(status_code=401, detail="utilisateur non géré par le current_user.")

        user_group = await UserGroupService.get_user_group(db, user_tiers_id, group_id)
        if not user_group:
            raise HTTPException(status_code=401, detail="Ce compte tiers n'appartient pas au groupe courant.")

        return await AuthService.create_tokens(db, UserSchema.from_user(user_tiers), False, False)

    @staticmethod
    async def switch_to_parent(db: AsyncSession, current_user: User, group_id: int) -> JSONResponse:
        user_parent: User = await UserService.get_user_by_id(db, current_user.gere_par)

        user_group = await UserGroupService.get_user_group(db, user_parent.id, group_id)
        if not user_group:
            raise HTTPException(status_code=401, detail="Ce compte tiers n'appartient pas au groupe courant.")

        return await AuthService.create_tokens(db, UserSchema.from_user(user_parent), False, False)








