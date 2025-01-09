"""add_dm_support

Revision ID: 5cb6ee688f15
Revises: 8905cee50c35
Create Date: 2025-01-09 10:15:04.710257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5cb6ee688f15'
down_revision: Union[str, None] = '8905cee50c35'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add is_dm column
    op.add_column('channels', sa.Column('is_dm', sa.Boolean(), nullable=True))
    
    # Set default value for is_dm
    op.execute("UPDATE channels SET is_dm = FALSE WHERE is_dm IS NULL")
    op.alter_column('channels', 'is_dm',
                    existing_type=sa.Boolean(),
                    nullable=False,
                    server_default=sa.text('false'))
    
    # Add constraint to ensure DMs are always private
    op.create_check_constraint(
        'dm_must_be_private',
        'channels',
        'NOT is_dm OR (is_dm AND is_private)'
    )


def downgrade() -> None:
    # Remove constraint first
    op.drop_constraint('dm_must_be_private', 'channels', type_='check')
    
    # Remove is_dm column
    op.drop_column('channels', 'is_dm')
