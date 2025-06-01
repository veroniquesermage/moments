import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import UserGroup
from app.models.user import User
from app.models.group import Group
from app.models.gift import Gift, GiftStatusEnum
from app.models.gift_delivery import GiftDelivery
from sqlalchemy import select


async def seed_data():

    async for db in get_db():

        print("Connexion BDD : OK")

        # --- Groupe existant : Famille Alpha (id=1) ---
        groupe_alpha_id = 1

        alpha_users_data = [
            ("Manon", "Blanc", "manon.blanc@example.com"),
            ("Julien", "Fontaine", "julien.fontaine@example.com"),
            ("Claire", "Fontaine", "claire.fontaine@example.com"),
            ("Aurore", "Lefevre", "aurore.lefevre@example.com")
        ]

        alpha_users = []
        for prenom, nom, email in alpha_users_data:
            user = User(name=f"{prenom} {nom}", email=email, google_id=email)
            db.add(user)
            await db.flush()
            db.add(UserGroup(utilisateur_id=user.id, groupe_id=groupe_alpha_id, role="MEMBRE"))
            alpha_users.append(user)

        # Cadeaux pour les utilisateurs d'Alpha
        for user in alpha_users:
            for i in range(2):
                cadeau = Gift(
                    nom=f"Cadeau {i+1} de {user.name}",
                    description="Un super cadeau de test",
                    destinataire_id=user.id,
                    priorite=i + 1,
                    statut=GiftStatusEnum.PRIS if i % 2 == 0 else GiftStatusEnum.RESERVE
                )
                db.add(cadeau)
                await db.flush()

                if cadeau.statut == GiftStatusEnum.PRIS:
                    db.add(GiftDelivery(gift_id=cadeau.id, recu=(i % 3 == 0)))

        # --- Nouveau groupe : Famille Bêta ---
        groupe_beta = Group()
        groupe_beta.nom_groupe = "Famille Bêta"
        groupe_beta.code = "BETA2023"
        db.add(groupe_beta)
        await db.flush()

        beta_users_data = [
            ("Léon", "Garcia", "leon.garcia@example.com"),
            ("Sophie", "Renaud", "sophie.renaud@example.com")
        ]

        for prenom, nom, email in beta_users_data:
            user = User(name=f"{prenom} {nom}", email=email, google_id=email)
            db.add(user)
            await db.flush()
            db.add(UserGroup(utilisateur_id=user.id, groupe_id=groupe_beta.id, role="MEMBRE"))

            for i in range(2):
                cadeau = Gift(
                    nom=f"Cadeau {i+1} de {user.name}",
                    description="Un petit cadeau bêta",
                    destinataire_id=user.id,
                    priorite=i + 1,
                    statut=GiftStatusEnum.DISPONIBLE
                )
                db.add(cadeau)

        await db.commit()
        print("Données de test injectées avec succès.")


if __name__ == "__main__":
    asyncio.run(seed_data())
