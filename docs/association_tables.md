# Association Tables in SQLAlchemy

This document explains how we handle many-to-many relationships in our application using SQLAlchemy's association tables.

## Association Tables vs. Association Objects

SQLAlchemy offers two ways to handle many-to-many relationships:

1. **Association Tables**: Simple tables with foreign keys to both related tables
2. **Association Objects**: Full model classes with additional attributes beyond the relationship

## Our Approach

We've simplified our data model by using plain association tables for simple relationships:

### User-Role Relationship

```python
# Association table for user-role relationship
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

# In UserModel class:
roles = relationship("RoleModel", secondary=user_role)

# In RoleModel class:
users = relationship("UserModel", secondary="user_role")
```

### Role-Permission Relationship

```python
# Association table for role-permission relationship
role_permission = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_name', String, ForeignKey('permissions.name'), primary_key=True)
)

# In RoleModel class:
permissions = relationship("PermissionModel", secondary=role_permission)
```

## Removed Models

The following models have been removed as they were duplicating functionality:

- `UserRoleModel` - Replaced by the `user_role` association table
- `RolePermissionModel` - Replaced by the `role_permission` association table

## Database Changes

The Alembic migration `c49a5b6ee1f2_remove_duplicate_tables.py` removes the redundant tables:

- `user_roles` - Redundant to `user_role`
- `role_permissions` - Redundant to `role_permission`

## When to Use Association Objects

Use a full model class instead of a simple association table when you need:

1. Additional attributes beyond the foreign keys
2. Custom behavior for the relationship
3. Direct queries against the relationship

Otherwise, prefer the simpler association table approach.
