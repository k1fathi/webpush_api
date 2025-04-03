"""Add campaign_templates table

Revision ID: add_campaign_templates
Revises: <previous_revision_id>
Create Date: 2023-10-01 12:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_campaign_templates'
down_revision = '<previous_revision_id>'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'campaign_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('category', sa.Enum('promotional', 'transactional', 'informational', 'reminder', 'survey', name='templatecategory'), nullable=False, server_default='informational'),
        sa.Column('status', sa.Enum('draft', 'active', 'archived', 'deprecated', name='templatestatus'), nullable=False, server_default='draft'),
        sa.Column('content', sa.JSON, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True)
    )

def downgrade():
    op.drop_table('campaign_templates')
