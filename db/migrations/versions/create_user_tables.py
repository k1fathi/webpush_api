"""create user tables

Revision ID: 001_create_user_tables
Revises: 
Create Date: 2024-01-20 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('birthday', sa.Date()),
        sa.Column('membership_date', sa.Date()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )

    # Create association tables
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id')),
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id'))
    )

    op.create_table(
        'user_segments',
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.user_id')),
        sa.Column('segment_id', sa.Integer(), sa.ForeignKey('segments.segment_id'))
    )

def downgrade():
    op.drop_table('user_segments')
    op.drop_table('user_roles')
    op.drop_table('users')
