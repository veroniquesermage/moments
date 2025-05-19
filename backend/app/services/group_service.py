from fastapi import HTTPException
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.functions import current_user

from app.core.logger import logger
from app.models import User, Group, UserGroup
from app.schemas.group import GroupCreate, RoleEnum
from app.utils.code_generator import generate_random_code


class GroupService:

    @staticmethod
    async def create_group(group_data: GroupCreate, current_user: User, db: AsyncSession) -> Group:
        # Vérif unicité du nom
        result = await db.execute(select(Group).where(Group.nom_groupe == group_data.nom_groupe))
        existing = result.scalars().first()
        if existing:
            logger.info(f"un groupe existe déjà avec le nom {group_data.nom_groupe}")
            raise HTTPException(status_code=400, detail="Un groupe avec ce nom existe déjà.")

        code = generate_random_code()

        # Création du groupe
        db_group = Group(
            nom_groupe=group_data.nom_groupe,
            description=group_data.description,
            code=code
        )
        db.add(db_group)
        await db.commit()
        await db.refresh(db_group)

        # Lien avec l'utilisateur
        link = UserGroup(
            utilisateur_id=current_user.id,
            groupe_id=db_group.id,
            role=RoleEnum.ADMIN
        )
        db.add(link)
        await db.commit()

        return db_group

    @staticmethod
    async def get_groups(current_user: User, db: Session):
        groups_user = []
        result = await db.execute(
            select(UserGroup)
            .options(selectinload(UserGroup.groupe))  # 👈 essentiel pour éviter le lazy-load bloquant
            .where(UserGroup.utilisateur_id == current_user.id)
        )
        db_user_group = result.scalars().all()

        for db_ug in db_user_group:
            groups_user.append(db_ug.groupe)
        return groups_user

    @staticmethod
    async def join_group(current_user, db, code):
        result = await db.execute(select(Group).where(Group.code == code))
        existing = result.scalars().first()

        if not existing:
            logger.info(f"Ce code d'invitation {code} n'est relié à aucun groupe")
            raise HTTPException(status_code=400, detail="Ce code d'invitation n'est relié à aucun groupe.")

        link = UserGroup(
            utilisateur_id=current_user.id,
            groupe_id=existing.id,
            role=RoleEnum.MEMBRE
        )

        result = await db.execute(select(UserGroup).where(and_(
            UserGroup.utilisateur_id == current_user.id,
            UserGroup.groupe_id == existing.id
            )))

        existing_link = result.scalars().first()

        if existing_link:
            logger.info(f"L'utilisateur {current_user.id} appartient déjà au group {existing.groupe_id}")
            raise HTTPException(status_code=400, detail="Utilisateur déjà dans ce groupe")

        db.add(link)
        await db.commit()
        return existing

    @staticmethod
    def _generate_unique_code(db: Session, length: int = 10) -> str:
        while True:
            code = generate_random_code(length)
            if not db.query(Group).filter_by(code=code).first():
                return code

