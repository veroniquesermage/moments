"""ACorrection id trace

Revision ID: a5998b339419
Revises: 73c0c96bbc51
Create Date: 2025-06-28 17:35:09.795109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID



# revision identifiers, used by Alembic.
revision: str = 'a5998b339419'
down_revision: Union[str, None] = '73c0c96bbc51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column('traces', 'id')
    op.add_column('traces', sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True))


def downgrade():
    op.drop_column('traces', 'id')
    op.add_column('traces', sa.Column('id', UUID(), primary_key=True))
