"""chat_replies

Revision ID: 9fc612a29cc9
Revises: 9681c6226e07
Create Date: 2025-01-10 14:06:00.423444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fc612a29cc9'
down_revision: Union[str, None] = '9681c6226e07'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('channels', 'is_dm',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('false'))
    op.add_column('messages', sa.Column('parent_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('unique_reply_message', 'messages', ['parent_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('unique_reply_message', 'messages', type_='unique')
    op.drop_column('messages', 'parent_id')
    op.alter_column('channels', 'is_dm',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('false'))
    # ### end Alembic commands ###
