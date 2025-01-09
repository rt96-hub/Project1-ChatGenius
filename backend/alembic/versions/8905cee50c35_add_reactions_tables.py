"""add_reactions_tables

Revision ID: 8905cee50c35
Revises: 4c94994e2d45
Create Date: 2025-01-08 20:36:34.594989

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8905cee50c35'
down_revision: Union[str, None] = '4c94994e2d45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create reactions table
    op.create_table('reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('is_system', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('image_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_reactions_id'), 'reactions', ['id'], unique=False)

    # Create message_reactions table
    op.create_table('message_reactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('reaction_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reaction_id'], ['reactions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'reaction_id', 'user_id', name='unique_message_reaction_user')
    )
    op.create_index(op.f('ix_message_reactions_id'), 'message_reactions', ['id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_message_reactions_id'), table_name='message_reactions')
    op.drop_table('message_reactions')
    op.drop_index(op.f('ix_reactions_id'), table_name='reactions')
    op.drop_table('reactions')
