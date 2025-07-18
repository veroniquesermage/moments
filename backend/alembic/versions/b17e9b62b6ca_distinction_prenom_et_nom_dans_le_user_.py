"""Distinction prenom et nom dans le User , ajout d'une date de création et d'un surnom dans le UserGroup

Revision ID: b17e9b62b6ca
Revises: c778cb55b216
Create Date: 2025-06-13 16:24:03.596462

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b17e9b62b6ca'
down_revision: Union[str, None] = 'c778cb55b216'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('utilisateur', sa.Column('prenom', sa.String(length=255), nullable=True))
    op.add_column('utilisateur', sa.Column('nom', sa.String(length=255), nullable=True))
    op.add_column('utilisateur', sa.Column('date_creation', sa.DateTime(), nullable=True))
    op.add_column('utilisateur_groupe', sa.Column('surnom', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('utilisateur_groupe', 'surnom')
    op.drop_column('utilisateur', 'date_creation')
    op.drop_column('utilisateur', 'nom')
    op.drop_column('utilisateur', 'prenom')
    # ### end Alembic commands ###
