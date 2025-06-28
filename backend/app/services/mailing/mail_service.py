from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.schemas.group import GroupResponse
from app.schemas.mailing import FeedbackRequest
from app.schemas.mailing.invite_request import InviteRequest
from app.services import GroupService, UserGroupService
from app.services.mailing.mailjet_adapter import MailjetAdapter


class MailService:

    @staticmethod
    async def send_feedback(
            feedback_request: FeedbackRequest,
            current_user: User
    ) -> None:
        MailjetAdapter.send_feedback(feedback_request, current_user)

    @staticmethod
    async def send_invites(
            invites_request: InviteRequest,
            group_id: int,
            db : AsyncSession,
            current_user: User
    ) -> None:

        group: GroupResponse = await GroupService.get_group(db, current_user, group_id)
        existing_users = await UserGroupService.get_existing_users_in_group(db, group_id, invites_request)
        valid_email = [mail for mail in invites_request.emails if mail not in existing_users]
        MailjetAdapter.send_invites(valid_email, group, current_user)
