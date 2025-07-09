from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.core.logger import logger
from app.models.user import User
from app.schemas import UserSchema
from app.services.trace_service import TraceService


class UserService:

    @staticmethod
    async def get_or_create_user(db: AsyncSession, email: str, prenom: str, nom: str, google_id: str) -> UserSchema:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if user:
            return UserSchema.model_validate(user)

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

        return UserSchema.model_validate(new_user)


    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> UserSchema:
        logger.info(f"Récupération de l'utilisateur avec l'id {user_id}")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="❌ Utilisateur non trouvé")

        return UserSchema.model_validate(user)


