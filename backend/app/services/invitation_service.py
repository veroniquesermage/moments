from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Invitation, User, UserGroup
from app.schemas.invitation import InvitationResponse


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