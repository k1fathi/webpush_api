import logging
import uuid
import re
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from core.config import settings
from models.schemas.template import Template
from models.schemas.template import TemplateStatus, TemplateType, TemplateValidation
from repositories.template import TemplateRepository
from repositories.campaign import CampaignRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class TemplateService:
    """Service for template management according to template_creation_flow.mmd"""
    
    def __init__(self):
        self.template_repo = TemplateRepository()
        self.campaign_repo = CampaignRepository()
    
    async def create_template(self, template_data: Dict, user_id: str = None) -> Template:
        """
        Create a new template
        
        Args:
            template_data: Template data
            user_id: ID of the user creating the template
            
        Returns:
            Template: The created template
        """
        # Extract variables from content if not provided
        if "variables" not in template_data or not template_data["variables"]:
            variables = self._extract_variables_from_content(template_data)
            template_data["variables"] = variables
        
        # Create the template
        template = Template(
            id=str(uuid.uuid4()),
            created_by=user_id,
            status=TemplateStatus.DRAFT,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **template_data
        )
        
        # Save to repository
        created_template = await self.template_repo.create(template)
        
        # Log the creation
        audit_log(
            message=f"Created template {created_template.name}",
            user_id=user_id,
            action_type="create_template",
            resource_type="template",
            resource_id=created_template.id
        )
        
        return created_template
    
    def _extract_variables_from_content(self, template_data: Dict) -> List[str]:
        """Extract variables from template content"""
        variables = set()
        
        # Check title
        if "title" in template_data:
            title_vars = re.findall(r'\{([a-zA-Z0-9_]+)\}', template_data["title"])
            variables.update(title_vars)
            
        # Check body
        if "body" in template_data:
            body_vars = re.findall(r'\{([a-zA-Z0-9_]+)\}', template_data["body"])
            variables.update(body_vars)
            
        # Check content dictionary if present
        if "content" in template_data and isinstance(template_data["content"], dict):
            content_str = str(template_data["content"])
            content_vars = re.findall(r'\{([a-zA-Z0-9_]+)\}', content_str)
            variables.update(content_vars)
            
        return list(variables)
    
    async def get_template(self, template_id: str) -> Optional[Template]:
        """
        Get a template by ID
        
        Args:
            template_id: The template ID
            
        Returns:
            Optional[Template]: The template if found
        """
        return await self.template_repo.get(template_id)
    
    async def update_template(
        self, 
        template_id: str, 
        template_data: Dict, 
        user_id: str = None,
        create_version: bool = True
    ) -> Template:
        """
        Update a template
        
        Args:
            template_id: The template ID
            template_data: Updated template data
            user_id: ID of the user updating the template
            create_version: Whether to create a new version
            
        Returns:
            Template: The updated template
        """
        # Get the existing template
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        # Check if template can be updated
        if template.status not in [TemplateStatus.DRAFT, TemplateStatus.REJECTED, TemplateStatus.ACTIVE]:
            raise ValueError(f"Template in {template.status} status cannot be updated")
            
        # Update template fields
        for key, value in template_data.items():
            if hasattr(template, key):
                setattr(template, key, value)
                
        # Re-extract variables if content has changed
        if "title" in template_data or "body" in template_data or "content" in template_data:
            extracted_vars = self._extract_variables_from_content({
                "title": template.title,
                "body": template.body,
                "content": template.content
            })
            if "variables" not in template_data:
                template.variables = extracted_vars
                
        # Reset status to DRAFT if content was changed
        content_fields = ["title", "body", "image_url", "action_url", "icon_url", "content"]
        if any(field in template_data for field in content_fields):
            if template.status == TemplateStatus.ACTIVE:
                # Active templates remain active until explicitly changed
                pass
            else:
                template.status = TemplateStatus.DRAFT
        
        # Update timestamp and user
        template.updated_at = datetime.now()
        if user_id:
            template.created_by = user_id  # This is used for the version
            
        # Save to repository
        updated_template = await self.template_repo.update(
            template_id, 
            template,
            create_version=create_version
        )
        
        # Log the update
        audit_log(
            message=f"Updated template {updated_template.name}",
            user_id=user_id,
            action_type="update_template",
            resource_type="template",
            resource_id=template_id
        )
        
        return updated_template
    
    async def delete_template(self, template_id: str, user_id: str = None) -> bool:
        """
        Delete a template
        
        Args:
            template_id: The template ID
            user_id: ID of the user deleting the template
            
        Returns:
            bool: True if deleted, False otherwise
        """
        # Check if template is used by any campaigns
        campaigns = await self.campaign_repo.get_by_template(template_id)
        if campaigns:
            raise ValueError(f"Cannot delete template: it is used by {len(campaigns)} campaigns")
            
        # Delete the template
        result = await self.template_repo.delete(template_id)
        
        # Log the deletion
        if result:
            audit_log(
                message=f"Deleted template {template_id}",
                user_id=user_id,
                action_type="delete_template",
                resource_type="template",
                resource_id=template_id
            )
            
        return result
    
    async def get_all_templates(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[TemplateStatus] = None,
        template_type: Optional[TemplateType] = None,
        tag: Optional[str] = None,
        category: Optional[str] = None
    ) -> tuple[List[Template], int]:
        """
        Get all templates with pagination and filtering
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            status: Filter by status
            template_type: Filter by template type
            tag: Filter by tag
            category: Filter by category
            
        Returns:
            Tuple[List[Template], int]: List of templates and total count
        """
        templates = await self.template_repo.get_all(
            skip=skip, 
            limit=limit, 
            status=status, 
            type_filter=template_type,
            tag=tag,
            category=category
        )
        total = await self.template_repo.count_templates(status, template_type)
        return templates, total
    
    async def validate_template(self, template_data: Dict) -> TemplateValidation:
        """
        Validate a template
        
        Args:
            template_data: Template data to validate
            
        Returns:
            TemplateValidation: Validation result
        """
        errors = []
        warnings = []
        
        # Required fields
        if not template_data.get("name"):
            errors.append("Template name is required")
            
        if not template_data.get("title"):
            errors.append("Template title is required")
            
        if not template_data.get("body"):
            errors.append("Template body is required")
            
        # Length constraints
        if "title" in template_data and len(template_data["title"]) > 50:
            warnings.append("Title exceeds recommended length of 50 characters")
            
        if "body" in template_data and len(template_data["body"]) > 500:
            warnings.append("Body exceeds recommended length of 500 characters")
            
        # Check for invalid variables
        variables = self._extract_variables_from_content(template_data)
        for var in variables:
            if not re.match(r'^[a-zA-Z0-9_]+$', var):
                errors.append(f"Invalid variable name: {var}")
                
        # Check URL validity (already handled by Pydantic for image_url and action_url)
        
        return TemplateValidation(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    async def render_template(self, template_id: str, data: Dict[str, Any] = None) -> Dict:
        """
        Render a template with provided data
        
        Args:
            template_id: The template ID
            data: Dictionary with variables for rendering
            
        Returns:
            Dict: Rendered template
        """
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        data = data or {}
        
        # Render title and body
        title = template.title
        body = template.body
        
        for var_name, var_value in data.items():
            placeholder = "{" + var_name + "}"
            title = title.replace(placeholder, str(var_value))
            body = body.replace(placeholder, str(var_value))
            
        # Result dictionary
        result = {
            "title": title,
            "body": body,
            "image_url": template.image_url,
            "action_url": template.action_url,
            "icon_url": template.icon_url,
            "rendered_content": template.content.copy() if template.content else {}
        }
        
        return result
    
    async def submit_for_approval(self, template_id: str, user_id: str = None) -> Template:
        """
        Submit a template for approval
        
        Args:
            template_id: The template ID
            user_id: ID of the user submitting the template
            
        Returns:
            Template: The updated template
        """
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        if template.status != TemplateStatus.DRAFT:
            raise ValueError(f"Only draft templates can be submitted for approval")
            
        # Validate the template before submission
        validation = await self.validate_template({
            "name": template.name,
            "title": template.title,
            "body": template.body,
            "content": template.content
        })
        
        if not validation.is_valid:
            raise ValueError(f"Template validation failed: {validation.errors}")
            
        # Update status
        template = await self.template_repo.update_status(template_id, TemplateStatus.PENDING_APPROVAL)
        
        # Log the submission
        audit_log(
            message=f"Submitted template {template.name} for approval",
            user_id=user_id,
            action_type="submit_template",
            resource_type="template",
            resource_id=template_id
        )
        
        return template
    
    async def approve_template(self, template_id: str, user_id: str = None) -> Template:
        """
        Approve a template
        
        Args:
            template_id: The template ID
            user_id: ID of the user approving the template
            
        Returns:
            Template: The updated template
        """
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        if template.status != TemplateStatus.PENDING_APPROVAL:
            raise ValueError(f"Only pending templates can be approved")
            
        # Update status
        template = await self.template_repo.update_status(template_id, TemplateStatus.ACTIVE)
        
        # Log the approval
        audit_log(
            message=f"Approved template {template.name}",
            user_id=user_id,
            action_type="approve_template",
            resource_type="template",
            resource_id=template_id
        )
        
        return template
    
    async def reject_template(
        self, 
        template_id: str, 
        reason: str = None,
        user_id: str = None
    ) -> Template:
        """
        Reject a template
        
        Args:
            template_id: The template ID
            reason: Reason for rejection
            user_id: ID of the user rejecting the template
            
        Returns:
            Template: The updated template
        """
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        if template.status != TemplateStatus.PENDING_APPROVAL:
            raise ValueError(f"Only pending templates can be rejected")
            
        # Update status
        template = await self.template_repo.update_status(template_id, TemplateStatus.REJECTED)
        
        # Add rejection reason to content metadata
        if reason:
            content = template.content or {}
            content["rejection_reason"] = reason
            content["rejected_at"] = datetime.now().isoformat()
            content["rejected_by"] = user_id
            
            # Update the template content
            template.content = content
            template = await self.template_repo.update(template_id, template, create_version=False)
        
        # Log the rejection
        audit_log(
            message=f"Rejected template {template.name}" + (f": {reason}" if reason else ""),
            user_id=user_id,
            action_type="reject_template",
            resource_type="template",
            resource_id=template_id,
            metadata={"reason": reason} if reason else None
        )
        
        return template
    
    async def archive_template(self, template_id: str, user_id: str = None) -> Template:
        """
        Archive a template
        
        Args:
            template_id: The template ID
            user_id: ID of the user archiving the template
            
        Returns:
            Template: The updated template
        """
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        # Update status
        template = await self.template_repo.update_status(template_id, TemplateStatus.ARCHIVED)
        
        # Log the archive
        audit_log(
            message=f"Archived template {template.name}",
            user_id=user_id,
            action_type="archive_template",
            resource_type="template",
            resource_id=template_id
        )
        
        return template
    
    async def get_template_versions(self, template_id: str) -> List[Dict]:
        """
        Get all versions of a template
        
        Args:
            template_id: The template ID
            
        Returns:
            List[Dict]: List of template versions
        """
        return await self.template_repo.get_versions(template_id)
    
    async def restore_template_version(
        self, 
        template_id: str, 
        version: int,
        user_id: str = None
    ) -> Template:
        """
        Restore a template to a specific version
        
        Args:
            template_id: The template ID
            version: The version to restore
            user_id: ID of the user restoring the version
            
        Returns:
            Template: The updated template
        """
        result = await self.template_repo.restore_version(template_id, version)
        if not result:
            raise ValueError(f"Version {version} of template {template_id} not found")
            
        # Log the version restore
        audit_log(
            message=f"Restored template {result.name} to version {version}",
            user_id=user_id,
            action_type="restore_template_version",
            resource_type="template",
            resource_id=template_id,
            metadata={"version": version}
        )
        
        return result
    
    async def search_templates(self, query: str, limit: int = 10) -> List[Template]:
        """
        Search for templates
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Template]: Matching templates
        """
        return await self.template_repo.search(query, limit)
