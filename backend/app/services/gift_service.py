from datetime import timedelta
from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import GiftActionEnum, GiftStatusEnum, RoleUtilisateur
from app.core.logger import logger
from app.core.message import *
from app.models import User, GiftShared, GiftIdeas, GiftDelivery, UserGroup
from app.models.gift import Gift
from app.schemas.gift.eligibility_response import EligibilityResponse
from app.schemas.gift.gift_create import GiftCreate
from app.schemas.gift.gift_delivery_schema import GiftDeliverySchema
from app.schemas.gift.gift_delivery_update import GiftDeliveryUpdate
from app.schemas.gift.gift_detail_response import GiftDetailResponse
from app.schemas.gift.gift_followed import GiftFollowed
from app.schemas.gift.gift_priority import GiftPriority
from app.schemas.gift.gift_public_response import GiftPublicResponse
from app.schemas.gift.gift_response import GiftResponse
from app.schemas.gift.gift_shared import GiftSharedSchema
from app.schemas.gift.gift_status import GiftStatus
from app.schemas.gift.gift_update import GiftUpdate
from app.services.builders import build_gift_public_response, build_gift_shared_schema, build_gift_idea_schema
from app.services.mailing.mail_service import MailService
from app.services.sharing_service import SharingService
from app.services.trace_service import TraceService
from app.utils.date_helper import now_paris


