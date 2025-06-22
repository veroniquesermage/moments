from app.core.logger import logger
from app.models import User
from app.schemas.feedback_schema import FeedbackRequest
from app.services.mailing.mailjet_adapter import MailjetAdapter


class MailService:

    @staticmethod
    async def send_feedback(
            feedback_request: FeedbackRequest,
            current_user: User
    ) -> None:
        MailjetAdapter.send_feedback(feedback_request, current_user)

