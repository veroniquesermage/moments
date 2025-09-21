import json

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models import Gift, User, Invitation
from app.schemas.group import GroupResponse
from app.schemas.mailing import InviteResponse
from app.schemas.mailing.invite_request import InviteRequest
from app.services.group_service import GroupService
from app.services.mailing.mailjet_adapter import MailjetAdapter
from app.services.trace_service import TraceService
from app.services.user_group_service import UserGroupService
from app.utils.email_validator import validate_email_format, sanitize_email_list, generate_invitation_token, calculate_expiration_date


class MailService:

    @staticmethod
    async def send_invites(
            invites_request: InviteRequest,
            group_id: int,
            db : AsyncSession,
            current_user: User
    ) -> InviteResponse:

        # Nettoyer et normaliser les emails
        cleaned_emails = sanitize_email_list(invites_request.emails)

        # Valider le format des emails
        emails_valides = []
        emails_invalides = []
        for email in cleaned_emails:
            if validate_email_format(email):
                emails_valides.append(email)
            else:
                emails_invalides.append(email)

        # Récupérer le groupe et les utilisateurs existants
        group: GroupResponse = await GroupService.get_group(db, group_id)
        existing_users = await UserGroupService.get_existing_users_in_group(db, group_id, InviteRequest(emails=emails_valides))

        # Séparer les emails à envoyer et ceux déjà membres
        emails_a_envoyer = [email for email in emails_valides if email not in existing_users]
        emails_deja_membres = [email for email in emails_valides if email in existing_users]

        emails_envoyes = []

        if emails_a_envoyer:
            try:
                # Créer les invitations avec tokens avant l'envoi
                invitations_data = []
                from app.utils.date_helper import now_paris
                date_now = now_paris().replace(tzinfo=None)
                date_expiration = calculate_expiration_date().replace(tzinfo=None)

                for email in emails_a_envoyer:
                    token = generate_invitation_token()
                    invitation_data = {
                        'email': email,
                        'token': token,
                        'groupe_id': group_id,
                        'envoye_par_id': current_user.id,
                        'date_envoi': date_now,
                        'date_expiration': date_expiration,
                        'utilise': False
                    }
                    invitations_data.append(invitation_data)

                # Envoyer les emails avec les tokens
                response = MailjetAdapter.send_invites_with_tokens(invitations_data, group, current_user)

                if response.status_code != 200:
                    await TraceService.record_trace(
                        db,
                        f"{current_user.prenom} {current_user.nom}",
                        "ERROR",
                        f"Erreur lors de l'envoi d'un mail d'invitation",
                        {"emails": json.dumps(emails_a_envoyer),
                         "group_id": group_id,
                         "user_id": current_user.id}
                    )

                    raise HTTPException(
                        status_code=500,
                        detail=f"Erreur d'envoi du mail d'invitation : {response.json()}"
                    )
                else:
                    # Enregistrer les invitations en base
                    for invitation_data in invitations_data:
                        invitation = Invitation(**invitation_data)
                        db.add(invitation)
                    await db.commit()
                    emails_envoyes = emails_a_envoyer

            except Exception as e:
                logger.error(f"📨 Erreur d'envoi du mail d'invitation")
                logger.exception(e)
                raise HTTPException(
                    status_code=500,
                    detail="Une erreur est survenue lors de l'envoi de l'email. Merci de réessayer plus tard."
                )

        return InviteResponse(
            emails_envoyes=emails_envoyes,
            emails_invalides=emails_invalides,
            emails_deja_membres=emails_deja_membres
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
                detail="Une erreur est survenue lors de l'envoi d'un mail de réinitialisation de mot de passe. Merci de réessayer plus tard."
            )

    @staticmethod
    async def send_sharing_added(
            db: AsyncSession,
            cadeau: Gift,
            participant: User,
            preneur: User,
            montant: float
    ):
        """Envoie un email de notification quand un participant est ajouté à un partage"""
        try:
            response = await MailjetAdapter.send_sharing_added(cadeau, participant, preneur, montant)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{preneur.prenom} {preneur.nom}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail de notification de partage ajouté",
                    {"cadeau_id": cadeau.id, "participant_id": participant.id, "preneur_id": preneur.id}
                )
            else:
                await TraceService.record_trace(
                    db,
                    f"{preneur.prenom} {preneur.nom}",
                    "SHARING_EMAIL_SENT",
                    f"Email de partage ajouté envoyé à {participant.prenom}",
                    {"cadeau_id": cadeau.id, "participant_id": participant.id, "preneur_id": preneur.id}
                )
        except Exception as e:
            logger.error(f"📨 Erreur d'envoi du mail de partage ajouté")
            logger.exception(e)

    @staticmethod
    async def send_sharing_removed(
            db: AsyncSession,
            cadeau: Gift,
            participant: User,
            preneur: User,
            montant: float
    ):
        """Envoie un email de notification quand un participant est retiré d'un partage"""
        try:
            response = await MailjetAdapter.send_sharing_removed(cadeau, participant, preneur, montant)
            if response.status_code != 200:
                await TraceService.record_trace(
                    db,
                    f"{preneur.prenom} {preneur.nom}",
                    "ERROR",
                    f"Erreur lors de l'envoi d'un mail de notification de partage retiré",
                    {"cadeau_id": cadeau.id, "participant_id": participant.id, "preneur_id": preneur.id}
                )
            else:
                await TraceService.record_trace(
                    db,
                    f"{preneur.prenom} {preneur.nom}",
                    "SHARING_EMAIL_SENT",
                    f"Email de partage retiré envoyé à {participant.prenom}",
                    {"cadeau_id": cadeau.id, "participant_id": participant.id, "preneur_id": preneur.id}
                )
        except Exception as e:
            logger.error(f"📨 Erreur d'envoi du mail de partage retiré")
            logger.exception(e)
