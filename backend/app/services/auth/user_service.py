from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logger import logger
from app.models.user import User
from app.schemas import UserSchema
from app.schemas.auth import CompleteProfileRequest
from app.services.trace_service import TraceService


class UserService:

    @staticmethod
    async def get_or_create_user(
            db: AsyncSession,
            email: str,
            prenom: str,
            nom: str,
            google_id: str
    ) -> tuple[UserSchema, bool]:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if user:
            return UserSchema.model_validate(user), False

        new_user = User(email=email, prenom=prenom, nom=nom, google_id=google_id)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        await TraceService.record_trace(
            db,
            f"{prenom} {nom}",
            "USER_CREATED",
            "Creation d'un nouvel utilisateur",
            {"user_id": new_user.id, "email": email},
        )

        return UserSchema.model_validate(new_user), True

    @staticmethod
    async def create_user(
            db: AsyncSession,
            email: str,
            prenom: str,
            nom: str,
            password: str
    ) -> UserSchema:

        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if user:
            raise HTTPException(status_code=409, detail="Utilisateur déjà existant.")

        new_user = User(email=email, prenom=prenom, nom=nom, password=password)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        await TraceService.record_trace(
            db,
            f"{prenom} {nom}",
            "USER_CREATED",
            "Creation d'un nouvel utilisateur",
            {"user_id": new_user.id, "email": email},
        )

        return UserSchema.model_validate(new_user)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserSchema:
        logger.info(f"Récupération de l'utilisateur avec l'id {user_id}")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="❌ Utilisateur non trouvé")

        return UserSchema.model_validate(user)

    @staticmethod
    async def ensure_mail_available(db: AsyncSession, mail: str) -> bool:
        logger.info(f"[MAIL CHECK] Vérification de l'existence de l'email : {mail}")

        result = await db.execute(select(User).where(User.email == mail))
        user: User | None = result.scalars().first()

        if user:
            if user.password:
                logger.info("[MAIL CHECK] ❌ Email déjà utilisé avec un mot de passe")
                raise HTTPException(status_code=409)
            if user.google_id:
                logger.info("[MAIL CHECK] ❌ Email déjà utilisé avec Google")
                raise HTTPException(status_code=423)
            return False
        else:
            logger.info("[MAIL CHECK] ✅ Email disponible")
            return True

    @staticmethod
    async def complete_user( db: AsyncSession, user_id: int, request: CompleteProfileRequest) -> UserSchema:

        result = await db.execute(select(User).where(User.id == user_id))
        existing: User = result.scalars().first()

        if not existing:
            raise HTTPException(status_code=404, detail="❌ Utilisateur non trouvé")

        old_name = existing.nom
        old_given_name = existing.prenom

        existing.nom = request.family_name
        existing.prenom = request.given_name

        await TraceService.record_trace(
            db,
            f"{existing.nom} {existing.prenom}",
            "USER_COMPLETE",
            "Complétion d'un nouvel utilisateur",
            {"user_id": user_id, "email": existing.email, "ancien_prenom": old_given_name, "ancien_nom": old_name},
        )

        await db.commit()
        await db.refresh(existing)

        return UserSchema.model_validate(existing)

    @staticmethod
    async def reset_password( db: AsyncSession, mail: str, new_password: str) -> UserSchema:

        result = await db.execute(select(User).where(User.email == mail))
        existing: User = result.scalars().first()

        if not existing:
            raise HTTPException(status_code=404, detail="❌ Utilisateur non trouvé")

        existing.password = new_password
        await TraceService.record_trace(
            db,
            f"{existing.nom} {existing.prenom}",
            "RESET_PASSWORD",
            "Réinitialisation du mot de passe",
            {"user_id": existing.id, "email": existing.email, "changement": "✔ mot de passe mis à jour"},
        )

        await db.commit()
        await db.refresh(existing)

        return UserSchema.model_validate(existing)


    @staticmethod
    async def get_user_by_mail(db: AsyncSession, mail: str) -> User:
        logger.info(f"Récupération de l'utilisateur avec l'email {mail}")

        result = await db.execute(select(User).where(User.email == mail))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="❌ Utilisateur non trouvé")

        return user

    @staticmethod
    async def change_password(db: AsyncSession, mail: str, password: str) -> User:

        user: User = await UserService.get_user_by_mail(db, mail)

        if not user :
            raise HTTPException(status_code=401, detail="❌ Utilisateur non trouvé")

        user.password = password
        await db.commit()

        return user