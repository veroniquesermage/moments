from datetime import datetime
from pathlib import Path

from mailjet_rest import Client

from app.core.config import settings
from app.core.logger import logger
from app.models import User
from app.schemas.feedback_schema import FeedbackRequest
from jinja2 import Template


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
            date_envoi=datetime.now().strftime("%d/%m/%Y à %Hh%M"),
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

        result = mailjet.send.create(data=data)
        logger.info(f"{result.status_code}")
        logger.info(f"{result.json()}")

    @staticmethod
    def _get_mailjet_client():
        api_key = settings.mj_apikey_public
        api_secret = settings.mj_apikey_private
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        return mailjet