from fastapi import HTTPException
from sqlalchemy import select, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import RoleEnum
from app.core.logger import logger
from app.models import User, UserGroup
from app.schemas import UserSchema, UserDisplaySchema


class UserGroupService:

    @staticmethod
    async def get_users(db: AsyncSession,
                        current_user: User,
                        groupId: int) -> list[UserDisplaySchema]:

        results = (await db.execute(
            select(UserGroup)
            .where(UserGroup.groupe_id == groupId,
                   UserGroup.utilisateur_id != current_user.id)
            .options(
                selectinload(UserGroup.utilisateur),
                selectinload(UserGroup.groupe)
            )
        )).scalars().all()

        user_display_schema = [
            UserDisplaySchema(
            id= result.utilisateur.id,
            nom= result.utilisateur.nom,
            prenom= result.utilisateur.prenom,
            surnom= result.surnom if result.surnom else None
            )
            for result in results ]

        return user_display_schema

    @staticmethod
    async def get_all_my_users(db: AsyncSession,
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

    @staticmethod
    async def get_group_admins(
            db: AsyncSession,
            group_id: int) -> Sequence[UserGroup]:

        return (await db.execute(
            select(UserGroup)
            .where(UserGroup.groupe_id == group_id)
            .where(UserGroup.role == RoleEnum.ADMIN)
            .options(
                selectinload(UserGroup.utilisateur),
                selectinload(UserGroup.groupe)
            )
        )).scalars().all()

    @staticmethod
    async def get_user_group(
            db: AsyncSession,
            user_id: int,
            group_id: int) -> UserGroup:

        return (await db.execute(
            select(UserGroup)
            .where(UserGroup.utilisateur_id == user_id)
            .where(UserGroup.groupe_id == group_id)
            .options(
                selectinload(UserGroup.groupe)
            )
        )).scalars().first()

    @staticmethod
    async def update_nickname(
            db: AsyncSession,
            current_user: User,
            group_id: int,
            nickname: str
    ):
        user_group = await UserGroupService.get_user_group(db, current_user.id, group_id)

        if not user_group:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans le groupe.")
        if user_group.groupe_id != group_id:
            raise HTTPException(status_code=403, detail="❌ Accès interdit à ce groupe.")

        user_group.surnom = nickname
        db.add(user_group)
        await db.commit()
        await db.refresh(user_group)

        logger.info(f"Surnom mis à jour pour l'utilisateur {current_user.id} dans le groupe {group_id}")

    @staticmethod
    async def delete_user_group(
            db: AsyncSession,
            current_user: User,
            group_id: int
    ):
        result = await db.execute(
            select(UserGroup)
            .where(
                UserGroup.utilisateur_id == current_user.id,
                UserGroup.groupe_id == group_id
            )
        )

        user_group = result.scalars().first()

        if not user_group:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans le groupe.")

        await db.delete(user_group)
        await db.commit()

        logger.info(f"Utilisateur {current_user.id} retiré du groupe {group_id}")
