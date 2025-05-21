from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.enum.gift_action_enum import GiftActionEnum
from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.gift import GiftResponse, EligibilityResponse, GiftStatus, GiftCreate, GiftFollowed
from app.schemas.gift.gift_update import GiftUpdate
from app.services import GiftService

router = APIRouter(prefix="/cadeaux", tags=["cadeaux"])

@router.get("/", response_model=list[GiftResponse])
async def get_gifts(
        userId: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> list[GiftResponse]:

    effective_user_id = userId or current_user.id
    logger.info(f"L'utilisateur concerné est {effective_user_id}")
    return await GiftService.get_gifts(db, effective_user_id)

@router.post("/", response_model=GiftResponse)
async def create_gift(
        gift: GiftCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> GiftResponse:

    return await GiftService.create_gift(db, current_user, gift)

@router.get("/suivis", response_model=list[GiftFollowed])
async def get_followed_gifts(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> list[GiftFollowed]:

    return await GiftService.get_followed_gifts(db, current_user)

@router.get("/{giftId}", response_model=GiftResponse)
async def get_gift(
        giftId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> GiftResponse:

    return await GiftService.get_gift(db, giftId, current_user)

@router.put("/{giftId}", response_model=GiftResponse)
async def update_gift(
        giftId: int,
        gift: GiftUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> GiftResponse:

    return await GiftService.update_gift(db, giftId, current_user, gift)

@router.delete("/{giftId}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gift(
        giftId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ):

    await GiftService.delete_gift(db, giftId, current_user)

@router.get("/{giftId}/eligibilite", response_model=EligibilityResponse)
async def verify_eligibility(
        giftId: int,
        action: Optional[GiftActionEnum] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> EligibilityResponse:

    return await GiftService.verify_eligibility(db, giftId, current_user, action)

@router.put("/{giftId}/changer-statut", response_model=GiftResponse)
async def change_status(
        giftId: int,
        gift_status: GiftStatus,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> GiftResponse:

    return await GiftService.change_status(db, current_user, giftId, gift_status)


