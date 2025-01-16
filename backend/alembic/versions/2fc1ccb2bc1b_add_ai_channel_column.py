"""add_ai_channel_column

Revision ID: 2fc1ccb2bc1b
Revises: e7b62f89908f
Create Date: 2025-01-16 15:44:54.343354

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2fc1ccb2bc1b'
down_revision: Union[str, None] = 'e7b62f89908f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('channels', sa.Column('ai_channel', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('channels', 'ai_channel')
    # ### end Alembic commands ###
