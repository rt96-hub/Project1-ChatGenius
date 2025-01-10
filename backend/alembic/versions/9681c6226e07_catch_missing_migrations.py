"""catch_missing_migrations

Revision ID: 9681c6226e07
Revises: initial_migration
Create Date: 2025-01-10 02:05:10.496429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9681c6226e07'
down_revision: Union[str, None] = 'initial_migration'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_active column to users table
    op.add_column('users', sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False))
    
    # Make email nullable (it was non-nullable in initial migration)
    op.alter_column('users', 'email',
               existing_type=sa.String(),
               nullable=True)
    
    # Create user_channels table
    op.create_table('user_channels',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'channel_id')
    )
    
    # Add index to channels.name (was missing in initial migration)
    op.create_index(op.f('ix_channels_name'), 'channels', ['name'], unique=False)
    
    # Make channels.is_private nullable with default false
    op.alter_column('channels', 'is_private',
               existing_type=sa.BOOLEAN(),
               nullable=True,
               server_default=sa.text('false'))


def downgrade() -> None:
    # Revert all changes in reverse order
    op.alter_column('channels', 'is_private',
               existing_type=sa.BOOLEAN(),
               nullable=False,
               server_default=sa.text('false'))
               
    op.drop_index(op.f('ix_channels_name'), table_name='channels')
    
    op.drop_table('user_channels')
    
    op.alter_column('users', 'email',
               existing_type=sa.String(),
               nullable=False)
               
    op.drop_column('users', 'is_active')
