from fastapi import APIRouter, Depends, HTTPException
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


@router.delete("/{groupId}/invitations/{invitationId}", status_code=204)
async def delete_invitation(
        groupId: int,
        invitationId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    # Vérifier que l'utilisateur est admin du groupe
    await GroupService.get_group_if_admin(current_user, db, groupId)

    success = await InvitationService.delete_invitation(db, invitationId, current_user, groupId)
    if not success:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")


@router.post("/{groupId}/invitations/{invitationId}/resend", status_code=200)
async def resend_invitation(
        groupId: int,
        invitationId: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user_from_cookie)
):
    # Vérifier que l'utilisateur est admin du groupe
    await GroupService.get_group_if_admin(current_user, db, groupId)

    invitation = await InvitationService.resend_invitation(db, invitationId, current_user, groupId)
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation non trouvée")

    # Envoyer le nouveau mail d'invitation
    from app.services.mailing.mail_service import MailService
    from app.services.mailing.mailjet_adapter import MailjetAdapter

    group = await GroupService.get_group(db, groupId)
    invitation_data = {
        'email': invitation.email,
        'token': invitation.token,
        'groupe_id': invitation.groupe_id,
        'envoye_par_id': invitation.envoye_par_id,
        'date_envoi': invitation.date_envoi,
        'date_expiration': invitation.date_expiration,
        'utilise': invitation.utilise
    }

    try:
        response = MailjetAdapter.send_invites_with_tokens([invitation_data], group, current_user)
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du mail")

        return {"message": "Invitation renvoyée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erreur lors de l'envoi du mail")
