import base64
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

        # Lire le guide utilisateur PDF et l'encoder en base64
        guide_pdf_path = Path(__file__).resolve().parents[4] / "frontend" / "src" / "assets" / "docs" / "Guide utilisateur - Invités Moments.pdf"
        guide_pdf_base64 = None

        try:
            if guide_pdf_path.exists():
                pdf_content = guide_pdf_path.read_bytes()
                guide_pdf_base64 = base64.b64encode(pdf_content).decode()
                logger.info(f"📖 Guide utilisateur chargé pour envoi en pièce jointe")
            else:
                logger.warning(f"📖 Guide utilisateur non trouvé: {guide_pdf_path}")
        except Exception as e:
            logger.error(f"📖 Erreur lors du chargement du guide utilisateur: {e}")

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

            message = {
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
            }

            # Ajouter la pièce jointe si le PDF a été chargé
            if guide_pdf_base64:
                message["Attachments"] = [
                    {
                        "ContentType": "application/pdf",
                        "Filename": "Guide utilisateur - Invités Moments.pdf",
                        "Base64Content": guide_pdf_base64
                    }
                ]

            messages.append(message)

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
    async def send_sharing_added(
            cadeau: Gift,
            participant: User,
            preneur: User,
            montant: float
    ):
        """Envoie un email quand un participant est ajouté à un partage"""
        sender_email = settings.mj_sender_email

        # Lecture du template
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "sharing_added.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        # Rendu avec les données
        html_rendered = template.render(
            participant=participant,
            preneur=preneur,
            cadeau=cadeau,
            montant=montant,
            app_url=settings.app_url,
            date_envoi=now_paris().strftime("%d/%m/%Y à %H:%M")
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
                            "Email": participant.email,
                        }
                    ],
                    "Subject": "(Moments) Vous participez à un présent collectif",
                    "HTMLPart": html_rendered
                }
            ]
        }

        response = mailjet.send.create(data=data)
        logger.info(f"📧 Email partage ajouté envoyé à {participant.email}, status: {response.status_code}")
        return response

    @staticmethod
    async def send_sharing_removed(
            cadeau: Gift,
            participant: User,
            preneur: User,
            montant: float
    ):
        """Envoie un email quand un participant est retiré d'un partage"""
        sender_email = settings.mj_sender_email

        # Lecture du template
        template_path = Path(__file__).resolve().parents[2] / "templates" / "mails" / "sharing_removed.html"
        template_str = template_path.read_text(encoding="utf-8")
        template = Template(template_str)

        # Rendu avec les données
        html_rendered = template.render(
            participant=participant,
            preneur=preneur,
            cadeau=cadeau,
            montant=montant,
            app_url=settings.app_url,
            date_envoi=now_paris().strftime("%d/%m/%Y à %H:%M")
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
                            "Email": participant.email,
                        }
                    ],
                    "Subject": "(Moments) Modification dans l'organisation d'un présent collectif",
                    "HTMLPart": html_rendered
                }
            ]
        }

        response = mailjet.send.create(data=data)
        logger.info(f"📧 Email partage retiré envoyé à {participant.email}, status: {response.status_code}")
        return response

    @staticmethod
    def _get_mailjet_client():
        api_key = settings.mj_apikey_public
        api_secret = settings.mj_apikey_private
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        return mailjet
