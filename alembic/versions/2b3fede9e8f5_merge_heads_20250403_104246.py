"""merge_heads_20250403_104246

Revision ID: 2b3fede9e8f5
Revises: clear_migrations, merge_heads_migration
Create Date: 2025-04-03 10:42:51.219395

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b3fede9e8f5'
down_revision: Union[str, None] = ('clear_migrations', 'merge_heads_migration')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
