"""Add pagination indexes for gifts

Revision ID: 688930d9fdb4
Revises: bdc9498dbf29
Create Date: 2025-09-12 13:16:26.372562

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '688930d9fdb4'
down_revision: Union[str, None] = 'bdc9498dbf29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add composite index for gift pagination optimization."""
    op.create_index(
        'ix_cadeaux_destinataire_priorite',
        'cadeaux',
        ['destinataire_id', 'priorite'],
        unique=False
    )


def downgrade() -> None:
    """Remove composite index for gift pagination."""
    op.drop_index('ix_cadeaux_destinataire_priorite', 'cadeaux')
