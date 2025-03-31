from alembic import op
import sqlalchemy as sa
from datetime import datetime

def upgrade():
    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), unique=True),
        sa.Column('description', sa.String(200)),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint('id')
    )

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), unique=True),
        sa.Column('description', sa.String(200)),
        sa.PrimaryKeyConstraint('id')
    )

    # Create role_permissions association table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), sa.ForeignKey('roles.id')),
        sa.Column('permission_id', sa.Integer(), sa.ForeignKey('permissions.id')),
    )

    # Create user activities table
    op.create_table(
        'user_activities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id')),
        sa.Column('action', sa.String(100)),
        sa.Column('module', sa.String(50)),
        sa.Column('timestamp', sa.DateTime(), default=datetime.utcnow),
        sa.Column('details', sa.String(500)),
        sa.Column('status', sa.String(20)),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('user_activities')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('roles')
