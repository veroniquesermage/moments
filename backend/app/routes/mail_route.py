from fastapi import APIRouter, Depends

from app.dependencies.current_user import get_current_user
from app.models import User
from app.schemas.feedback_schema import FeedbackRequest
from app.services.mailing.mail_service import MailService

router = APIRouter(prefix="/email", tags=["email"])

@router.post("/", status_code=204)
async def send_feedback_mail(
        feedbackRequest: FeedbackRequest,
        current_user: User = Depends(get_current_user) ) :


    return await MailService.send_feedback(feedbackRequest, current_user)