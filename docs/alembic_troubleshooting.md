# Alembic Troubleshooting Guide

## Common Issues and Solutions

### Foreign Key Reference Errors

#### Issue: NoReferencedTableError
Error message like: `sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 'analytics.notification_id' could not find table 'notifications'`

**Solution:**
1. Ensure all model files are properly imported in the correct order
2. Use the `db/models_helper.py` module to ensure models are loaded in the right order
3. Update `alembic/env.py` to use the helper module:
   ```python
   from db.models_helper import load_all_models
   load_all_models()
   ```

4. If you're creating models with circular dependencies, use string references:
   ```python
   # Instead of direct references:
   from models.other import OtherModel
   relationship(OtherModel)
   
   # Use string references:
   relationship("OtherModel")
   ```

### Missing Tables or Schema Issues

#### Issue: Table doesn't exist after migration

**Solution:**
1. Make sure your models are properly imported in `alembic/env.py`
2. Verify that all models inherit from the same `Base` class
3. Run a clean migration with this sequence:
   ```bash
   # Create a new migration
   alembic revision --autogenerate -m "recreate_schema"
   
   # Apply the migration
   alembic upgrade head
   ```

### Circular Dependencies

#### Issue: ImportError due to circular imports

**Solution:**
1. Use string references in relationships:
   ```python
   relationship("OtherModel", back_populates="relationship_name")
   ```
2. Split your models into separate files
3. Use the `models_helper.py` module to control import order

### Manual Fix for Migration Versions

If you need to manually fix migration issues, you can:

1. Reset the database (drop all tables)
2. Delete all migration versions
3. Create a fresh initial migration:
   ```bash
   alembic revision --autogenerate -m "initial_setup"
   alembic upgrade head
   ```

## Recommended Migration Workflow

1. Make sure all models are properly defined and imported
2. Use string references for relationships between models
3. Run `from db.models_helper import load_all_models; load_all_models()` before creating migrations
4. Generate and apply migrations:
   ```bash
   alembic revision --autogenerate -m "descriptive_message"
   alembic upgrade head
   ```
