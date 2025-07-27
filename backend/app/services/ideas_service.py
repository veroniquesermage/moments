from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logger import logger
from app.models import GiftIdeas, Gift, User, UserGroup
from app.schemas.gift import GiftIdeaCreate
from app.schemas.gift import GiftIdeasResponse, GiftCreate
from app.services.builders import build_gift_public_response, build_gift_idea_schema
from app.services.trace_service import TraceService


class GiftIdeasService:

    @staticmethod
    async def get_my_ideas(db: AsyncSession,
                           current_user: User,
                           group_id: int) -> list[GiftIdeasResponse]:
        logger.info(f"Récupération des idées de l'utilisateur {current_user.id}")

        gifts_ideas_response = []

        gifts = await db.execute(
            select(Gift, GiftIdeas)
            .join(GiftIdeas, Gift.gift_idea)
            .join(UserGroup, UserGroup.utilisateur_id == Gift.destinataire_id)
            .where(GiftIdeas.proposee_par_id == current_user.id,
                   UserGroup.groupe_id == group_id
                   )
            .options(
                selectinload(Gift.gift_idea).selectinload(GiftIdeas.proposee_par),
                selectinload(Gift.destinataire),
            )
            .order_by(Gift.destinataire_id)
        )

        result = gifts.all()

        logger.info(f"Nombre d'idées récupérées : {len(result)}")

        if result :
            gifts_ideas_response =  [GiftIdeasResponse(
                gift= await build_gift_public_response(gift, group_id, db),
                gift_idea = await build_gift_idea_schema(gift_idea, group_id, db)
            )
            for gift, gift_idea in result]

        return gifts_ideas_response

    @staticmethod
    async def create_gift_idea(db: AsyncSession,
                               current_user: User,
                               gift_idea: GiftIdeaCreate):
        logger.info(f"Création d'une idée de cadeau pour l'utilisateur {current_user}")

        if current_user.id == gift_idea.gift.destinataire_id:
            raise HTTPException(
                status_code=400,
                detail="❌ L'utilisateur ne peut pas proposer une idée de cadeau pour lui-même."
            )

        idea = GiftIdeas(
            proposee_par_id=current_user.id,
            visibilite=gift_idea.visibilite
        )

        db.add(idea)
        await db.flush()
        logger.debug(f"Idée de cadeau créée avec l'ID {idea.id}")

        gift_data = gift_idea.gift.model_dump()
        gift = Gift(**gift_data, gift_idea_id=idea.id)
        db.add(gift)

        await db.commit()
        await db.refresh(idea)
        await db.refresh(gift, attribute_names=["destinataire"])

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_IDEA_CREATED",
            f"Idee de cadeau {idea.id} creee",
            {"idea_id": idea.id, "gift_id": gift.id, "user_id": current_user.id},
        )


    @staticmethod
    async def change_visibility( db: AsyncSession,
                                 current_user: User,
                                 ideaId: int,
                                 visibility: bool) :
        logger.info(f"Changement de visibilité de l'idée {ideaId} pour l'utilisateur {current_user.id}")

        existing = (await db.execute(select(GiftIdeas)
                         .where(GiftIdeas.id == ideaId))).scalars().first()

        if not existing :
            raise HTTPException(
                status_code=400,
                detail=f"❌ L'idée de cadeau avec l\'ID {ideaId} n\'existe pas."
            )

        if existing.proposee_par_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="❌ Vous n'êtes pas autorisé à modifier la visibilité de cette idée."
            )

        existing.visibilite = visibility

        await db.commit()
        await db.refresh(existing)

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "IDEA_VISIBILITY_CHANGED",
            f"Visibilite idee {ideaId} -> {visibility}",
            {"idea_id": ideaId, "user_id": current_user.id, "visible": visibility},
        )


    @staticmethod
    async def duplicate_gift_idea(db: AsyncSession,
                                    current_user: User,
                                    ideaId: int,
                                    new_dest_id: int):

            logger.info(f"Dupliquer l'idée de cadeau {ideaId} pour l'utilisateur {current_user.id}")

            existing: Gift = (await db.execute(select(Gift)
                             .where(Gift.gift_idea_id == ideaId)
                             .options(selectinload(Gift.gift_idea)))).scalars().first()

            if not existing:
                raise HTTPException(
                    status_code=400,
                    detail=f"❌ L'idée de cadeau avec l'ID {ideaId} n'existe pas."
                )

            idea = existing.gift_idea
            if idea.proposee_par_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="❌ Vous n'êtes pas autorisé à dupliquer cette idée."
                )

            gift_data = GiftCreate.model_validate(existing, from_attributes=True).model_dump()
            gift_data["destinataire_id"] = new_dest_id

            gift_idea_create = GiftIdeaCreate(
                gift=GiftCreate(**gift_data),
                visibilite=existing.gift_idea.visibilite
            )

            await TraceService.record_trace(
                db,
                f"{current_user.prenom} {current_user.nom}",
                "IDEA_DUPLICATED",
                f"Duplication de l'idee {ideaId}",
                {"idea_id": ideaId, "new_dest_id": new_dest_id, "user_id": current_user.id},
            )
            await GiftIdeasService.create_gift_idea(db, current_user, gift_idea_create)

    @staticmethod
    async def delete_gift_idea(db: AsyncSession,
                               current_user: User,
                               ideaId: int) :

        logger.info(f"Suppression de l'idée de cadeau {ideaId} pour l'utilisateur {current_user.id}")

        existing: Gift = (await db.execute(select(Gift)
                                           .where(Gift.gift_idea_id == ideaId)
                                           .options(selectinload(Gift.gift_idea)))).scalars().first()

        if not existing:
            raise HTTPException(
                status_code=400,
                detail=f"❌ L'idée de cadeau avec l'ID {ideaId} n'existe pas."
            )

        if existing.gift_idea.proposee_par_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="❌ Vous n'êtes pas autorisé à supprimer cette idée."
            )

        await db.delete(existing.gift_idea)
        await db.delete(existing)
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_IDEA_DELETED",
            f"Suppression idee {ideaId}",
            {"idea_id": ideaId, "user_id": current_user.id},
        )

