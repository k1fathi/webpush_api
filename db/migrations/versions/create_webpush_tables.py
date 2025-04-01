"""create webpush tables

Revision ID: create_webpush_tables
Revises: create_user_tables
Create Date: 2024-01-20 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'webpush',
        sa.Column('webpush_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id')),
        sa.Column('template_id', sa.Integer(), sa.ForeignKey('templates.template_id')),
        sa.Column('campaign_id', sa.Integer(), sa.ForeignKey('campaigns.campaign_id')),
        sa.Column('trigger_id', sa.Integer(), sa.ForeignKey('triggers.trigger_id')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('body', sa.String(1000), nullable=False),
        sa.Column('icon', sa.String(255)),
        sa.Column('image', sa.String(255)),
        sa.Column('deep_link', sa.String(255)),
        sa.Column('data', sa.JSON),
        sa.Column('status', sa.String(50)),
        sa.Column('sent_at', sa.DateTime),
        sa.Column('delivered_at', sa.DateTime),
        sa.Column('clicked_at', sa.DateTime),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.PrimaryKeyConstraint('webpush_id')
    )

def downgrade():
    op.drop_table('webpush')
