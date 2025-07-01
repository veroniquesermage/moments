from fastapi import APIRouter, Depends

from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.current_user import get_current_user, get_current_group_id
from app.models import User
from app.schemas.mailing import FeedbackRequest
from app.schemas.mailing.invite_request import InviteRequest
from app.services.mailing.mail_service import MailService

router = APIRouter(prefix="/api/email", tags=["email"])

@router.post("/feedback/", status_code=204)
async def send_feedback_mail(
        feedbackRequest: FeedbackRequest,
        current_user: User = Depends(get_current_user) ) :


    return await MailService.send_feedback(feedbackRequest, current_user)

@router.post("/invitation/", status_code=204)
async def send_feedback_mail(
        inviteRequest: InviteRequest,
        group_id: int = Depends(get_current_group_id),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user) ) :


    return await MailService.send_invites(inviteRequest, group_id, db, current_user)