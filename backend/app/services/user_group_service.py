from operator import and_
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, Sequence, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import RoleEnum
from app.core.logger import logger
from app.models import User, UserGroup
from app.schemas import UserDisplaySchema
from app.schemas.mailing.invite_request import InviteRequest
from app.services.trace_service import TraceService


class UserGroupService:

    @staticmethod
    async def get_users_except_current_user(db: AsyncSession,
                                            current_user: User,
                                            group_id: int) -> list[UserDisplaySchema]:

        results = (await db.execute(
            select(UserGroup)
            .where(UserGroup.groupe_id == group_id,
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
            surnom= result.surnom if result.surnom else None,
            role= result.role
            )
            for result in results ]

        return user_display_schema

    @staticmethod
    async def get_users(
            db: AsyncSession,
            group_id: int) -> list[UserDisplaySchema]:

        results = (await db.execute(
            select(UserGroup)
            .where(UserGroup.groupe_id == group_id)
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
                surnom= result.surnom if result.surnom else None,
                role= result.role
            )
            for result in results ]

        return user_display_schema

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

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "NICKNAME_UPDATED",
            f"Surnom mis a jour dans le groupe {group_id}",
            {"group_id": group_id, "user_id": current_user.id},
        )

    @staticmethod
    async def delete_user_group(
            db: AsyncSession,
            current_user: User,
            group_id: int,
            user_id_to_delete: Optional[int]
    ):
        # Vérifie que current_user fait partie du groupe
        result = await db.execute(
            select(UserGroup)
            .where(and_(
                UserGroup.utilisateur_id == current_user.id,
                UserGroup.groupe_id == group_id
            ))
        )
        user_group = result.scalars().first()

        if not user_group:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans le groupe.")

        # Cas : l'utilisateur quitte le groupe
        if user_id_to_delete is None:
            await db.delete(user_group)
            await db.commit()
            await TraceService.record_trace(
                db,
                f"{current_user.prenom} {current_user.nom}",
                "GROUP_LEFT",
                f"{current_user.prenom} a quitté le groupe {group_id}",
                {"group_id": group_id, "user_id": current_user.id},
            )
            return

        # Cas : tentative d’exclure quelqu’un → faut être admin
        if user_group.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Vous n'avez pas les droits pour exclure un membre.")

        # Vérifie que le membre à exclure existe dans le groupe
        result_exclude = await db.execute(
            select(UserGroup)
            .where(and_(
                UserGroup.utilisateur_id == user_id_to_delete,
                UserGroup.groupe_id == group_id
            ))
        )
        to_exclude = result_exclude.scalars().first()
        if not to_exclude:
            raise HTTPException(status_code=404, detail="Membre à exclure introuvable dans ce groupe.")

        await db.delete(to_exclude)
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "MEMBER_REMOVED",
            f"Membre {user_id_to_delete} exclu du groupe {group_id}",
            {"group_id": group_id, "user_id": current_user.id, "target_id": user_id_to_delete},
        )

    @staticmethod
    async def update_role(db: AsyncSession, group_id: int, current_user: User, groupRoleUpdate: list[UserDisplaySchema]) -> list[UserDisplaySchema]:

        me = await UserGroupService.get_user_group(db, current_user.id, group_id)

        if me.role != RoleEnum.ADMIN:
            raise HTTPException(status_code=403, detail="❌ Cet utilisateur n'a pas le droit de modifier les rôles des membres.")

        user_ids = [item.id for item in groupRoleUpdate]

        result = await db.execute(select(UserGroup).where(UserGroup.groupe_id == group_id)
                                            .where(UserGroup.utilisateur_id.in_(user_ids)))

        user_groups_to_update = result.scalars().all()

        for user_group in user_groups_to_update:
            new_data = next((u for u in groupRoleUpdate if u.id == user_group.utilisateur_id), None)
            if new_data:
                user_group.role = new_data.role

        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "ROLE_UPDATED",
            f"Roles mis a jour dans le groupe {group_id}",
            {"group_id": group_id, "user_id": current_user.id},
        )

        return await UserGroupService.get_users_except_current_user(db, current_user, group_id)

    @staticmethod
    async def delete_all_users_from_group(db: AsyncSession, group_id: int):
        stmt = delete(UserGroup).where(UserGroup.groupe_id == group_id)
        await db.execute(stmt)

    @staticmethod
    async def get_existing_users_in_group(db: AsyncSession, group_id: int, invite_request: InviteRequest) -> list[str]:
        stmt = (
            select(User.email)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(
                UserGroup.groupe_id == group_id,
                User.email.in_(invite_request.emails)
            )
        )
        result = await db.execute(stmt)
        return [row[0] for row in result.fetchall()]


