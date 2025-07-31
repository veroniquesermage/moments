"""ajout du détail achat pour un cadeau

Revision ID: e06196d589be
Revises: 5a7b035cfe9f
Create Date: 2025-07-29 20:50:34.689179

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e06196d589be'
down_revision: Union[str, None] = '5a7b035cfe9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema propre avec renommage."""

    # Renommer la table existante au lieu de la supprimer
    op.rename_table('gift_delivery', 'livraison_cadeau')

    # Créer la nouvelle table "details_achat_cadeau"
    op.create_table(
        'detail_achat_cadeau',
        sa.Column('gift_id', sa.Integer(), nullable=False),
        sa.Column('prix_reel', sa.Numeric(10, 2), nullable=True),
        sa.Column('commentaire', sa.String(), nullable=True),
        sa.Column('compte_tiers_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['gift_id'], ['cadeaux.id']),
        sa.ForeignKeyConstraint(['compte_tiers_id'], ['utilisateur.id']),
        sa.PrimaryKeyConstraint('gift_id')
    )
    op.create_index(op.f('ix_detail_achat_cadeau_gift_id'), 'detail_achat_cadeau', ['gift_id'], unique=False)

    # Copier les données de prix_reel dans la nouvelle table
    op.execute("""
               INSERT INTO details_achat_cadeau (gift_id, prix_reel)
               SELECT gift_id, prix_reel FROM livraison_cadeau WHERE prix_reel IS NOT NULL
               """)

    # Supprimer la colonne prix_reel de la table renommée
    op.drop_column('livraison_cadeau', 'prix_reel')



def downgrade() -> None:
    """Downgrade propre."""

    # Ajouter de nouveau la colonne dans livraison_cadeau
    op.add_column('livraison_cadeau', sa.Column('prix_reel', sa.Numeric(10, 2), nullable=True))

    # Restaurer les données depuis details_achat_cadeau
    op.execute("""
               UPDATE livraison_cadeau
               SET prix_reel = d.prix_reel
                   FROM details_achat_cadeau d
               WHERE livraison_cadeau.gift_id = d.gift_id
               """)

    # Supprimer la table details_achat_cadeau
    op.drop_index(op.f('ix_detail_achat_cadeau_gift_id'), table_name='detail_achat_cadeau')
    op.drop_table('detail_achat_cadeau')

    # Renommer la table dans l’autre sens
    op.rename_table('livraison_cadeau', 'gift_delivery')

