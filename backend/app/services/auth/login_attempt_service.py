from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.login_attempts import LoginAttempts
from app.utils.date_helper import now_paris


class LoginAttemptService:

    MAX_ATTEMPTS = 5
    BLOCK_DURATION = timedelta(minutes=15)

    @staticmethod
    async def  is_blocked(db: AsyncSession, email: str) -> bool:
        record = await db.scalar(
            select(LoginAttempts).where(LoginAttempts.email == email)
        )
        if not record:
            return False

        if record.tentatives >= LoginAttemptService.MAX_ATTEMPTS:
            return record.derniere_tentative + LoginAttemptService.BLOCK_DURATION > now_paris()
        return False

    @staticmethod
    async def increment_attempt(db: AsyncSession, email: str):
        record = await db.scalar(
            select(LoginAttempts).where(LoginAttempts.email == email)
        )
        if record:
            record.increment()
            record.derniere_tentative = now_paris()
        else:
            record = LoginAttempts(
                email=email,
                tentatives=1,
                derniere_tentative=now_paris()
            )
            db.add(record)
        await db.commit()

    @staticmethod
    async def reset_attempts(db: AsyncSession, email: str):
        record = await db.scalar(
            select(LoginAttempts).where(LoginAttempts.email == email)
        )
        if record:
            await db.delete(record)
            await db.commit()
