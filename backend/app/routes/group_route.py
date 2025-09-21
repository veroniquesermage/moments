from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.current_user import get_current_user_from_cookie, get_current_user_from_cookie_with_tiers
from app.models import User
from app.schemas.group import GroupResponse, GroupCreate, GroupDetails, GroupUpdate
from app.schemas.invitation_response import InvitationResponse
from app.services.group_service import GroupService
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/api/groupe", tags=["groupe"])


@router.post("", response_model=GroupResponse, status_code=201)
async def create_group(
        group: GroupCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    return await GroupService.create_group(db, current_user, group)


@router.get("", response_model=list[GroupResponse])
async def get_groups(
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    return await GroupService.get_groups(db, current_user )

@router.post("/rejoindre/token/{token}", response_model=GroupResponse)
async def join_group_with_token(
        token: str,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    return await GroupService.join_group_with_token(db, current_user, token)

@router.get("/{groupId}", response_model=GroupResponse)
async def get_group(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
) -> GroupResponse:
    return await GroupService.get_group(db, groupId )

@router.patch("/{groupId}", response_model=GroupResponse)
async def update_group(
        groupId: int,
        group: GroupUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
) -> GroupResponse:
    return await GroupService.update_group(db, current_user, group, groupId )

@router.delete("/{groupId}", status_code=204 )
async def delete_group(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    return await GroupService.delete_group(db, current_user, groupId)

@router.get("/{groupId}/details", response_model=GroupDetails)
async def get_group_details(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = get_current_user_from_cookie_with_tiers()
) -> GroupDetails:
    return await GroupService.get_group_details(db, current_user, groupId)


@router.get("/{groupId}/invitations", response_model=list[InvitationResponse])
async def get_pending_invitations(
        groupId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
) -> list[InvitationResponse]:
    # Vérifier que l'utilisateur est admin du groupe avant de retourner les invitations
    await GroupService.get_group_if_admin(current_user, db, groupId)
    return await InvitationService.get_pending_invitations(db, groupId)
