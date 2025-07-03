from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from jinja2 import Template
from mailjet_rest import Client

from app.core.config import settings
from app.core.enum import GiftStatusEnum
from app.core.logger import logger
from app.models import User, Gift
from app.schemas.group import GroupResponse
from app.schemas.mailing import FeedbackRequest


class MailjetAdapter:

    @staticmethod
    def send_feedback(
            feedback_request: FeedbackRequest,
            user: User
    ):
        sender_email = settings.mj_sender_email
        feedback_email = settings.mj_feedback_email

        # Lecture du fichier HTML
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "feedback.html"
        template_str = template_path.read_text(encoding="utf-8")

        # Création d’un template Jinja2
        template = Template(template_str)

        # Rendu avec les vraies données
        html_rendered = template.render(
            feedback_request=feedback_request,
            user=user,
            date_envoi=datetime.now(ZoneInfo("Europe/Paris")).strftime("%d/%m/%Y à %Hh%M"),
            user_id=user.id
        )

        mailjet = MailjetAdapter._get_mailjet_client()
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": sender_email,
                        "Name": "Moments-ep"
                    },
                    "To": [
                        {
                            "Email": feedback_email,
                        }
                    ],
                    "Subject": "Feedback envoyé",
                    "HTMLPart": html_rendered
                }
            ]
        }

        return mailjet.send.create(data=data)


    @staticmethod
    def send_invites(
            valid_email: list[str],
            group: GroupResponse,
            user: User):

        sender_email = settings.mj_sender_email

        # Lecture du fichier HTML
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "invite.html"
        template_str = template_path.read_text(encoding="utf-8")

        # Création d’un template Jinja2
        template = Template(template_str)


        invite_url = f"{settings.invitation_link}{group.code}"

        # Rendu avec les vraies données
        html_rendered = template.render(
            groupe= group,
            user=user,
            url_avec_code=invite_url
        )

        mailjet = MailjetAdapter._get_mailjet_client()
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": sender_email,
                        "Name": "Moments-ep"
                    },
                    "To": [
                        {
                            "Email": mail,
                        }
                    ],
                    "Subject": "Invitation à rejoindre un groupe sur (Moments)",
                    "HTMLPart": html_rendered
                }
                for mail in valid_email
            ]
        }

        return mailjet.send.create(data=data)


    @staticmethod
    async def send_alert_update(
            gift_updated: Gift,
            destinataire: User):

        sender_email = settings.mj_sender_email

        # Lecture du fichier HTML
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "alert_udpate.html"
        template_str = template_path.read_text(encoding="utf-8")

        # Création d’un template Jinja2
        template = Template(template_str)

        statut: str = "réservé" if gift_updated.statut == GiftStatusEnum.RESERVE else "pris"

        # Rendu avec les vraies données
        html_rendered = template.render(
            gift= gift_updated,
            statut=statut,
            destinataire=destinataire,
            url= settings.google_redirect_uri
        )

        mail_to: str = gift_updated.reserve_par.email

        mailjet = MailjetAdapter._get_mailjet_client()
        data = {
            'Messages': [
                {
                    "From": {
                        "Email": sender_email,
                        "Name": "Moments-ep"
                    },
                    "To": [
                        {
                            "Email": mail_to,
                        }
                    ],
                    "Subject": "(Moments) Un cadeau que vous avez pris a été modifié",
                    "HTMLPart": html_rendered
                }
            ]
        }

        response = mailjet.send.create(data=data)

        # Log minimal pour voir si ça passe
        logger.info(f"📧 Mailjet response status: {response.status_code}")
        logger.info(f"📧 Mailjet response body: {response.json()}")


    @staticmethod
    def _get_mailjet_client():
        api_key = settings.mj_apikey_public
        api_secret = settings.mj_apikey_private
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        return mailjet