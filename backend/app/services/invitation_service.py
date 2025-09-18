from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Invitation, User, UserGroup, Group
from app.schemas.invitation_response import InvitationResponse
from app.schemas.invitation_validation_result import InvitationValidationResult
from app.utils.date_helper import now_paris


class InvitationService:

    @staticmethod
    async def get_pending_invitations(
        db: AsyncSession,
        group_id: int
    ) -> list[InvitationResponse]:
        """
        Récupère les invitations en attente pour un groupe.
        Une invitation est considérée comme:
        - En attente: si la personne n'a pas encore rejoint le groupe ET le code n'a pas été refreshé
        - Expirée: si le code d'invitation a été refreshé après l'envoi de l'invitation
        """

        # Récupérer toutes les invitations du groupe avec les infos du groupe
        result = await db.execute(
            select(Invitation)
            .options(selectinload(Invitation.groupe), selectinload(Invitation.envoye_par))
            .where(Invitation.groupe_id == group_id)
        )
        invitations = result.scalars().all()

        # Récupérer les emails des utilisateurs déjà dans le groupe
        result = await db.execute(
            select(User.email)
            .join(UserGroup, User.id == UserGroup.utilisateur_id)
            .where(UserGroup.groupe_id == group_id)
        )
        existing_emails = set(result.scalars().all())

        # Filtrer et déterminer le statut de chaque invitation
        pending_invitations = []
        for invitation in invitations:
            # Ignorer si la personne a déjà rejoint le groupe
            if invitation.email in existing_emails:
                continue

            # Déterminer le statut: expirée si envoyée avant le dernier refresh du code
            is_expired = (
                invitation.groupe.date_refresh_code and
                invitation.date_envoi < invitation.groupe.date_refresh_code
            )

            status = "EXPIREE" if is_expired else "EN_ATTENTE"

            pending_invitations.append(
                InvitationResponse(
                    id=invitation.id,
                    email=invitation.email,
                    date_envoi=invitation.date_envoi,
                    envoye_par_nom=f"{invitation.envoye_par.prenom} {invitation.envoye_par.nom}",
                    statut=status
                )
            )

        return pending_invitations

    @staticmethod
    async def validate_and_use_token(
        db: AsyncSession,
        token: str
    ) -> InvitationValidationResult:
        """
        Valide un token d'invitation et le marque comme utilisé si valide.
        """
        # Récupérer l'invitation avec le token
        result = await db.execute(
            select(Invitation)
            .options(selectinload(Invitation.groupe))
            .where(Invitation.token == token)
        )
        invitation = result.scalar_one_or_none()

        if not invitation:
            return InvitationValidationResult(
                is_valid=False,
                error_message="Ce lien d'invitation n'est plus valide"
            )

        # Vérifier si déjà utilisé
        if invitation.utilise:
            return InvitationValidationResult(
                is_valid=False,
                error_message="Vous avez déjà rejoint ce groupe avec cette invitation"
            )

        # Vérifier l'expiration
        current_time = now_paris().replace(tzinfo=None)
        if invitation.date_expiration and current_time > invitation.date_expiration:
            return InvitationValidationResult(
                is_valid=False,
                error_message="Ce lien d'invitation a expiré"
            )

        # Marquer comme utilisé
        invitation.utilise = True
        await db.commit()

        return InvitationValidationResult(
            is_valid=True,
            invitation=invitation,
            group=invitation.groupe
        )

    @staticmethod
    async def get_group_from_token(
        db: AsyncSession,
        token: str
    ) -> Group | None:
        """
        Récupère le groupe associé à un token d'invitation sans le valider.
        """
        result = await db.execute(
            select(Invitation)
            .options(selectinload(Invitation.groupe))
            .where(and_(
                Invitation.token == token,
                Invitation.utilise == False
            ))
        )
        invitation = result.scalar_one_or_none()

        return invitation.groupe if invitation else None
