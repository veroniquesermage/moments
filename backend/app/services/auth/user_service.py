from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.logger import logger
from app.models import UserGroup
from app.models.user import User
from app.schemas import UserSchema, UserTiersResponse
from app.schemas.auth import CompleteProfileRequest
from app.schemas.user_tiers_request import UserTiersRequest
from app.services import UserGroupService
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
            return UserSchema.from_user(user), False

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

        return UserSchema.from_user(new_user), True

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

        return UserSchema.from_user(new_user)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        logger.info(f"Récupération de l'utilisateur avec l'id {user_id}")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="❌ Utilisateur non trouvé")

        return user

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

        return UserSchema.from_user(existing)

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

        return UserSchema.from_user(existing)


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

    @staticmethod
    async def create_managed_account(request: UserTiersRequest, current_user: User, group_id: int, db: AsyncSession) -> UserTiersResponse:

        if current_user.is_compte_tiers:
            raise HTTPException(status_code=403, detail="❌ Un compte-tiers ne peut pas créer de compte-tiers")

        new_user = User( prenom = request.prenom.strip(),
                         nom = request.nom.strip() if request.nom else None,
                         is_compte_tiers= True,
                         gere_par=current_user.id)

        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)

        user_group: UserGroup = await UserGroupService.get_user_group(db, current_user.id, group_id)
        if not user_group:
            raise HTTPException(status_code=403, detail="L'utilisateur n'appartient pas au groupe demandé")
        await UserGroupService.add_user_to_group(db, group_id, new_user.id, request.surnom)

        return UserTiersResponse.model_validate(new_user)

    @staticmethod
    async def get_managed_account(current_user, group_id, db) -> list[UserTiersResponse]:
        result = await db.execute(
            select(User, UserGroup.surnom)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(
                User.gere_par == current_user.id,
                UserGroup.groupe_id == group_id
            )
        )
        rows = result.all()
        managed_accounts = [
            UserTiersResponse(
                id=user.id,
                nom=user.nom,
                prenom=user.prenom,
                surnom=surnom,
                is_compte_tiers=user.is_compte_tiers
            )
            for user, surnom in rows
        ]

        return managed_accounts




