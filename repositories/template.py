import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_session
from models.domain.template import TemplateModel, TemplateVersionModel
from models.template import Template
from models.schemas.template import TemplateStatus, TemplateType
from repositories.base import BaseRepository

class TemplateRepository(BaseRepository):
    """Repository for template operations"""
    
    async def create(self, template: Template) -> Template:
        """Create a new template"""
        async with get_session() as session:
            # Create the template model
            db_template = TemplateModel(
                id=str(uuid.uuid4()) if not template.id else template.id,
                name=template.name,
                description=template.description,
                title=template.title,
                body=template.body,
                image_url=template.image_url,
                action_url=template.action_url,
                icon_url=template.icon_url,
                template_type=template.template_type,
                content=template.content,
                variables=template.variables,
                tags=template.tags,
                status=template.status,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=template.created_by,
                version=1,
                category=template.category
            )
            session.add(db_template)
            
            # Also create the first version
            db_version = TemplateVersionModel(
                id=str(uuid.uuid4()),
                template_id=db_template.id,
                version=1,
                title=template.title,
                body=template.body,
                image_url=template.image_url,
                action_url=template.action_url,
                icon_url=template.icon_url,
                content=template.content,
                created_at=datetime.now(),
                created_by=template.created_by
            )
            session.add(db_version)
            
            await session.commit()
            await session.refresh(db_template)
            return Template.from_orm(db_template)
    
    async def get(self, template_id: str) -> Optional[Template]:
        """Get a template by ID"""
        async with get_session() as session:
            result = await session.execute(
                select(TemplateModel).where(TemplateModel.id == template_id)
            )
            db_template = result.scalars().first()
            return Template.from_orm(db_template) if db_template else None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[TemplateStatus] = None,
        type_filter: Optional[TemplateType] = None,
        tag: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Template]:
        """Get all templates with pagination and filtering"""
        async with get_session() as session:
            query = select(TemplateModel)
            
            # Apply filters
            if status:
                query = query.where(TemplateModel.status == status)
                
            if type_filter:
                query = query.where(TemplateModel.template_type == type_filter)
                
            if tag:
                query = query.where(TemplateModel.tags.contains([tag]))
                
            if category:
                query = query.where(TemplateModel.category == category)
            
            # Apply pagination and ordering
            query = query.order_by(desc(TemplateModel.updated_at)).offset(skip).limit(limit)
            
            result = await session.execute(query)
            db_templates = result.scalars().all()
            return [Template.from_orm(db_template) for db_template in db_templates]
    
    async def update(self, template_id: str, template: Template, create_version: bool = True) -> Template:
        """Update a template"""
        async with get_session() as session:
            result = await session.execute(
                select(TemplateModel).where(TemplateModel.id == template_id)
            )
            db_template = result.scalars().first()
            if not db_template:
                raise ValueError(f"Template with ID {template_id} not found")
                
            # Get current version before updating
            current_version = db_template.version
            
            # Update fields
            db_template.name = template.name
            db_template.description = template.description
            db_template.title = template.title
            db_template.body = template.body
            db_template.image_url = template.image_url
            db_template.action_url = template.action_url
            db_template.icon_url = template.icon_url
            db_template.template_type = template.template_type
            db_template.content = template.content
            db_template.variables = template.variables
            db_template.tags = template.tags
            db_template.status = template.status
            db_template.updated_at = datetime.now()
            db_template.category = template.category
            
            # Create a new version if needed
            if create_version:
                # Increment version number
                db_template.version = current_version + 1
                
                # Create a new version entry
                db_version = TemplateVersionModel(
                    id=str(uuid.uuid4()),
                    template_id=template_id,
                    version=current_version + 1,
                    title=template.title,
                    body=template.body,
                    image_url=template.image_url,
                    action_url=template.action_url,
                    icon_url=template.icon_url,
                    content=template.content,
                    created_at=datetime.now(),
                    created_by=template.created_by
                )
                session.add(db_version)
                
            await session.commit()
            await session.refresh(db_template)
            return Template.from_orm(db_template)
    
    async def delete(self, template_id: str) -> bool:
        """Delete a template"""
        async with get_session() as session:
            # Check if template exists
            result = await session.execute(
                select(TemplateModel).where(TemplateModel.id == template_id)
            )
            db_template = result.scalars().first()
            if not db_template:
                return False
                
            # Delete versions first
            await session.execute(
                select(TemplateVersionModel).where(TemplateVersionModel.template_id == template_id)
            )
            versions = await session.execute(
                select(TemplateVersionModel).where(TemplateVersionModel.template_id == template_id)
            )
            for version in versions.scalars().all():
                await session.delete(version)
                
            # Then delete the template
            await session.delete(db_template)
            await session.commit()
            return True
    
    async def get_versions(self, template_id: str) -> List[Dict]:
        """Get all versions of a template"""
        async with get_session() as session:
            result = await session.execute(
                select(TemplateVersionModel)
                .where(TemplateVersionModel.template_id == template_id)
                .order_by(desc(TemplateVersionModel.version))
            )
            versions = result.scalars().all()
            return [{
                "id": str(v.id),
                "template_id": str(v.template_id),
                "version": v.version,
                "title": v.title,
                "body": v.body,
                "image_url": v.image_url,
                "action_url": v.action_url,
                "icon_url": v.icon_url,
                "content": v.content,
                "created_at": v.created_at,
                "created_by": str(v.created_by) if v.created_by else None
            } for v in versions]
    
    async def get_version(self, template_id: str, version: int) -> Optional[Dict]:
        """Get a specific version of a template"""
        async with get_session() as session:
            result = await session.execute(
                select(TemplateVersionModel)
                .where(
                    and_(
                        TemplateVersionModel.template_id == template_id,
                        TemplateVersionModel.version == version
                    )
                )
            )
            v = result.scalars().first()
            if not v:
                return None
                
            return {
                "id": str(v.id),
                "template_id": str(v.template_id),
                "version": v.version,
                "title": v.title,
                "body": v.body,
                "image_url": v.image_url,
                "action_url": v.action_url,
                "icon_url": v.icon_url,
                "content": v.content,
                "created_at": v.created_at,
                "created_by": str(v.created_by) if v.created_by else None
            }
    
    async def restore_version(self, template_id: str, version: int) -> Optional[Template]:
        """Restore a template to a specific version"""
        # Get the specified version
        version_data = await self.get_version(template_id, version)
        if not version_data:
            return None
            
        # Get the current template
        template = await self.get(template_id)
        if not template:
            return None
            
        # Update template with version data
        template.title = version_data["title"]
        template.body = version_data["body"]
        template.image_url = version_data["image_url"]
        template.action_url = version_data["action_url"]
        template.icon_url = version_data["icon_url"]
        template.content = version_data["content"]
        
        # Save the updated template and create a new version
        updated = await self.update(template_id, template, create_version=True)
        return updated
    
    async def update_status(self, template_id: str, status: TemplateStatus) -> Optional[Template]:
        """Update template status"""
        async with get_session() as session:
            result = await session.execute(
                select(TemplateModel).where(TemplateModel.id == template_id)
            )
            db_template = result.scalars().first()
            if not db_template:
                return None
                
            db_template.status = status
            db_template.updated_at = datetime.now()
            
            await session.commit()
            await session.refresh(db_template)
            return Template.from_orm(db_template)
    
    async def count_templates(
        self, 
        status: Optional[TemplateStatus] = None,
        type_filter: Optional[TemplateType] = None
    ) -> int:
        """Count templates with optional filters"""
        async with get_session() as session:
            query = select(func.count(TemplateModel.id))
            
            if status:
                query = query.where(TemplateModel.status == status)
                
            if type_filter:
                query = query.where(TemplateModel.template_type == type_filter)
                
            result = await session.execute(query)
            return result.scalar() or 0
    
    async def search(self, query: str, limit: int = 10) -> List[Template]:
        """Search templates by name or content"""
        search_term = f"%{query}%"
        
        async with get_session() as session:
            result = await session.execute(
                select(TemplateModel)
                .where(
                    or_(
                        TemplateModel.name.ilike(search_term),
                        TemplateModel.description.ilike(search_term),
                        TemplateModel.title.ilike(search_term),
                        TemplateModel.body.ilike(search_term)
                    )
                )
                .limit(limit)
            )
            db_templates = result.scalars().all()
            return [Template.from_orm(t) for t in db_templates]
