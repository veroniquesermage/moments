from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import UserGroup, Gift, GiftIdeas, GiftShared
from app.schemas import UserDisplaySchema
from app.schemas.gift import GiftPublicResponse, GiftIdeasSchema, GiftSharedSchema


async def build_user_display(user_id: int, group_id: int, db: AsyncSession) -> UserDisplaySchema:
    result = await db.execute(
        select(UserGroup)
        .where(
            UserGroup.utilisateur_id == user_id,
            UserGroup.groupe_id == group_id
        )
        .options(selectinload(UserGroup.utilisateur))
    )

    user_group = result.scalars().first()

    if not user_group:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé dans le groupe.")

    return UserDisplaySchema(
        id=user_group.utilisateur.id,
        nom=user_group.utilisateur.nom,
        prenom=user_group.utilisateur.prenom,
        surnom=user_group.surnom if user_group.surnom else None
    )

async def build_gift_public_response(gift: Gift, group_id: int, db: AsyncSession) -> GiftPublicResponse:
    return GiftPublicResponse(
        id=gift.id,
        destinataire=await build_user_display(gift.destinataire_id, group_id, db),
        nom=gift.nom,
        description=gift.description,
        marque=gift.marque,
        magasin=gift.magasin,
        url=gift.url,
        quantite=gift.quantite,
        prix=gift.prix,
        frais_port=gift.frais_port,
        commentaire=gift.commentaire,
        priorite=gift.priorite,
        statut=gift.statut,
        reserve_par=await build_user_display(gift.reserve_par_id, group_id, db) if gift.reserve_par_id else None,
        date_reservation=gift.date_reservation,
        expiration_reservation=gift.expiration_reservation,
        gift_idea=await build_gift_idea_schema(gift.gift_idea, group_id, db) if gift.gift_idea else None
    )

async def build_gift_idea_schema(gift_idea: GiftIdeas, group_id: int, db: AsyncSession):

    return GiftIdeasSchema(
        id=gift_idea.id,
        proposee_par= await build_user_display(gift_idea.proposee_par_id, group_id , db),
        visibilite=gift_idea.visibilite
    )

async def build_gift_shared_schema(gift: GiftShared, group_id: int, db: AsyncSession) -> GiftSharedSchema:
    return GiftSharedSchema(
        id=gift.id,
        preneur=await build_user_display(gift.preneur_id, group_id, db),
        cadeau_id=gift.cadeau_id,
        participant=await build_user_display(gift.participant_id, group_id, db),
        montant=gift.montant,
        rembourse=gift.rembourse
    )
