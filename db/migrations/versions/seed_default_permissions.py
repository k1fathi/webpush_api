"""seed default permissions

Revision ID: seed_default_perms
Revises: create_role_tables
Create Date: 2024-01-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from db.seeders.role_permission_seeder import seed_role_permissions
from sqlalchemy.orm import Session

# revision identifiers, used by Alembic
revision = 'seed_default_perms'
down_revision = 'create_role_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        seed_role_permissions(session)
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def downgrade() -> None:
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Delete all role permissions
        session.execute('DELETE FROM role_permissions')
        # Delete all permissions
        session.execute('DELETE FROM permissions')
        # Delete all roles
        session.execute('DELETE FROM roles')
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
