"""Add is_admin to users

Revision ID: 002
Revises: add_service_token_fields
Create Date: 2026-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = 'add_service_token_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_admin column
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=False, server_default='false'))


def downgrade() -> None:
    # Remove column
    op.drop_column('users', 'is_admin')
