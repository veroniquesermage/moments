from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.current_user import get_current_user, get_current_group_id
from app.models import User
from app.schemas.gift import GiftDetailResponse, GiftSharedSchema
from app.services.sharing_service import SharingService

router = APIRouter(prefix="/api/partage", tags=["partage"])

@router.patch("/rembourse/", response_model=GiftDetailResponse)
async def verify_eligibility(
        shared: GiftSharedSchema,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),
        group_id: int = Depends(get_current_group_id)) -> GiftDetailResponse:
    return await SharingService.set_gift_refund(db, current_user, shared, group_id)

@router.put("/{gift_id}/", response_model=GiftDetailResponse)
async def update_partage(
    gift_id: int,
    updates: list[GiftSharedSchema],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    group_id: int = Depends(get_current_group_id)) -> GiftDetailResponse:
    return await SharingService.save_all_shares(db, current_user, gift_id, updates, group_id)
