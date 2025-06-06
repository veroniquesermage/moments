from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import GiftStatusEnum
from app.core.logger import logger
from app.models import GiftIdeas, Gift, User, UserGroup
from app.schemas import UserSchema
from app.schemas.gift import GiftIdeasResponse
from app.schemas.gift import GiftPublicResponse
from app.schemas.gift import GiftIdeasSchema
from app.schemas.gift import GiftIdeaCreate

class GiftIdeasService:

    @staticmethod
    async def get_my_ideas(db: AsyncSession,
                           current_user: User,
                           groupId: int) -> list[GiftIdeasResponse]:
        logger.info(f"Récupération des idées de l'utilisateur {current_user.id}")

        gifts_ideas_response = []

        gifts = await db.execute(
            select(Gift, GiftIdeas)
            .join(GiftIdeas, Gift.gift_idea)
            .join(UserGroup, UserGroup.utilisateur_id == Gift.destinataire_id)
            .where(GiftIdeas.proposee_par_id == current_user.id,
                   UserGroup.groupe_id == groupId
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
                gift= GiftPublicResponse.model_validate(gift),
                gift_idea = GiftIdeasSchema.model_validate(gift_idea)
            )
            for gift, gift_idea in result]

        return gifts_ideas_response

    @staticmethod
    async def create_gift_idea(db: AsyncSession,
                               current_user: User,
                               gift_idea: GiftIdeaCreate) -> GiftIdeasResponse:
        logger.info(f"Création d'une idée de cadeau pour l'utilisateur {current_user}")

        if current_user.id == gift_idea.gift.destinataire_id:
            raise ValueError("L'utilisateur ne peut pas proposer une idée de cadeau pour lui-même.")

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

        return GiftIdeasResponse(
            gift=GiftPublicResponse.model_validate(gift),
            gift_idea=GiftIdeasSchema.model_validate(idea)
        )
