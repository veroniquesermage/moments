from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, Sequence, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import GiftActionEnum, GiftStatusEnum, RoleUtilisateur
from app.core.logger import logger
from app.core.message import *
from app.models import User, GiftShared
from app.models.gift import Gift
from app.schemas.gift import EligibilityResponse, GiftResponse, GiftStatus, GiftCreate, GiftDetailResponse, \
    GiftSharedSchema, GiftPriority
from app.schemas.gift.gift_update import GiftUpdate
from app.services.sharing_service import SharingService


class GiftService:

    @staticmethod
    async def get_gifts(db: AsyncSession,
                        effective_user_id: int) -> list[GiftResponse]:
        logger.info(f"Récupération des cadeaux de l'utilisateur {effective_user_id}")
        result = (await db.execute(
            select(Gift).where(Gift.utilisateur_id == effective_user_id)
            .order_by(Gift.priorite)
            .options(
                selectinload(Gift.utilisateur),  # charge eager le créateur du cadeau
                selectinload(Gift.reservePar)  # charge eager l’utilisateur qui réserve
            )
        )).scalars().all()
        return [GiftResponse.model_validate(g) for g in result]

    @staticmethod
    async def get_gift(db: AsyncSession,
                       giftId: int,
                       current_user: User) -> GiftDetailResponse:

        logger.info(f"Récupération du cadeau à l'id {giftId}")
        result: Gift = await GiftService.get_gift_or_raise(db, giftId)
        shared_schema = await SharingService.get_all_shares_for_gift(db, gift_id=giftId)

        role_user = GiftService.define_user_role(current_user, result, shared_schema)

        logger.debug(f"Récupération du cadeau {result.id} par l'utilisateur {current_user.id} avec le rôle {role_user}")

        return GiftService.set_gift_detail(result, current_user, shared_schema)


    @staticmethod
    async def verify_eligibility(db: AsyncSession,
                                 gift_id: int,
                                 user: User,
                                 action: GiftActionEnum) -> EligibilityResponse:
        gift = await db.get(Gift, gift_id)
        if not gift:
            logger.error(f"Cadeau {gift_id} introuvable.")
            return EligibilityResponse(ok=False, message=CADEAU_INEXISTANT)

        match action:
            case GiftActionEnum.RESERVER:
                logger.debug(f"L'action est de réserver le cadeau {gift_id} par l'utilisateur {user.id}")
                if gift.statut == GiftStatusEnum.DISPONIBLE:
                    return EligibilityResponse(ok=True, message=CADEAU_DISPONIBLE)

            case GiftActionEnum.PRENDRE:
                logger.debug(f"L'action est de prendre le cadeau {gift_id} par l'utilisateur {user.id}")
                if gift.statut == GiftStatusEnum.DISPONIBLE:
                    return EligibilityResponse(ok=True, message=CADEAU_DISPONIBLE)
                if (
                        gift.statut == GiftStatusEnum.RESERVE
                        and gift.reservePar is not None
                        and gift.reservePar.id == user.id
                ):
                    return EligibilityResponse(ok=True, message=RESERVATION_VALIDEE)
            case GiftActionEnum.ANNULER_RESERVATION:
                logger.debug(f"L'action est d'annuler la réservation pour le cadeau {gift_id} par l'utilisateur {user.id}")
                if gift.statut != GiftStatusEnum.RESERVE:
                    return EligibilityResponse(ok=False, message=CADEAU_NON_RESERVE)
                if gift.reserve_par_id == user.id:
                    return EligibilityResponse(ok=True, message=CADEAU_RESERVATION_ANNULEE)
            case GiftActionEnum.RETIRER:
                logger.debug(f"L'action est de retirer le cadeau {gift_id} par l'utilisateur {user.id}")
                if gift.statut != GiftStatusEnum.PRIS and gift.statut != GiftStatusEnum.PARTAGE:
                    return EligibilityResponse(ok=False, message=CADEAU_NON_PRIS)
                if gift.reserve_par_id == user.id:
                    return EligibilityResponse(ok=True, message=CADEAU_RETIRE)

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
    async def update_all_gifts(db: AsyncSession,
                               current_user: User,
                               payload: list[GiftPriority]) -> list[GiftResponse]:
        logger.info(f"Mise à jour de {len(payload)} cadeaux pour l'utilisateur {current_user.id}")

        ids = [p.id for p in payload]
        gifts_list = (await db.execute(
            select(Gift).where(Gift.id.in_(ids))
            .options(selectinload(Gift.reservePar))
            .options(selectinload(Gift.utilisateur))
        )).scalars().all()

        if any(gift.utilisateur_id != current_user.id for gift in gifts_list):
            raise HTTPException(status_code=403, detail="Vous ne pouvez modifier que vos propres cadeaux.")

        gift_map = {gift.id: gift for gift in gifts_list}
        logger.debug(f"Gift map: {gift_map}")
        for p in payload:
            gift_map[p.id].priorite = p.priority
        logger.debug(f"Gift map mis à jour: {gift_map}")

        await db.commit()
        for gift in gift_map.values():
            await db.refresh(gift)

        sorted_gifts = sorted(gift_map.values(), key=lambda g: g.priorite)
        return [GiftResponse.model_validate(gm) for gm in sorted_gifts]


    @staticmethod
    async def set_gift_delivery(db: AsyncSession,
                                current_user: User,
                                giftId: int,
                                recu: bool) -> GiftDetailResponse:
        logger.debug(f"Marquage du cadeau {giftId} comme reçu : {recu}")
        gift: Gift = await GiftService.get_gift_or_raise(db, giftId)
        if gift.reserve_par_id != current_user.id:
            logger.error(f"L'utilisateur {current_user.id} n'est pas autorisé à marquer le cadeau {giftId} comme reçu.")
            raise HTTPException(status_code=403, detail="Seule la personne qui a réservé le cadeau peut le marquer comme reçu.")

        gift.recu = recu
        logger.debug(f"Attributs de gift : {vars(gift)}")

        db.add(gift)
        await db.commit()
        await db.refresh(gift)

        return GiftService.set_gift_detail(gift, current_user)

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
        elif gift_status.status == GiftStatusEnum.PARTAGE:
            # ne rien toucher de plus que le statut
            logger.debug("Passage en PARTAGE, pas de changement de réservation.")
        else:
            # cas PRIS ou RÉSERVÉ
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
                                 current_user: User) -> list[GiftResponse]:

        # 1) récupérer les cadeaux suivis par l'utilisateur
        result_gift = await db.execute((
            select(Gift)
            .where(Gift.reserve_par_id == current_user.id)
            .options(selectinload(Gift.utilisateur))
        ))
        gifts = result_gift.scalars().all()

        gifts_followed = [GiftResponse.model_validate(gi) for gi in gifts]

        # 3) recuperer les cadeaux partagés

        result_gift_shared = await db.execute((
            select(Gift)
            .join(GiftShared, Gift.id == GiftShared.cadeau_id)
            .where(GiftShared.participant_id == current_user.id)
        ))

        shared = result_gift_shared.scalars().all()

        gift_shared = [GiftResponse.model_validate(sh) for sh in shared]

        return gifts_followed + gift_shared

    @staticmethod
    def set_gift_detail(gift: Gift, current_user: User, partage: Optional[list[GiftSharedSchema]] = None) -> GiftDetailResponse:
        return GiftDetailResponse(
            gift=GiftResponse.model_validate(gift),
            partage=partage,
            est_partage=gift.statut == GiftStatusEnum.PARTAGE,
            droits_utilisateur= GiftService.define_user_role(current_user, gift, partage)
        )

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
    def define_user_role(
            current_user: User,
            gift: Gift,
            partages: Optional[list[GiftSharedSchema]] = None
    ) -> RoleUtilisateur:
        if gift.utilisateur.id == current_user.id:
            return RoleUtilisateur.CREATEUR
        elif gift.reservePar and gift.reservePar.id == current_user.id:
            return RoleUtilisateur.PRENEUR
        elif any(p.participant.id == current_user.id for p in partages):
            return RoleUtilisateur.PARTICIPANT
        else:
            return RoleUtilisateur.SPECTATEUR

