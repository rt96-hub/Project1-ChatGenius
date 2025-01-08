"""add updated_at to messages

Revision ID: b37feb6aa2c7
Revises: 7807d3ae38e0
Create Date: 2025-01-07 19:28:48.878346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b37feb6aa2c7'
down_revision: Union[str, None] = '7807d3ae38e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('messages', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'updated_at')
    # ### end Alembic commands ###
