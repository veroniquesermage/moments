from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enum.gift_action_enum import GiftActionEnum
from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user_from_cookie, get_current_group_id
from app.models import User
from app.schemas.gift import EligibilityResponse, GiftStatus, GiftCreate, \
    GiftDetailResponse, RecuPayload, GiftResponse, GiftPriority, GiftPublicResponse, GiftDeliveryUpdate, GiftFollowed
from app.schemas.gift.gift_update import GiftUpdate
from app.services import GiftService

router = APIRouter(prefix="/api/cadeaux", tags=["cadeaux"])

@router.get("", response_model=list[GiftResponse])
@router.get("/", response_model=list[GiftResponse])
async def get_gifts(
        userId: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> list[GiftResponse]:

    effective_user_id = userId or current_user.id
    logger.info(f"L'utilisateur concerné est {effective_user_id}")
    return await GiftService.get_my_gifts(db, effective_user_id)

@router.post("", response_model=GiftResponse)
async def create_gift(
        gift: GiftCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> GiftResponse:

    return await GiftService.create_gift(db, current_user, gift)

@router.put("", response_model=list[GiftResponse])
async def update_all_gifts(
        gifts: list[GiftPriority],
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> list[GiftResponse]:

    return await GiftService.update_all_gifts(db, current_user, gifts)


@router.get("/suivis/{groupId}", response_model=list[GiftFollowed])
async def get_followed_gifts(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> list[GiftFollowed]:

    return await GiftService.get_followed_gifts(db, current_user, groupId)

@router.get("/membre/{user_id}", response_model=list[GiftPublicResponse])
async def get_visible_gifts_for_member(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)) -> list[GiftPublicResponse]:

    return await GiftService.get_visible_gifts_for_member(db, user_id)

@router.get("/{giftId}", response_model=GiftDetailResponse)
async def get_gift(
        giftId: int,
        groupId: int = Depends(get_current_group_id),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> GiftDetailResponse:

    return await GiftService.get_gift(db, giftId, groupId, current_user)

@router.put("/{giftId}", response_model=GiftResponse)
async def update_gift(
        giftId: int,
        giftUpdate: GiftUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> GiftResponse:

    return await GiftService.update_gift(db, current_user, giftId, giftUpdate)

@router.delete("/{giftId}", status_code=204)
async def delete_gift(
        giftId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ):

    await GiftService.delete_gift(db, giftId, current_user)
    return

@router.put("/{giftId}/livraison", response_model=GiftDeliveryUpdate)
async def update_gift_delivery(
        giftId: int,
        giftDeliveryUpdate: GiftDeliveryUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> GiftDeliveryUpdate:

    return await GiftService.update_gift_delivery(db, current_user, giftId, giftDeliveryUpdate)

@router.get("/{giftId}/eligibilite", response_model=EligibilityResponse)
async def verify_eligibility(
        giftId: int,
        action: Optional[GiftActionEnum] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> EligibilityResponse:

    return await GiftService.verify_eligibility(db, giftId, current_user, action)

@router.patch("/{giftId}/recu", response_model=GiftDetailResponse)
async def set_gift_delivery(
        giftId: int,
        payload: RecuPayload,
        groupId: int = Depends(get_current_group_id),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> GiftDetailResponse:

    return await GiftService.set_gift_delivery(db, current_user, giftId, payload.recu, groupId)


@router.put("/{giftId}/changer-statut", response_model=GiftResponse)
async def change_status(
        giftId: int,
        gift_status: GiftStatus,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie) ) -> GiftResponse:

    return await GiftService.change_status(db, current_user, giftId, gift_status)


