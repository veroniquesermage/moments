import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models import Gift
from app.models import User
from app.schemas.group import GroupResponse
from app.schemas.mailing import FeedbackRequest
from app.schemas.mailing.invite_request import InviteRequest
from app.services.group_service import GroupService
from app.services.mailing.mailjet_adapter import MailjetAdapter
from app.services.trace_service import TraceService
from app.services.user_group_service import UserGroupService


class MailService:

    @staticmethod
    async def send_feedback(
            feedback_request: FeedbackRequest,
            db : AsyncSession,
            current_user: User
    ) -> None:

        try:
            response = MailjetAdapter.send_feedback(feedback_request, current_user)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{current_user.prenom} {current_user.nom}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail de feedback",
                    {"composant": feedback_request.composant,
                            "user_id": current_user.id}
                )

                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur d'envoi du mail d'invitation : {response.json()}"
                )
        except Exception as e:
            logger.error(f"📨 Erreur d'envoi du mail d'invitation")
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Une erreur est survenue lors de l’envoi de l’email. Merci de réessayer plus tard."
            )

    @staticmethod
    async def send_invites(
            invites_request: InviteRequest,
            group_id: int,
            db : AsyncSession,
            current_user: User
    ) -> None:

        group: GroupResponse = await GroupService.get_group(db, group_id)
        existing_users = await UserGroupService.get_existing_users_in_group(db, group_id, invites_request)
        valid_email = [mail for mail in invites_request.emails if mail not in existing_users]

        try:
            response = MailjetAdapter.send_invites(valid_email, group, current_user)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{current_user.prenom} {current_user.nom}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail d'invitation",
                    {"emails": json.dumps(invites_request.emails),
                     "group_id": group_id,
                     "user_id": current_user.id}
                )

                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur d'envoi du mail d'invitation : {response.json()}"
                )
        except Exception as e:
            logger.error(f"📨 Erreur d'envoi du mail d'invitation")
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Une erreur est survenue lors de l’envoi de l’email. Merci de réessayer plus tard."
            )

    @staticmethod
    async def send_alert_update(
            gift_updated: Gift,
            destinataire: User,
            db: AsyncSession
    ):
        try:
            response = await MailjetAdapter.send_alert_update(gift_updated, destinataire)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{destinataire.prenom} {destinataire.nom}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail suite à modification cadeau",
                    {"cadeau_id": gift_updated.id,
                     "mail_to": gift_updated.reserve_par_id
                     }
                )
        except Exception as e:
            logger.error(f"📨 Erreur d'envoi du mail d'invitation")
            logger.exception(e)

    @staticmethod
    async def send_validation_email(
            db: AsyncSession,
            email: str,
            token: str
    ):
        try:
            response = await MailjetAdapter.send_validation_email(email, token)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{email}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail de confirmation de compte",
                    {"token": token}
                )

                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur d'envoi de la validation du mail : {response.json()}"
                )
            else :
                await TraceService.record_trace(
                    db,
                    f"{email}",
                    "CHECK_MAIL",
                    f"Envoi d'un mail de confirmation de compte",
                    {"token": token}
                )
        except Exception as e:
            logger.error(f"📨 Erreur d'envoi du mail de confirmation de compte")
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Une erreur est survenue lors de l’envoi du mail de confirmation de compte. Merci de réessayer plus tard."
            )

    @staticmethod
    async def send_token_password(
            db: AsyncSession,
            email: str,
            token: str
    ):
        try:
            response = await MailjetAdapter.send_token_password(email, token)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{email}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail de réinitialisation de mot de passe",
                    {"token": token}
                )

                raise HTTPException(
                    status_code=500,
                    detail=f"Erreur d'envoi du mail de réinitialisation du mot de passe : {response.json()}"
                )
            else :
                await TraceService.record_trace(
                    db,
                    f"{email}",
                    "RESET_PASSWORD",
                    f"Envoi d'un mail de pour réinitialiser son mot de passe",
                    {"token": token}
                )
        except Exception as e:
            logger.error(f"📨 Erreur lors de l'envoi d'un mail de réinitialisation de mot de passe")
            logger.exception(e)
            raise HTTPException(
                status_code=500,
                detail="Une erreur est survenue lors de l’envoi d'un mail de réinitialisation de mot de passe. Merci de réessayer plus tard."
            )
