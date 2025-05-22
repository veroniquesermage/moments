from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select, Sequence, false
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import GiftActionEnum, GiftStatusEnum
from app.core.logger import logger
from app.core.message import CADEAU_DISPONIBLE, CADEAU_INEXISTANT, RESERVATION_VALIDEE, CADEAU_NON_DISPONIBLE
from app.models import User, Gift
from app.models.gift import Gift
from app.schemas.gift import EligibilityResponse, GiftResponse, GiftStatus, GiftCreate, GiftBase, GiftFollowed
from app.schemas.gift.gift_update import GiftUpdate


class GiftService:

    @staticmethod
    async def get_gifts(db: AsyncSession,
                        effective_user_id: int) -> list[GiftResponse]:
        logger.info(f"Récupération des cadeaux de l'utilisateur {effective_user_id}")
        result = (await db.execute(
            select(Gift).where(Gift.utilisateur_id == effective_user_id)
            .options(
                selectinload(Gift.utilisateur),  # charge eager le créateur du cadeau
                selectinload(Gift.reservePar)  # charge eager l’utilisateur qui réserve
            )
        )).scalars().all()
        return [GiftResponse.model_validate(g) for g in result]

    @staticmethod
    async def get_gift(db: AsyncSession,
                       giftId: int,
                       current_user: User) -> GiftResponse:

        logger.info(f"Récupération du cadeau à l'id {giftId}")

        result = await GiftService.get_gift_or_raise(db, giftId)

        return GiftResponse.model_validate(result)


    @staticmethod
    async def verify_eligibility(db: AsyncSession,
                                 gift_id: int,
                                 user: User,
                                 action: GiftActionEnum) -> EligibilityResponse:
        gift = await db.get(Gift, gift_id)
        if not gift:
            return EligibilityResponse(ok=False, message=CADEAU_INEXISTANT)

        match action:
            case GiftActionEnum.RESERVER:
                if gift.statut == GiftStatusEnum.DISPONIBLE:
                    return EligibilityResponse(ok=True, message=CADEAU_DISPONIBLE)

            case GiftActionEnum.PRENDRE:
                if gift.statut == GiftStatusEnum.DISPONIBLE:
                    return EligibilityResponse(ok=True, message=CADEAU_DISPONIBLE)
                if (
                        gift.statut == GiftStatusEnum.RESERVE
                        and gift.reservePar is not None
                        and gift.reservePar.id == user.id
                ):
                    return EligibilityResponse(ok=True, message=RESERVATION_VALIDEE)

        return EligibilityResponse(ok=False, message=CADEAU_NON_DISPONIBLE)

    @staticmethod
    async def update_gift(
            db: AsyncSession,
            gift_id: int,
            user: User,
            updates: GiftUpdate
    ) -> GiftResponse:
        # 1. Vérifier la cohérence des IDs
        if gift_id != updates.id:
            raise HTTPException(
                status_code=400,
                detail="❌ L’ID du payload ne correspond pas à l’ID en path."
            )

        # 2. Récupérer l’entité existante
        existing: Gift | None = (await db.execute(
            select(Gift).where(Gift.id == gift_id)
            .options(
                selectinload(Gift.utilisateur),  # charge eager le créateur du cadeau
                selectinload(Gift.reservePar)  # charge eager l’utilisateur qui réserve
            )
        )).scalars().first()
        if not existing:
            raise HTTPException(status_code=404, detail="Cadeau introuvable.")

        # 3. Appliquer les mises à jour dynamiquement
        for field in updates.model_fields_set:
            setattr(existing, field, getattr(updates, field))

        # 4. Persister et rafraîchir l’instance
        db.add(existing)
        await db.commit()
        await db.refresh(existing)

        # 5. Retourner l’instance ORM (FastAPI la convertira en GiftResponse si response_model est défini)
        return GiftResponse.model_validate(existing)

    @staticmethod
    async def delete_gift(db: AsyncSession,
                          giftId: int,
                          current_user: User):

        logger.info(f"Suppression du cadeau à l'id {giftId}")

        result: Gift | None = (await db.execute(
            select(Gift).where(Gift.id == giftId)
        )).scalars().first()

        if result is None:
            logger.info(f"Cadeau avec l'id {giftId} introuvable.")
            raise HTTPException(status_code=404, detail="Cadeau introuvable.")
        elif result.utilisateur_id != current_user.id:
            logger.info(
                f"Lutilisateur {current_user.id} tente de supprimer un cadeau qui appartien à l'utilisateur {result.utilisateur_id}")
            raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres cadeaux.")

        await db.delete(result)
        await db.commit()

    @staticmethod
    async def change_status(db: AsyncSession,
                            current_user: User,
                            giftId: int,
                            gift_status: GiftStatus) -> GiftResponse:

        result = await GiftService.get_gift_or_raise(db, giftId)

        result.statut = gift_status.status

        if gift_status.status == GiftStatusEnum.DISPONIBLE:
            logger.debug(f"Le statut du cadeau est {gift_status.status}")
            result.lieuLivraison = None
            result.dateLivraison = None
            result.prixReel = None
            result.reserve_par_id = None
            result.reservePar = None
            result.dateReservation = None
            result.recu = False
        else:
            result.reservePar = current_user
            result.dateReservation = datetime.now()

        logger.debug("Attributs de gift : %s", vars(result))

        db.add(result)
        await db.commit()

        return GiftResponse.model_validate(result)

    @staticmethod
    async def create_gift(db: AsyncSession,
                          current_user: User,
                          gift_created: GiftCreate) -> GiftResponse:

        if current_user.id != gift_created.utilisateur.id:
            raise HTTPException(status_code=403, detail="Vous ne pouvez enregistrer un cadeau que pour vous-même.")

        gift_data = gift_created.model_dump(exclude={"utilisateur"})
        gift = Gift(**gift_data)
        gift.utilisateur_id = current_user.id

        db.add(gift)
        await db.commit()
        await db.refresh(gift)

        return GiftResponse.model_validate(gift)

    @staticmethod
    async def get_followed_gifts(db: AsyncSession,
                                 current_user: User) -> list[GiftFollowed]:

        # 1) exécution de la requête
        stmt = (
            select(Gift)
            .where(Gift.reserve_par_id == current_user.id)
            .options(selectinload(Gift.utilisateur))
        )
        rows = await db.execute(stmt)
        gifts = rows.scalars().all()
        # 3) log de diagnostic
        gift_followeds = [GiftFollowed.model_validate(g) for g in gifts]

        # debug : dump en dict pour voir
        logger.info(
            "[get_followed_gifts] Pydantic objects raw data: %s",
            [gf.model_dump() for gf in gift_followeds]
        )

        return gift_followeds

    @staticmethod
    async def get_gift_or_raise(db: AsyncSession,
                                giftId: int) -> Gift:
        result: Gift | None = (await db.execute(
            select(Gift).where(Gift.id == giftId)
            .options(
                selectinload(Gift.utilisateur),  # charge eager le créateur du cadeau
                selectinload(Gift.reservePar)  # charge eager l’utilisateur qui réserve
            )
        )).scalars().first()
        if result is None:
            logger.error(f"Cadeau {giftId} introuvable.")
            raise HTTPException(status_code=404, detail="Cadeau introuvable.")
        return result

    @staticmethod
    def _apply_updates_to_entity(
            existing: Gift,
            updates: GiftBase) -> Gift:

        for field in updates.model_fields_set:
            setattr(existing, field, getattr(updates, field))
        return existing
