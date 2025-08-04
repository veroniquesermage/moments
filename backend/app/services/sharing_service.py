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

        # 2. Suppression des anciens partages
        result = await db.execute(
            delete(GiftShared).where(GiftShared.cadeau_id == gift_id)
        )

        logger.debug(f"Nombre de partages supprimés pour le cadeau {gift_id} : {result.rowcount}")

        # 3. Insertion des nouveaux partages
        for partage in updates:
            db.add(GiftShared(
                cadeau_id=gift_id,
                preneur_id=current_user.id,
                participant_id=partage.participant.id,
                montant=partage.montant,
                rembourse=partage.rembourse
            ))

        # 4. Commit
        await db.commit()

        shared_refresh = (await db.execute(
            select(GiftShared)
            .where(GiftShared.cadeau_id == gift_id)
            .options(
                selectinload(GiftShared.participant),
                selectinload(GiftShared.preneur)
            )
        )).scalars().all()

        shared_schema = [await build_gift_shared_schema(sh, group_id, db) for sh in shared_refresh]
        new_status: GiftStatus
        if gift.statut == GiftStatusEnum.PRIS and len(shared_schema) > 0:
            gift.statut = GiftStatusEnum.PARTAGE
            new_status = GiftStatus(status=GiftStatusEnum.PARTAGE)
            await GiftService.change_status(db, current_user, gift_id, new_status)

        elif gift.statut == GiftStatusEnum.PARTAGE and len(shared_schema) == 0:
            gift.statut = GiftStatusEnum.PRIS
            new_status = GiftStatus(status=GiftStatusEnum.PRIS)
            await GiftService.change_status(db, current_user, gift_id, new_status)

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

        # Maj du remboursement
        existing.rembourse = shared.rembourse

        await db.commit()
        await db.refresh(existing)

        # 🔁 Requête : lignes de partage avec les relations nécessaires
        partage = (await db.execute(
            select(GiftShared)
            .where(GiftShared.cadeau_id == shared.cadeau_id)
            .options(
                selectinload(GiftShared.participant),
                selectinload(GiftShared.preneur)
            )
        )).scalars().all()

        partage_schema = [GiftSharedSchema.model_validate(p) for p in partage]

        # 🔁 Requête : le cadeau avec ses relations
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
        return [await build_gift_shared_schema(entry, group_id, db) for entry in shared_entries]




