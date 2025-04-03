"""Reset migrations to ensure type consistency

Revision ID: reset_migrations
Revises: 
Create Date: 2025-04-03 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'reset_migrations'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # This migration is empty - it serves as a reset point with consistent types
    pass

def downgrade():
    # Nothing to revert
    pass
