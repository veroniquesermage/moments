from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.group import GroupResponse, GroupCreate, GroupDetails, GroupUpdate
from app.services.group_service import GroupService

router = APIRouter(prefix="/api/groupe", tags=["groupe"])


@router.post("", response_model=GroupResponse)
async def create_group(
        group: GroupCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await GroupService.create_group(db, current_user, group)


@router.get("", response_model=list[GroupResponse])
async def get_groups(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await GroupService.get_groups(db, current_user )

@router.post("/rejoindre/{code}", response_model=GroupResponse)
async def get_groups(
        code: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)

):
    return await GroupService.join_group(db, current_user, code)

@router.get("/{groupId}", response_model=GroupResponse)
async def get_group(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> GroupResponse:
    return await GroupService.get_group(db, current_user, groupId )

@router.patch("/{groupId}", response_model=GroupResponse)
async def update_group(
        groupId: int,
        group: GroupUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> GroupResponse:
    return await GroupService.update_group(db, current_user, group, groupId )

@router.delete("/{groupId}", status_code=204 )
async def delete_group(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return await GroupService.delete_group(db, current_user, groupId)

@router.get("/{groupId}/details", response_model=GroupDetails)
async def get_group_details(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
) -> GroupDetails:
    return await GroupService.get_group_details(db, current_user, groupId)