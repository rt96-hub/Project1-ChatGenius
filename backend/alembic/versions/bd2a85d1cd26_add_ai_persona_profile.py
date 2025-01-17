"""add_ai_persona_profile

Revision ID: bd2a85d1cd26
Revises: 2fc1ccb2bc1b
Create Date: 2025-01-17 12:15:03.597953

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd2a85d1cd26'
down_revision: Union[str, None] = '2fc1ccb2bc1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('channels', 'name',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_constraint('message_reactions_message_id_fkey', 'message_reactions', type_='foreignkey')
    op.drop_constraint('message_reactions_user_id_fkey', 'message_reactions', type_='foreignkey')
    op.drop_constraint('message_reactions_reaction_id_fkey', 'message_reactions', type_='foreignkey')
    op.create_foreign_key(None, 'message_reactions', 'messages', ['message_id'], ['id'])
    op.create_foreign_key(None, 'message_reactions', 'reactions', ['reaction_id'], ['id'])
    op.create_foreign_key(None, 'message_reactions', 'users', ['user_id'], ['id'])
    op.alter_column('messages', 'content',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.create_index(op.f('ix_messages_vector_id'), 'messages', ['vector_id'], unique=True)
    op.create_foreign_key(None, 'messages', 'messages', ['parent_id'], ['id'])
    op.alter_column('reactions', 'is_system',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
    op.add_column('users', sa.Column('ai_persona_profile', sa.Text(), nullable=True))
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               existing_server_default=sa.text('true'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'is_active',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
    op.drop_column('users', 'ai_persona_profile')
    op.alter_column('reactions', 'is_system',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               existing_server_default=sa.text('true'))
    op.drop_constraint(None, 'messages', type_='foreignkey')
    op.drop_index(op.f('ix_messages_vector_id'), table_name='messages')
    op.alter_column('messages', 'content',
               existing_type=sa.VARCHAR(),
               nullable=False)
    op.drop_constraint(None, 'message_reactions', type_='foreignkey')
    op.drop_constraint(None, 'message_reactions', type_='foreignkey')
    op.drop_constraint(None, 'message_reactions', type_='foreignkey')
    op.create_foreign_key('message_reactions_reaction_id_fkey', 'message_reactions', 'reactions', ['reaction_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('message_reactions_user_id_fkey', 'message_reactions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('message_reactions_message_id_fkey', 'message_reactions', 'messages', ['message_id'], ['id'], ondelete='CASCADE')
    op.alter_column('channels', 'name',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
