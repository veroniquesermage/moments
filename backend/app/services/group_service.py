from typing import Any, Coroutine

from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import RoleEnum
from app.core.logger import logger
from app.models import User, Group, UserGroup
from app.schemas.group import GroupCreate, GroupResponse
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
        current_user: User,
        group_id: int
    ) -> GroupResponse:
        """Retourne la liste des Group dont current_user est membre."""
        result = (await db.execute(
            select(Group)
            .where(Group.id == group_id)
        )).scalars().first()

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

        return GroupResponse.model_validate(existing)
