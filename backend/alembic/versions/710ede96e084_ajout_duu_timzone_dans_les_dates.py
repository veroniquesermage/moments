"""Ajout duu timzone dans les dates

Revision ID: 710ede96e084
Revises: bd13892a05a6
Create Date: 2025-06-16 21:56:58.324396

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '710ede96e084'
down_revision: Union[str, None] = 'bd13892a05a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('cadeaux', 'date_reservation',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    op.alter_column('utilisateur', 'date_creation',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=True)
    op.alter_column('utilisateur_groupe', 'date_ajout',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('utilisateur_groupe', 'date_ajout',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    op.alter_column('utilisateur', 'date_creation',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=False)
    op.alter_column('cadeaux', 'date_reservation',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               existing_nullable=True)
    # ### end Alembic commands ###
