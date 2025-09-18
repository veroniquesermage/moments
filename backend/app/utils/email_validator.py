import re
import uuid
from datetime import datetime, timedelta
from app.utils.date_helper import now_paris


def validate_email_format(email: str) -> bool:
    """
    Valide le format d'un email avec une regex robuste.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def sanitize_email_list(emails: list[str]) -> list[str]:
    """
    Nettoie et normalise une liste d'emails.
    """
    cleaned_emails = []
    for email in emails:
        email = email.strip().lower()
        if email:
            cleaned_emails.append(email)
    return cleaned_emails


def generate_invitation_token() -> str:
    """
    Génère un token unique pour une invitation.
    """
    return str(uuid.uuid4())


def calculate_expiration_date() -> datetime:
    """
    Calcule la date d'expiration (30 jours à partir de maintenant).
    """
    return now_paris() + timedelta(days=30)