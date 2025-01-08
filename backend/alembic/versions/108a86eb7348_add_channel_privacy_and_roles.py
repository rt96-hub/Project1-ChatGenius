"""add_channel_privacy_and_roles

Revision ID: 108a86eb7348
Revises: b37feb6aa2c7
Create Date: 2025-01-08 12:28:16.805348

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '108a86eb7348'
down_revision: Union[str, None] = 'b37feb6aa2c7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to channels table if they don't exist
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    columns = [col['name'] for col in inspector.get_columns('channels')]
    
    if 'is_private' not in columns:
        op.add_column('channels', sa.Column('is_private', sa.Boolean(), nullable=True))
        # Set default value for is_private
        op.execute("UPDATE channels SET is_private = FALSE WHERE is_private IS NULL")
        op.alter_column('channels', 'is_private',
                        existing_type=sa.Boolean(),
                        nullable=False,
                        server_default=sa.text('false'))
    
    if 'join_code' not in columns:
        op.add_column('channels', sa.Column('join_code', sa.String(), nullable=True))

    # Create channel_roles table if it doesn't exist
    tables = inspector.get_table_names()
    if 'channel_roles' not in tables:
        op.create_table('channel_roles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('channel_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('role', sa.String(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_channel_roles_id'), 'channel_roles', ['id'], unique=False)


def downgrade() -> None:
    # Drop channel_roles table if it exists
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    tables = inspector.get_table_names()
    
    if 'channel_roles' in tables:
        op.drop_index(op.f('ix_channel_roles_id'), table_name='channel_roles')
        op.drop_table('channel_roles')
    
    # Drop columns from channels table if they exist
    columns = [col['name'] for col in inspector.get_columns('channels')]
    
    if 'join_code' in columns:
        op.drop_column('channels', 'join_code')
    if 'is_private' in columns:
        op.drop_column('channels', 'is_private')
