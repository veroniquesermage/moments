from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import RoleEnum
from app.core.logger import logger
from app.models import User, Group, UserGroup
from app.schemas.group import GroupCreate, GroupResponse, GroupDetails, GroupUpdate
from app.services.trace_service import TraceService
from app.services.user_group_service import UserGroupService
from app.utils.code_generator import generate_random_code


class GroupService:

    @staticmethod
    async def create_group(
        db: AsyncSession,
        current_user: User,
        group_data: GroupCreate
    ) -> GroupResponse:
        # 1. Vérif unicité du nom
        result = await db.execute(
            select(Group).where(Group.nom_groupe == group_data.nom_groupe)
        )
        if result.scalars().first():
            logger.info(f"Un groupe existe déjà avec le nom {group_data.nom_groupe}")
            raise HTTPException(
                status_code=400,
                detail="Un groupe avec ce nom existe déjà."
            )

        # 2. Création du groupe
        code = generate_random_code()
        db_group = Group(
            nom_groupe=group_data.nom_groupe,
            description=group_data.description,
            code=code
        )
        db.add(db_group)
        await db.commit()
        await db.refresh(db_group)

        # 3. Lien ADMIN avec l’utilisateur créateur
        link = UserGroup(
            utilisateur_id=current_user.id,
            groupe_id=db_group.id,
            role=RoleEnum.ADMIN
        )
        db.add(link)
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GROUP_CREATED",
            f"Creation du groupe {db_group.nom_groupe}",
            {"group_id": db_group.id, "user_id": current_user.id},
        )

        return GroupResponse.model_validate(db_group)


    @staticmethod
    async def get_groups(
        db: AsyncSession,
        current_user: User
    ) -> list[GroupResponse]:
        """Retourne la liste des Group dont current_user est membre."""
        result = await db.execute(
            select(UserGroup)
            .options(selectinload(UserGroup.groupe))
            .where(UserGroup.utilisateur_id == current_user.id)
        )
        user_groups = result.scalars().all()
        # Extraire directement la liste des Group
        groups = [ug.groupe for ug in user_groups]

        return [GroupResponse.model_validate(g) for g in groups]

    @staticmethod
    async def get_group(
        db: AsyncSession,
        group_id: int
    ) -> GroupResponse:

        result = (await db.execute(
            select(Group)
            .where(Group.id == group_id)
        )).scalars().first()
        if not result:
            raise HTTPException(status_code=404)

        return GroupResponse.model_validate(result)

    @staticmethod
    async def join_group(
        db: AsyncSession,
        current_user: User,
        code: str
    ) -> GroupResponse:
        # 1. Chercher le groupe existant
        result = await db.execute(select(Group).where(Group.code == code))
        existing = result.scalars().first()
        if not existing:
            logger.info(f"Code d'invitation invalide : {code}")
            raise HTTPException(
                status_code=400,
                detail="Ce code d'invitation n'est relié à aucun groupe."
            )

        # 2. Vérifier que l’utilisateur n’est pas déjà membre
        result = await db.execute(
            select(UserGroup).where(
                and_(
                    UserGroup.utilisateur_id == current_user.id,
                    UserGroup.groupe_id == existing.id
                )
            )
        )
        if result.scalars().first():
            logger.info(f"Utilisateur {current_user.id} est déjà dans le groupe {existing.id}")
            raise HTTPException(
                status_code=400,
                detail="Utilisateur déjà dans ce groupe."
            )

        # 3. Ajouter le lien Membre
        link = UserGroup(
            utilisateur_id=current_user.id,
            groupe_id=existing.id,
            role=RoleEnum.MEMBRE
        )
        db.add(link)
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GROUP_JOINED",
            f"{current_user.prenom} a rejoint le groupe {existing.id}",
            {"group_id": existing.id, "user_id": current_user.id},
        )

        return GroupResponse.model_validate(existing)

    @staticmethod
    async def get_group_details(
        db: AsyncSession,
        current_user: User,
        group_id: int
    ) -> GroupDetails:

        user = await UserGroupService.get_user_group(db, current_user.id, group_id)

        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans le groupe.")
        if user.groupe.id != group_id:
            raise HTTPException(status_code=403, detail="❌ Accès interdit à ce groupe.")

        admins: list[UserGroup] = await UserGroupService.get_group_admins(db, group_id)

        if not admins:
            raise HTTPException(status_code=404, detail="Groupe non trouvé.")

        if not user.role:
            raise HTTPException(status_code=500, detail="Role non défini.")


        return GroupDetails(
            groupe= GroupResponse.model_validate(user.groupe),
            admins=[admin.surnom if admin.surnom else admin.utilisateur.prenom
                    for admin in admins],
            surnom=user.surnom,
            role= RoleEnum(user.role),
            prenom= current_user.prenom
        )

    @staticmethod
    async def update_group(
            db: AsyncSession,
            current_user: User,
            group: GroupUpdate,
            group_id: int
    ) -> GroupResponse :

        group_existing = await GroupService.get_group_if_admin(current_user, db, group_id)

        group_existing.nom_groupe = group.nom_groupe
        group_existing.description = group.description

        await db.commit()
        try:
            await db.refresh(group_existing)
        except Exception as e:
            logger.info(f"Refresh failed, but update was successful: {e}")

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GROUP_UPDATED",
            f"Mise a jour du groupe {group_existing.id}",
            {"group_id": group_existing.id, "user_id": current_user.id},
        )

        return GroupResponse.model_validate(group_existing)

    @staticmethod
    async def delete_group(db: AsyncSession,
                           current_user: User,
                           group_id: int):
        group = await GroupService.get_group_if_admin(current_user, db, group_id)

        try:
            await UserGroupService.delete_all_users_from_group(db, group_id)
            await db.delete(group)
            await db.commit()
        except Exception:
            await db.rollback()
            raise HTTPException(status_code=500, detail="❌ Une erreur est survenue pendant la suppression.")

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GROUP_DELETED",
            f"Suppression du groupe {group_id}",
            {"group_id": group_id, "user_id": current_user.id},
        )


    @staticmethod
    async def update_code_invitation(db: AsyncSession,
                                     current_user: User,
                                     group_id: int):
        group = await GroupService.get_group_if_admin(current_user, db, group_id)
        code = generate_random_code()

        group.code = code
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.nom} {current_user.prenom}",
            "CODE_INVIT",
            "Refresh du code d'invitation",
            {"user_id": current_user.id, "groupe": group_id},
        )

    @staticmethod
    async def get_group_if_admin(current_user: User,
                                 db: AsyncSession,
                                 group_id: int) -> Group:
        result = await db.execute(select(Group).where(Group.id == group_id))
        group = result.scalars().first()
        if not group:
            raise HTTPException(status_code=400, detail="❌ Ce groupe n'existe pas.")
        me = await UserGroupService.get_user_group(db, current_user.id, group_id)
        if me is None or me.role != RoleEnum.ADMIN:
            raise HTTPException(status_code=403, detail="❌ Vous n'avez pas les droits pour supprimer ce groupe.")
        return group


