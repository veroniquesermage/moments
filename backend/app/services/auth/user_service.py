from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.services.trace_service import TraceService


class UserService:

    @staticmethod
    async def get_or_create_user(db: AsyncSession, email: str, prenom: str, nom: str, google_id: str) -> User:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if user:
            return user

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

        return new_user

