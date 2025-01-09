"""add_message_reply_functionality

Revision ID: 0d9f41b3acc9
Revises: 5cb6ee688f15
Create Date: 2025-01-09 15:22:14.590321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0d9f41b3acc9'
down_revision: Union[str, None] = '5cb6ee688f15'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add parent_id column
    op.add_column('messages',
        sa.Column('parent_id', sa.Integer(), nullable=True)
    )
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_message_parent',
        'messages', 'messages',
        ['parent_id'], ['id']
    )
    
    # Add unique constraint on parent_id
    op.create_unique_constraint(
        'unique_message_parent',
        'messages',
        ['parent_id']
    )


def downgrade() -> None:
    # Remove unique constraint
    op.drop_constraint(
        'unique_message_parent',
        'messages',
        type_='unique'
    )
    
    # Remove foreign key constraint
    op.drop_constraint(
        'fk_message_parent',
        'messages',
        type_='foreignkey'
    )
    
    # Remove parent_id column
    op.drop_column('messages', 'parent_id')
