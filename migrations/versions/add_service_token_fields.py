"""Add service token fields

Revision ID: add_service_token_fields
Revises: initial_migration
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_service_token_fields'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to tokens table
    op.add_column('tokens', sa.Column('token_type', sa.String(), nullable=False, server_default='refresh'))
    op.add_column('tokens', sa.Column('scope', sa.String(), nullable=True))
    op.add_column('tokens', sa.Column('last_used_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove the columns
    op.drop_column('tokens', 'last_used_at')
    op.drop_column('tokens', 'scope')
    op.drop_column('tokens', 'token_type') 