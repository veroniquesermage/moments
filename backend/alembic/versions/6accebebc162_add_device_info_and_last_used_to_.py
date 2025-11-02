"""add_device_info_and_last_used_to_refresh_tokens

Revision ID: 6accebebc162
Revises: 8f17f8398062
Create Date: 2025-11-02 10:05:46.312965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6accebebc162'
down_revision: Union[str, None] = '8f17f8398062'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Ajouter device_info (optionnel)
    op.add_column('refresh_tokens', sa.Column('device_info', sa.String(length=255), nullable=True))

    # Ajouter last_used_at avec valeur par défaut = created_at pour les tokens existants
    op.add_column('refresh_tokens', sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True))

    # Mettre à jour les tokens existants : last_used_at = created_at
    op.execute("""
        UPDATE refresh_tokens
        SET last_used_at = created_at
        WHERE last_used_at IS NULL
    """)

    # Rendre last_used_at non-nullable maintenant qu'il est rempli
    op.alter_column('refresh_tokens', 'last_used_at', nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('refresh_tokens', 'last_used_at')
    op.drop_column('refresh_tokens', 'device_info')