class GiftService:

    @staticmethod
    async def get_my_gifts(db: AsyncSession,
                           effective_user_id: int) -> list[GiftResponse]:
        logger.info(f"Récupération des cadeaux de l'utilisateur {effective_user_id}")
        result = (await db.execute(
            select(Gift).where(and_(Gift.destinataire_id == effective_user_id, Gift.gift_idea_id.is_(None)))
            .order_by(Gift.priorite)
            .options(
                selectinload(Gift.destinataire),  # charge eager le créateur du cadeau
                selectinload(Gift.reserve_par)  # charge eager l’utilisateur qui réserve
            )
        )).scalars().all()
        return [GiftResponse.model_validate(g) for g in result]

    @staticmethod
    async def get_gift(db: AsyncSession,
                       gift_id: int,
                       group_id: int,
                       current_user: User) -> GiftDetailResponse:
        logger.info(f"Récupération du cadeau à l'id {gift_id}")

        result: Gift = await GiftService.get_gift_or_raise(db, gift_id)
        shared_schema = await SharingService.get_all_shares_for_gift(db, gift_id=gift_id, group_id=group_id)

        role_user = GiftService.define_user_role(current_user, result, shared_schema)

        logger.debug(f"Récupération du cadeau {result.id} par l'utilisateur {current_user.id} avec le rôle {role_user}")

        return await GiftService.set_gift_detail(result, current_user, group_id, db, shared_schema)

    @staticmethod
    async def get_visible_gifts_for_member(db: AsyncSession,
                                           user_id: int) -> list[GiftPublicResponse]:

        result = await db.execute(
            select(Gift)
            .outerjoin(Gift.gift_idea)
            .options(
                selectinload(Gift.destinataire),
                selectinload(Gift.reserve_par),
                selectinload(Gift.gift_idea).selectinload(GiftIdeas.proposee_par),
            )
            .where(
                Gift.destinataire_id == user_id,
                or_(
                    Gift.gift_idea_id == None,
                    Gift.gift_idea.has(GiftIdeas.visibilite.is_(True))
                )
            )
            .order_by(Gift.priorite)
        )
        gifts = result.scalars().all()

        logger.debug(
            f"Récupération des cadeaux visibles pour l'utilisateur {user_id}, nombre de cadeaux trouvés : {len(gifts)}")
        return [GiftPublicResponse.model_validate(g) for g in gifts]

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
                        and gift.reserve_par is not None
                        and gift.reserve_par.id == user.id
                ):
                    return EligibilityResponse(ok=True, message=RESERVATION_VALIDEE)
            case GiftActionEnum.ANNULER_RESERVATION:
                logger.debug(
                    f"L'action est d'annuler la réservation pour le cadeau {gift_id} par l'utilisateur {user.id}")
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
            current_user: User,
            gift_id: int,
            updates: GiftUpdate) -> GiftResponse:

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
                selectinload(Gift.destinataire),  # charge eager le créateur du cadeau
                selectinload(Gift.reserve_par),
                selectinload(Gift.gift_idea).selectinload(GiftIdeas.proposee_par)# charge eager l’utilisateur qui réserve
            )
        )).scalars().first()
        if not existing:
            raise HTTPException(status_code=404, detail="Cadeau introuvable.")

        if updates.destinataire_id != current_user.id and (existing.gift_idea.proposee_par.id != current_user.id):
            raise HTTPException(
                status_code=400,
                detail="❌ Vous ne pouvez modifier que vos propres cadeaux ou idées."
            )

        logger.info(f"Modification du cadeau {gift_id} : champs modifiés → {updates.model_fields_set}")

        if existing.statut != GiftStatusEnum.DISPONIBLE:
            await MailService.send_alert_update(existing, current_user, db)

        # 3. Appliquer les mises à jour dynamiquement
        for field in updates.model_fields_set:
            setattr(existing, field, getattr(updates, field))

        # 4. Persister et rafraîchir l’instance
        db.add(existing)
        await db.commit()
        await db.refresh(existing)

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_UPDATED",
            f"Mise a jour du cadeau {existing.id}",
            {"gift_id": existing.id, "user_id": current_user.id},
        )

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
            .options(selectinload(Gift.reserve_par))
            .options(selectinload(Gift.destinataire))
        )).scalars().all()

        if any(gift.destinataire.id != current_user.id for gift in gifts_list):
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
    async def update_gift_delivery(db,
                                   current_user,
                                   giftId,
                                   giftDeliveryUpdate) -> GiftDeliveryUpdate:
        # 1. On récupère le cadeau
        gift: Gift | None = (
            await db.execute(
                select(Gift)
                .options(
                    selectinload(Gift.reserve_par),
                    selectinload(Gift.gift_delivery)
                )
                .where(Gift.id == giftId)
            )
        ).scalars().first()

        if not gift:
            raise HTTPException(status_code=404, detail="Cadeau introuvable.")

        # 2. Check autorisation
        if not gift.reserve_par or gift.reserve_par.id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit à la livraison de ce cadeau.")

        # 3. Récupérer ou créer la livraison
        delivery = gift.gift_delivery
        if not delivery:
            delivery = GiftDelivery(gift_id=giftId)

        # 4. Appliquer les updates
        for field in giftDeliveryUpdate.model_fields_set:
            setattr(delivery, field, getattr(giftDeliveryUpdate, field))

        # 5. Commit
        db.add(delivery)
        await db.commit()
        await db.refresh(delivery)

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_DELIVERY_UPDATED",
            f"Livraison du cadeau {giftId} mise a jour",
            {"gift_id": giftId, "user_id": current_user.id},
        )

        return GiftDeliveryUpdate.model_validate(delivery)

    @staticmethod
    async def set_gift_delivery(db: AsyncSession,
                                current_user: User,
                                giftId: int,
                                recu: bool,
                                group_id: int) -> GiftDetailResponse:
        logger.debug(f"Marquage du cadeau {giftId} comme reçu : {recu}")
        gift: Gift = await GiftService.get_gift_or_raise(db, giftId)
        if gift.reserve_par_id != current_user.id:
            logger.error(f"L'utilisateur {current_user.id} n'est pas autorisé à marquer le cadeau {giftId} comme reçu.")
            raise HTTPException(status_code=403,
                                detail="Seule la personne qui a réservé le cadeau peut le marquer comme reçu.")

        if gift.gift_delivery is None:
            gift.gift_delivery = GiftDelivery(gift_id=gift.id, recu=recu)
        else:
            gift.gift_delivery.recu = recu

        db.add(gift.gift_delivery)
        await db.commit()
        await db.refresh(gift.gift_delivery)

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_MARKED_RECEIVED",
            f"Cadeau {giftId} marque comme recu : {recu}",
            {"gift_id": giftId, "user_id": current_user.id, "recu": recu},
        )

        return await GiftService.set_gift_detail(gift, current_user, group_id, db)

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
        elif result.destinataire_id != current_user.id:
            logger.info(
                f"Lutilisateur {current_user.id} tente de supprimer un cadeau qui appartien à l'utilisateur {result.destinataire_id}")
            raise HTTPException(status_code=403, detail="Vous ne pouvez supprimer que vos propres cadeaux.")

        await db.delete(result)
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_DELETED",
            f"Suppression du cadeau {giftId}",
            {"gift_id": giftId, "user_id": current_user.id},
        )

    @staticmethod
    async def change_status(db: AsyncSession,
                            current_user: User,
                            giftId: int,
                            gift_status: GiftStatus) -> GiftResponse:

        result: Gift = await GiftService.get_gift_or_raise(db, giftId)

        result.statut = gift_status.status

        today = now_paris() + timedelta(days=4)
        date_expiration = today.replace(hour=1, minute=00, second=00, microsecond=00)

        if gift_status.status == GiftStatusEnum.DISPONIBLE:
            logger.debug(f"Le statut du cadeau est {gift_status.status}")
            if result.gift_delivery:
                result.gift_delivery.lieu_livraison = None
                result.gift_delivery.date_livraison = None
                result.gift_delivery.prix_reel = None
                result.gift_delivery.recu = False
            result.reserve_par_id = None
            result.reserve_par = None
            result.date_reservation = None
            result.expiration_reservation = None
        elif gift_status.status == GiftStatusEnum.PARTAGE:
            # ne rien toucher de plus que le statut
            logger.debug("Passage en PARTAGE, pas de changement de réservation.")
        else:
            # cas PRIS ou RÉSERVÉ
            result.reserve_par = current_user
            result.date_reservation = now_paris()
            result.expiration_reservation = date_expiration

        logger.debug("Attributs de gift : %s", vars(result))

        db.add(result)
        await db.commit()

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_STATUS_CHANGED",
            f"Statut du cadeau {giftId} -> {gift_status.status}",
            {"gift_id": giftId, "user_id": current_user.id, "status": gift_status.status},
        )

        return GiftResponse.model_validate(result)

    @staticmethod
    async def create_gift(db: AsyncSession,
                          current_user: User,
                          gift_created: GiftCreate) -> GiftResponse:

        if current_user.id != gift_created.destinataire_id:
            raise HTTPException(status_code=403, detail="❌ Vous ne pouvez enregistrer un cadeau que pour vous-même.")

        gift_data = gift_created.model_dump(exclude={"destinataire"})
        gift = Gift(**gift_data)
        gift.destinataire_id = current_user.id  # 🔥 c’est cette ligne qui est propre

        db.add(gift)
        await db.commit()
        await db.refresh(gift)

        await TraceService.record_trace(
            db,
            f"{current_user.prenom} {current_user.nom}",
            "GIFT_CREATED",
            f"Creation du cadeau {gift.id}",
            {"gift_id": gift.id, "user_id": current_user.id},
        )

        return GiftResponse.model_validate(gift)

    @staticmethod
    async def get_followed_gifts(
            db: AsyncSession,
            current_user: User,
            group_id: int
    ) -> list[GiftFollowed]:

        # A. Cadeaux réservés ou pris PAR moi, créés PAR des membres du groupe courant
        gifts_followed = []
        result_gift = await db.execute(
            select(Gift)
            .join(User, Gift.destinataire_id == User.id)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(
                Gift.reserve_par_id == current_user.id,
                UserGroup.groupe_id == group_id
            )
            .options(
                selectinload(Gift.destinataire),
                selectinload(Gift.reserve_par),
                selectinload(Gift.gift_delivery),
                selectinload(Gift.gift_idea))
        )
        gifts = result_gift.scalars().all()

        if gifts:
            gifts_followed = [
                GiftFollowed(
                    gift=await build_gift_public_response(gift, group_id, db),
                    delivery=GiftDeliverySchema.model_validate(gift.gift_delivery,
                                                               from_attributes=True) if gift.gift_delivery else None,
                    partage=None  # à remplir si tu en as besoin
                )
                for gift in gifts
            ]

        # B. Cadeaux partagés AVEC moi, créés PAR des membres du groupe courant
        gifts_shared = []
        result_gift_shared = await db.execute(
            select(Gift, GiftShared)
            .join(GiftShared, Gift.id == GiftShared.cadeau_id)
            .join(User, Gift.destinataire_id == User.id)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(
                GiftShared.participant_id == current_user.id,
                UserGroup.groupe_id == group_id
            )
            .options(
                selectinload(Gift.destinataire),
                selectinload(Gift.reserve_par),
                selectinload(Gift.gift_delivery))
        )
        rows = result_gift_shared.all()
        if rows:
            gifts_shared = [
                GiftFollowed(
                    gift=await build_gift_public_response(gift, group_id, db),
                    delivery=GiftDeliverySchema.model_validate(gift.gift_delivery,
                                                               from_attributes=True) if gift.gift_delivery else None,
                    partage=await build_gift_shared_schema(gift_shared, group_id, db)
                )
                for gift, gift_shared in rows
            ]

        return gifts_followed + gifts_shared

    @staticmethod
    async def set_gift_detail(gift: Gift,
                              current_user: User,
                              group_id: int,
                              db: AsyncSession,
                              partage: Optional[list[GiftSharedSchema]] = None) -> GiftDetailResponse:
        return GiftDetailResponse(
            gift=await build_gift_public_response(gift, group_id, db),
            delivery=GiftDeliverySchema.model_validate(gift.gift_delivery) if gift.gift_delivery else None,
            partage=partage,
            ideas = await build_gift_idea_schema(gift.gift_idea, group_id, db) if gift.gift_idea else None,
            est_partage=gift.statut == GiftStatusEnum.PARTAGE,
            droits_utilisateur=GiftService.define_user_role(current_user, gift, partage)
        )

    @staticmethod
    async def get_gift_or_raise(db: AsyncSession,
                                gift_id: int) -> Gift:
        result: Gift | None = (await db.execute(
            select(Gift).where(Gift.id == gift_id)
            .options(
                selectinload(Gift.destinataire),  # charge eager le créateur du cadeau
                selectinload(Gift.reserve_par),
                selectinload(Gift.gift_delivery),
                selectinload(Gift.gift_idea).selectinload(GiftIdeas.proposee_par)
            )
        )).scalars().first()
        if result is None:
            logger.error(f"Cadeau {gift_id} introuvable.")
            raise HTTPException(status_code=404, detail="Cadeau introuvable.")
        return result

    @staticmethod
    def define_user_role(
            current_user: User,
            gift: Gift,
            partages: Optional[list[GiftSharedSchema]] = None
    ) -> RoleUtilisateur:
        if gift.destinataire.id == current_user.id:
            return RoleUtilisateur.CREATEUR
        elif gift.reserve_par and gift.reserve_par_id == current_user.id:
            return RoleUtilisateur.PRENEUR
        elif any(p.participant.id == current_user.id for p in partages):
            return RoleUtilisateur.PARTICIPANT
        else:
            return RoleUtilisateur.SPECTATEUR
