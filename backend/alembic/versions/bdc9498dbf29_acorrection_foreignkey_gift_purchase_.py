"""ajout du détail achat pour un cadeau

Revision ID: bdc9498dbf29
Revises: e06196d589be
Create Date: 2025-07-29 21:14:32.693433

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'bdc9498dbf29'
down_revision: Union[str, None] = 'e06196d589be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Drop la mauvaise FK
    op.drop_constraint('detail_achat_cadeau_compte_tiers_id_fkey', 'detail_achat_cadeau', type_='foreignkey')

    # Recrée la bonne
    op.create_foreign_key(
        constraint_name='detail_achat_cadeau_compte_tiers_id_fkey',
        source_table='detail_achat_cadeau',
        referent_table='utilisateur',
        local_cols=['compte_tiers_id'],
        remote_cols=['id']
    )


def downgrade():
    # Inverser proprement (remet la FK cassée vers user)
    op.drop_constraint('detail_achat_cadeau_compte_tiers_id_fkey', 'detail_achat_cadeau', type_='foreignkey')

    op.create_foreign_key(
        constraint_name='detail_achat_cadeau_compte_tiers_id_fkey',
        source_table='detail_achat_cadeau',
        referent_table='user',
        local_cols=['compte_tiers_id'],
        remote_cols=['id']
    )
