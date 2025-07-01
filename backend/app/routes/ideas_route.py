from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.gift import DuplicationPayload
from app.schemas.gift.gift_idea_create import GiftIdeaCreate
from app.schemas.gift.gift_ideas_response import GiftIdeasResponse
from app.services import GiftIdeasService

router = APIRouter(prefix="/api/idees", tags=["idees"])

@router.post("", response_model=GiftIdeasResponse)
@router.post("/", response_model=GiftIdeasResponse)
async def create_gift_idea(
        gift_idea: GiftIdeaCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> GiftIdeasResponse:

    return await GiftIdeasService.create_gift_idea(db, current_user, gift_idea)

@router.get("/{groupId}", response_model=list[GiftIdeasResponse])
@router.get("/{groupId}/", response_model=list[GiftIdeasResponse])
async def get_my_ideas(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) -> list[GiftIdeasResponse]:

    logger.info(f"L'utilisateur concerné est {current_user}")
    return await GiftIdeasService.get_my_ideas(db, current_user, groupId)


@router.patch("/{ideaId}", status_code=204)
@router.patch("/{ideaId}/", status_code=204)
async def change_visibility(
        ideaId: int,
        payload: dict = Body(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    visibility = payload.get("visibility")
    if visibility is None:
        raise HTTPException(status_code=422, detail="❌ Le champ 'visibility' est requis.")

    await GiftIdeasService.change_visibility(db, current_user, ideaId, visibility)
    return

@router.post("/{ideaId}", response_model=GiftIdeasResponse)
@router.post("/{ideaId}/", response_model=GiftIdeasResponse)
async def duplicate_gift_idea(
        ideaId: int,
        payload: DuplicationPayload,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)) -> GiftIdeasResponse:

    return await GiftIdeasService.duplicate_gift_idea(db, current_user, ideaId, payload.new_dest_id)

@router.delete("/{ideaId}", status_code=204)
@router.delete("/{ideaId}/", status_code=204)
async def delete_gift_idea(
        ideaId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):

    await GiftIdeasService.delete_gift_idea(db, current_user, ideaId)
    return
