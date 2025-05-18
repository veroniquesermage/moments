from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User

async def get_or_create_user(db: AsyncSession, email: str, name: str, google_id: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()

    if user:
        return user

    new_user = User(email=email, name=name, google_id=google_id)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
