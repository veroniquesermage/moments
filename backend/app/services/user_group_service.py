
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from app.models import User, UserGroup
from app.schemas import UserSchema


class UserGroupService:

    @staticmethod
    async def get_users( db: AsyncSession,
                         current_user: User,
                         groupId: int) -> list[UserSchema]:
        results = (await db.execute(
            select(User)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(
                UserGroup.groupe_id == groupId,
                User.id != current_user.id
            )
        )).scalars().all()
        return [UserSchema.model_validate(result) for result in results]

    @staticmethod
    async def get_all_my_users( db: AsyncSession,
                                current_user: User) -> list[UserSchema]:
        results = (await db.execute(
            select(User)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(
                UserGroup.groupe_id.in_(
                    select(UserGroup.groupe_id)
                    .where(UserGroup.utilisateur_id == current_user.id)
                ),
                User.id != current_user.id
            )
        )).scalars().all()

        return [UserSchema.model_validate(result) for result in results]
