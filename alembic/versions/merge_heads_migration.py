"""merge multiple heads

Revision ID: merge_heads_migration
Revises: reset_migrations, c7fd83cf7ae8
Create Date: 2025-04-03 12:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads_migration'
# Update this list with all head revisions found in your migrations folder
down_revision = None
# Update with the actual revision IDs for all heads
branch_labels = None
depends_on = ('reset_migrations', 'c7fd83cf7ae8')


def upgrade():
    # This is a merge migration that combines multiple heads
    # No actual schema changes needed
    pass


def downgrade():
    # No changes to revert
    pass
