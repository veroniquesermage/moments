from typing import Optional

from fastapi import HTTPException
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.enum import RoleUtilisateur, GiftStatusEnum
from app.core.logger import logger
from app.models import User, GiftShared, Gift, GiftPurchaseInfo
from app.schemas.gift import GiftSharedSchema, GiftDetailResponse, GiftStatus
from app.services.builders import build_gift_shared_schema
from app.services.trace_service import TraceService


class SharingService:

    @staticmethod
    async def save_all_shares(
        db: AsyncSession,
        current_user: User,
        gift_id: int,
        updates: list[GiftSharedSchema],
            group_id: int
    ) -> GiftDetailResponse:

        # 1. Récupération du cadeau et vérification des droits
        # dans la méthode concernée
        from app.services.gift_service import GiftService
        gift = await GiftService.get_gift_or_raise(db, gift_id)

        if gift.reserve_par_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Seul le preneur peut modifier le partage."
            )

        try:
            # 2. Récupération des anciens partages pour comparaison (avant suppression)
            anciens_partages_result = await db.execute(
                select(GiftShared)
                .where(GiftShared.cadeau_id == gift_id)
                .options(selectinload(GiftShared.participant))
            )
            anciens_partages = anciens_partages_result.scalars().all()

            # Créer des maps pour faciliter la comparaison
            anciens_map = {p.participant_id: p for p in anciens_partages}
            nouveaux_map = {p.participant.id: p for p in updates}

            # 3. Suppression des anciens partages
            result = await db.execute(
                delete(GiftShared).where(GiftShared.cadeau_id == gift_id)
            )

            logger.debug(f"Nombre de partages supprimés pour le cadeau {gift_id} : {result.rowcount}")

            # 4. Insertion des nouveaux partages
            for partage in updates:
                db.add(GiftShared(
                    cadeau_id=gift_id,
                    preneur_id=current_user.id,
                    participant_id=partage.participant.id,
                    montant=partage.montant,
                    rembourse=partage.rembourse
                ))

            # 5. Flush pour obtenir les IDs sans commit complet
            await db.flush()

            # 5. Vérification du nombre réel de partages en base (logique originale)
            shared_refresh = (await db.execute(
                select(GiftShared)
                .where(GiftShared.cadeau_id == gift_id)
                .options(
                    selectinload(GiftShared.participant),
                    selectinload(GiftShared.preneur)
                )
            )).scalars().all()

            shared_schema = []
            for sh in shared_refresh:
                schema = await build_gift_shared_schema(sh, group_id, db)
                shared_schema.append(schema)

            # 6. Déterminer le statut selon le nombre RÉEL en base (logique originale)
            if gift.statut == GiftStatusEnum.PRIS and len(shared_schema) > 0:
                gift.statut = GiftStatusEnum.PARTAGE
            elif gift.statut == GiftStatusEnum.PARTAGE and len(shared_schema) == 0:
                gift.statut = GiftStatusEnum.PRIS

            # 7. Commit atomique : partages + statut cadeau
            await db.commit()

            # 8. Envoi des emails de notification après commit réussi
            await SharingService._send_sharing_notifications(
                db, gift, current_user, anciens_map, nouveaux_map
            )

            await TraceService.record_trace(
                db,
                f"{current_user.prenom} {current_user.nom}",
                "SHARING_SAVED",
                f"Enregistrement des partages pour le cadeau {gift_id}",
                {"gift_id": gift_id, "user_id": current_user.id},
            )

        except Exception as e:
            await db.rollback()
            logger.error(f"Erreur lors de la sauvegarde des partages pour le cadeau {gift_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la sauvegarde des partages"
            )
        # 5. Retour d’un GiftDetailResponse mis à jour
        return await GiftService.set_gift_detail(gift, current_user, group_id, db, shared_schema)

    @staticmethod
    async def get_shares_for_user(
            db: AsyncSession,
            gift_id: int,
            user_id: int,
            role_user: RoleUtilisateur
    ) -> Optional[list[GiftSharedSchema]]:

        if role_user == RoleUtilisateur.PRENEUR:
            query = (
                select(GiftShared)
                .where(and_(
                    GiftShared.cadeau_id == gift_id,
                    GiftShared.preneur_id == user_id
                ))
                .options(selectinload(GiftShared.participant))
            )
        elif role_user == RoleUtilisateur.PARTICIPANT:
            query = (
                select(GiftShared)
                .where(and_(
                    GiftShared.cadeau_id == gift_id,
                    GiftShared.participant_id == user_id
                ))
                .options(selectinload(GiftShared.preneur))
            )
        else:
            return None

        result = await db.execute(query)
        shared_entries = result.scalars().all()
        return [GiftSharedSchema.model_validate(entry) for entry in shared_entries] if shared_entries else None

    @staticmethod
    async def set_gift_refund(db: AsyncSession, current_user: User, shared: GiftSharedSchema, group_id: int) -> GiftDetailResponse:
        logger.debug(
            f"Marquage du cadeau {shared.cadeau_id} comme remboursé pour l'utilisateur : {shared.participant.id}")

        # Vérif du preneur
        if shared.preneur.id != current_user.id:
            raise HTTPException(status_code=403,
                                detail="Seule la personne qui a pris le cadeau peut gérer le remboursement.")

        # Récup de la ligne GiftShared à modifier
        existing: GiftShared = (await db.execute(
            select(GiftShared).where(
                and_(
                    GiftShared.cadeau_id == shared.cadeau_id,
                    GiftShared.participant_id == shared.participant.id
                )
            )
        )).scalars().first()

        if not existing:
            raise HTTPException(status_code=403, detail="Ce cadeau n'est pas un cadeau partagé.")

        try:
            # Pré-chargement du cadeau avec ses relations AVANT modification
            gift: Gift = (await db.execute(
                select(Gift)
                .where(Gift.id == shared.cadeau_id)
                .options(
                    selectinload(Gift.destinataire),
                    selectinload(Gift.reserve_par),
                    selectinload(Gift.gift_delivery),
                    selectinload(Gift.gift_idea),
                    selectinload(Gift.gift_purchase_info).selectinload(GiftPurchaseInfo.compte_tiers)
                )
            )).scalars().first()

            if not gift:
                raise HTTPException(status_code=404, detail="Cadeau introuvable.")

            # Maj du remboursement
            existing.rembourse = shared.rembourse

            # Commit de la modification
            await db.commit()
            await db.refresh(existing)

            # Récupération des partages après commit (données à jour)
            partage = (await db.execute(
                select(GiftShared)
                .where(GiftShared.cadeau_id == shared.cadeau_id)
                .options(
                    selectinload(GiftShared.participant),
                    selectinload(GiftShared.preneur)
                )
            )).scalars().all()

            partage_schema = [GiftSharedSchema.model_validate(p) for p in partage]

        except Exception as e:
            await db.rollback()
            logger.error(f"Erreur lors de la mise à jour du remboursement pour le cadeau {shared.cadeau_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la mise à jour du remboursement"
            )

        from app.services.gift_service import GiftService
        return await GiftService.set_gift_detail(gift, current_user, group_id, db, partage_schema)

    @staticmethod
    async def get_all_shares_for_gift(db: AsyncSession, gift_id: int, group_id: int) -> list[GiftSharedSchema]:
        query = await db.execute(
            select(GiftShared)
            .where(GiftShared.cadeau_id == gift_id)
            .options(
                selectinload(GiftShared.participant),
                selectinload(GiftShared.preneur)
            )
        )
        shared_entries = query.scalars().all()
        result = []
        for entry in shared_entries:
            schema = await build_gift_shared_schema(entry, group_id, db)
            result.append(schema)
        return result

    @staticmethod
    async def delete_share(db: AsyncSession,
                           current_user: User,
                           partage_id: int,
                           group_id: int) :

        query = await db.execute(
            select(GiftShared).where(
                and_(
                    GiftShared.id == partage_id,
                    GiftShared.preneur_id == current_user.id
                )
            )
        )

        shared: GiftShared = query.scalars().first()

        gift_id = shared.cadeau_id

        if not shared:
            raise HTTPException(status_code=404, detail="Partage introuvable ou vous n'avez pas les droits pour le supprimer.")

        await db.delete(shared)
        await db.commit()

        from app.services.gift_service import GiftService
        gift: GiftDetailResponse = await GiftService.get_gift(db, gift_id, group_id, current_user)

        if not gift.partage:
            gift.gift.statut = GiftStatusEnum.PRIS
            await GiftService.change_status(db, current_user, gift_id, GiftStatus(status=GiftStatusEnum.PRIS))

    @staticmethod
    async def _send_sharing_notifications(
            db: AsyncSession,
            gift: Gift,
            preneur: User,
            anciens_map: dict,
            nouveaux_map: dict
    ):
        """Envoie les emails de notification pour les changements de partage"""
        from app.services.mailing.mail_service import MailService

        # Participants ajoutés (présents dans nouveaux mais pas dans anciens)
        for participant_id, nouveau_partage in nouveaux_map.items():
            if participant_id not in anciens_map:
                # Nouveau participant
                await MailService.send_sharing_added(
                    db, gift, nouveau_partage.participant, preneur, nouveau_partage.montant
                )
                logger.info(f"Email d'ajout de partage envoyé à {nouveau_partage.participant.email}")

        # Participants supprimés (présents dans anciens mais pas dans nouveaux)
        for participant_id, ancien_partage in anciens_map.items():
            if participant_id not in nouveaux_map:
                # Participant retiré
                await MailService.send_sharing_removed(
                    db, gift, ancien_partage.participant, preneur, ancien_partage.montant
                )
                logger.info(f"Email de suppression de partage envoyé à {ancien_partage.participant.email}")

        # Note: Les participants dont seul le montant a changé ne reçoivent pas d'email
        # car ce n'est qu'une modification de montant, pas un ajout/suppression




