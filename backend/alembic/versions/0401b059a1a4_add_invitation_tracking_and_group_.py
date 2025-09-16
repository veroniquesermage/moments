"""Add invitation tracking and group refresh date

Revision ID: 0401b059a1a4
Revises: 688930d9fdb4
Create Date: 2025-09-15 19:55:22.237040

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0401b059a1a4'
down_revision: Union[str, None] = '688930d9fdb4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create invitation table
    op.create_table('invitation',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('groupe_id', sa.Integer(), nullable=False),
    sa.Column('envoye_par_id', sa.Integer(), nullable=False),
    sa.Column('date_envoi', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['envoye_par_id'], ['utilisateur.id'], ),
    sa.ForeignKeyConstraint(['groupe_id'], ['groupe.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_invitation_id'), 'invitation', ['id'], unique=False)

    # Add refresh date column to groupe
    op.add_column('groupe', sa.Column('date_refresh_code', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove refresh date column
    op.drop_column('groupe', 'date_refresh_code')

    # Drop invitation table
    op.drop_index(op.f('ix_invitation_id'), table_name='invitation')
    op.drop_table('invitation')