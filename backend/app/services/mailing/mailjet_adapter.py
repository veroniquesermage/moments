from pathlib import Path

from jinja2 import Template
from mailjet_rest import Client

from app.core.config import settings
from app.core.enum import GiftStatusEnum
from app.core.logger import logger
from app.models import User, Gift
from app.schemas.group import GroupResponse
from app.utils.date_helper import now_paris


class MailjetAdapter:

    @staticmethod
    def send_invites_with_tokens(
            invitations_data: list[dict],
            group: GroupResponse,
            user: User):

        sender_email = settings.mj_sender_email

        # Lecture du fichier HTML
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "invite.html"
        template_str = template_path.read_text(encoding="utf-8")

        # Création d'un template Jinja2
        template = Template(template_str)

        messages = []
        for invitation_data in invitations_data:
            # Créer l'URL avec le token au lieu du code
            invite_url = f"{settings.invitation_link.replace('inviteCode=', 'inviteToken=')}{invitation_data['token']}"

            # Rendu avec les vraies données
            html_rendered = template.render(
                groupe=group,
                user=user,
                url_avec_code=invite_url
            )

            messages.append({
                "From": {
                    "Email": sender_email,
                    "Name": "Moments-ep"
                },
                "To": [
                    {
                        "Email": invitation_data['email'],
                    }
                ],
                "Subject": "Invitation à rejoindre un groupe sur (Moments)",
                "HTMLPart": html_rendered
            })

        mailjet = MailjetAdapter._get_mailjet_client()
        data = {'Messages': messages}

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

    @staticmethod
    async def send_validation_email(
                email: str,
                token: str):

        sender_email = settings.mj_sender_email
        invite_url = f"{settings.check_mail}{token}"

        # Lecture du fichier HTML
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "verify_email.html"
        template_str = template_path.read_text(encoding="utf-8")

        # Création d’un template Jinja2
        template = Template(template_str)

        # Rendu avec les vraies données
        html_rendered = template.render(
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
                            "Email": email,
                        }
                    ],
                    "Subject": "(Moments) Validez votre email pour nous rejoindre",
                    "HTMLPart": html_rendered
                }
            ]
        }

        response = mailjet.send.create(data=data)

        # Log minimal pour voir si ça passe
        logger.info(f"📧 Mailjet response status: {response.status_code}")

        return response

    @staticmethod
    async def send_token_password(
            email: str,
            token: str):

        sender_email = settings.mj_sender_email
        password_url = f"{settings.reset_password}{token}"

        # Lecture du fichier HTML
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "reset_password.html"
        template_str = template_path.read_text(encoding="utf-8")

        # Création d’un template Jinja2
        template = Template(template_str)

        # Rendu avec les vraies données
        html_rendered = template.render(
            url_avec_code=password_url
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
                            "Email": email,
                        }
                    ],
                    "Subject": "(Moments) Réinitialisez votre mot de passe",
                    "HTMLPart": html_rendered
                }
            ]
        }

        response = mailjet.send.create(data=data)

        # Log minimal pour voir si ça passe
        logger.info(f"📧 Mailjet response status: {response.status_code}")

        return response

    @staticmethod
    def _get_mailjet_client():
        api_key = settings.mj_apikey_public
        api_secret = settings.mj_apikey_private
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        return mailjet
