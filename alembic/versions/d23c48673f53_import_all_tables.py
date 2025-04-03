"""import all tables

Revision ID: d23c48673f53
Revises: adde15311fc0
Create Date: 2025-04-03 16:06:40.925932

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd23c48673f53'
down_revision: Union[str, None] = 'adde15311fc0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
