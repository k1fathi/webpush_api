"""merge multiple heads

Revision ID: 2b3fede9e8f5_merge
Revises: merge_heads_migration, 2b3fede9e8f5, merge_heads_20250403_104246
Create Date: 2025-04-15 16:40:00.000000

"""

# revision identifiers, used by Alembic.
revision = '2b3fede9e8f5_merge'
down_revision = None
depends_on = None

# Branch identifiers for the branches being merged
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass