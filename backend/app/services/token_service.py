from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from fastapi import HTTPException
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logger import logger
from app.models import RefreshToken
from app.utils.date_helper import is_expired, now_paris


class TokenService:

    SECRET_KEY = settings.jwt_secret
    ALGORITHM = "HS256"
    TZ = ZoneInfo("Europe/Paris")
    EXPIRATION_MINUTES = 30

    @staticmethod
    def create_refresh_token(data: dict, expires_at: datetime) -> str:
        to_encode = data.copy()
        to_encode.update({"exp": expires_at})
        encoded_jwt = jwt.encode(to_encode, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def store_refresh_token(
            db: AsyncSession,
            user_id: int,
            jti: str
    ) -> RefreshToken:

        logger.info(f"Enregistrement refresh token pour l'utilisateur {user_id}")
        expires_at: datetime = (datetime.now(TokenService.TZ) +
                                (timedelta(days=30)))

        logger.info(f"Date d'expiration pour le refresh_token {expires_at}")
        refresh_token = RefreshToken(
            user_id = user_id,
            jti = jti,
            expires_at = expires_at,
        )

        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)

        return refresh_token

    @staticmethod
    async def is_refresh_token_valid(
            db: AsyncSession,
            jti: str,
            user_id: int) -> bool :

        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id,
                        RefreshToken.jti == jti,
                        RefreshToken.is_active == True)

            )

        existing: RefreshToken = result.scalars().first()

        if not existing :
            return False

        if is_expired(existing.expires_at):
            return False

        return True

    @staticmethod
    async def revoke_refresh_token(
            db: AsyncSession,
            jti: str,
            user_id: int):

        logger.info(f"Revocation du refresh_token pour l'utilisateur {user_id}, jti={jti}")

        result = await db.execute(
            select(RefreshToken)
            .where(RefreshToken.user_id == user_id,
                       RefreshToken.jti == jti
            )
        )

        existing: RefreshToken = result.scalars().first()

        if not existing :
            raise HTTPException(
                status_code=404,
                detail="❌ Ce jti n'existe pas pour cet utilisateur"
            )

        existing.is_active = False
        await db.commit()

    @staticmethod
    def decode_refresh_token(token: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[TokenService.ALGORITHM]
            )
            return payload
        except JWTError:
            raise HTTPException(status_code=401, detail="❌ Token corrompu ou expiré")


    @staticmethod
    def generate_signup_token(email: str, hashed_pw: str, remember_me: bool) -> str:
        exp: datetime = now_paris() + timedelta(minutes=TokenService.EXPIRATION_MINUTES)
        to_encode = {"sub": email, "hashed_pw": hashed_pw, "remember_me": remember_me, "exp": exp}
        return jwt.encode(to_encode, TokenService.SECRET_KEY, algorithm=TokenService.ALGORITHM)

    @staticmethod
    def decode_signup_token(token: str) -> dict:
        return jwt.decode(token, TokenService.SECRET_KEY, algorithms=[TokenService.ALGORITHM])