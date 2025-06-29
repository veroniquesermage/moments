from typing import Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas import UserDisplaySchema
from app.services import UserGroupService

router = APIRouter(prefix="/utilisateur-groupe", tags=["Utilisateur & Groupe"])


@router.delete("/{groupId}", status_code=204)
async def delete_user_group(
        groupId: int,
        userId: Optional[int] = None,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    await UserGroupService.delete_user_group(db, current_user, groupId, userId)
    return

@router.patch("/{groupId}/surnom", status_code=204)
async def update_nickname(
        groupId: int,
        payload: dict = Body(...),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    nickname = payload.get("nickname")
    if nickname is None:
        raise HTTPException(status_code=422, detail="❌ Le champ 'nickname' est requis.")

    await UserGroupService.update_nickname(db, current_user, groupId, nickname)
    return

@router.patch("/{groupId}/update", response_model=list[UserDisplaySchema])
async def update_roles(
        groupId: int,
        payload: list[UserDisplaySchema],
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> list[UserDisplaySchema] :
    return await UserGroupService.update_role(db, groupId, current_user, payload)