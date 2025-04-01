import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder

from core.config import settings
from models.campaign import Campaign, CampaignStatus, CampaignType
from models.domain.notification import DeliveryStatus
from repositories.campaign import CampaignRepository
from repositories.segment import SegmentRepository
from repositories.template import TemplateRepository
from repositories.ab_test import AbTestRepository
from repositories.trigger import TriggerRepository
from repositories.user import UserRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class CampaignService:
    def __init__(self):
        self.campaign_repo = CampaignRepository()
        self.segment_repo = SegmentRepository()
        self.template_repo = TemplateRepository()
        self.ab_test_repo = AbTestRepository()
        self.trigger_repo = TriggerRepository()
        self.user_repo = UserRepository()

    async def create_campaign(self, campaign_data: Dict) -> Campaign:
        """
        Create a new campaign with initial status as draft
        """
        # Create campaign object with draft status
        campaign_data["status"] = CampaignStatus.DRAFT
        campaign_data["created_at"] = datetime.now()
        campaign_data["updated_at"] = datetime.now()
        
        # Handle campaign type-specific settings
        campaign_type = campaign_data.get("campaign_type", CampaignType.ONE_TIME)
        if campaign_type == CampaignType.RECURRING:
            if "recurrence_pattern" not in campaign_data:
                raise ValueError("Recurring campaigns require a recurrence pattern")
            campaign_data["is_recurring"] = True
        
        campaign = Campaign(**campaign_data)
        created_campaign = await self.campaign_repo.create(campaign)
        
        audit_log(f"Created campaign {created_campaign.id} - {created_campaign.name}")
        return created_campaign
    
    async def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """
        Get a campaign by ID
        """
        return await self.campaign_repo.get(campaign_id)
    
    async def get_all_campaigns(self, skip: int = 0, limit: int = 100) -> List[Campaign]:
        """
        Get all campaigns with pagination
        """
        return await self.campaign_repo.get_all(skip=skip, limit=limit)
    
    async def update_campaign(self, campaign_id: str, campaign_data: Dict) -> Campaign:
        """
        Update a campaign
        """
        # Get the existing campaign
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        # Don't allow status changes through this method
        if "status" in campaign_data:
            del campaign_data["status"]
        
        # Update fields
        campaign_data["updated_at"] = datetime.now()
        for key, value in campaign_data.items():
            setattr(campaign, key, value)
            
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Updated campaign {campaign_id}")
        return updated_campaign
    
    async def delete_campaign(self, campaign_id: str) -> bool:
        """
        Delete a campaign
        """
        # Check if campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        # Only allow deletion of draft campaigns
        if campaign.status != CampaignStatus.DRAFT:
            raise ValueError("Only draft campaigns can be deleted")
            
        result = await self.campaign_repo.delete(campaign_id)
        if result:
            audit_log(f"Deleted campaign {campaign_id}")
        return result
    
    async def set_campaign_template(self, campaign_id: str, template_id: str) -> Campaign:
        """
        Set the template for a campaign
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Verify template exists
        template = await self.template_repo.get(template_id)
        if not template:
            raise ValueError(f"Template with ID {template_id} not found")
            
        # Update campaign
        campaign.template_id = template_id
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Set template {template_id} for campaign {campaign_id}")
        return updated_campaign
    
    async def set_campaign_segment(self, campaign_id: str, segment_id: str) -> Campaign:
        """
        Set the target segment for a campaign
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Verify segment exists
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
            
        # Update campaign
        campaign.segment_id = segment_id
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Set segment {segment_id} for campaign {campaign_id}")
        return updated_campaign
    
    async def schedule_campaign(self, campaign_id: str, scheduled_time: datetime) -> Campaign:
        """
        Schedule a campaign for delivery
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Ensure campaign has required elements
        if not campaign.template_id:
            raise ValueError("Campaign requires a template before scheduling")
            
        if not campaign.segment_id:
            raise ValueError("Campaign requires a target segment before scheduling")
            
        # Cannot schedule campaigns in the past
        if scheduled_time < datetime.now():
            raise ValueError("Cannot schedule campaign for a time in the past")
            
        # Update campaign
        campaign.scheduled_time = scheduled_time
        campaign.status = CampaignStatus.SCHEDULED
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Scheduled campaign {campaign_id} for {scheduled_time}")
        
        # If A/B test campaign, ensure test is properly set up
        if campaign.campaign_type == CampaignType.AB_TEST:
            ab_tests = await self.ab_test_repo.get_by_campaign(campaign_id)
            if not ab_tests:
                logger.warning(f"A/B test campaign {campaign_id} has no test configured")
        
        return updated_campaign
    
    async def submit_for_approval(self, campaign_id: str) -> Campaign:
        """
        Submit a campaign for approval
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Can only submit draft campaigns for approval
        if campaign.status != CampaignStatus.DRAFT:
            raise ValueError("Only draft campaigns can be submitted for approval")
            
        # Update campaign status
        campaign.status = "pending_approval"  # Using string since it's not in the enum
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Submitted campaign {campaign_id} for approval")
        return updated_campaign
    
    async def approve_campaign(self, campaign_id: str) -> Campaign:
        """
        Approve a campaign that was submitted for approval
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Can only approve campaigns pending approval
        if campaign.status != "pending_approval":
            raise ValueError("Only campaigns pending approval can be approved")
            
        # Update campaign status
        campaign.status = CampaignStatus.DRAFT  # Return to draft status after approval
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Approved campaign {campaign_id}")
        return updated_campaign
    
    async def reject_campaign(self, campaign_id: str, reason: str = None) -> Campaign:
        """
        Reject a campaign that was submitted for approval
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Can only reject campaigns pending approval
        if campaign.status != "pending_approval":
            raise ValueError("Only campaigns pending approval can be rejected")
            
        # Update campaign status
        campaign.status = CampaignStatus.DRAFT  # Return to draft status after rejection
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Rejected campaign {campaign_id}" + (f": {reason}" if reason else ""))
        return updated_campaign
    
    async def activate_campaign(self, campaign_id: str) -> Campaign:
        """
        Activate a campaign for immediate sending
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Can only activate scheduled campaigns
        if campaign.status != CampaignStatus.SCHEDULED:
            raise ValueError("Only scheduled campaigns can be activated")
            
        # Update campaign status
        campaign.status = CampaignStatus.RUNNING
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Activated campaign {campaign_id}")
        
        # Queue campaign execution (this would normally trigger a background task)
        # from tasks.campaign_tasks import execute_campaign
        # execute_campaign.delay(campaign_id)
        
        return updated_campaign
    
    async def pause_campaign(self, campaign_id: str) -> Campaign:
        """
        Pause a running campaign
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Can only pause running campaigns
        if campaign.status != CampaignStatus.RUNNING:
            raise ValueError("Only running campaigns can be paused")
            
        # Update campaign status
        campaign.status = CampaignStatus.PAUSED
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Paused campaign {campaign_id}")
        return updated_campaign
    
    async def resume_campaign(self, campaign_id: str) -> Campaign:
        """
        Resume a paused campaign
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Can only resume paused campaigns
        if campaign.status != CampaignStatus.PAUSED:
            raise ValueError("Only paused campaigns can be resumed")
            
        # Update campaign status
        campaign.status = CampaignStatus.RUNNING
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Resumed campaign {campaign_id}")
        return updated_campaign
    
    async def complete_campaign(self, campaign_id: str) -> Campaign:
        """
        Mark a campaign as completed
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
            
        # Update campaign status
        campaign.status = CampaignStatus.COMPLETED
        campaign.updated_at = datetime.now()
        
        updated_campaign = await self.campaign_repo.update(campaign_id, campaign)
        audit_log(f"Completed campaign {campaign_id}")
        return updated_campaign
    
    async def create_ab_test_campaign(self, campaign_data: Dict, ab_test_data: Dict) -> Dict:
        """
        Create a new A/B test campaign
        """
        # First create the campaign
        campaign_data["campaign_type"] = CampaignType.AB_TEST
        campaign = await self.create_campaign(campaign_data)
        
        # Then create the A/B test
        ab_test_data["campaign_id"] = campaign.id
        ab_test = await self.ab_test_repo.create(ab_test_data)
        
        audit_log(f"Created A/B test campaign {campaign.id}")
        return {
            "campaign": campaign,
            "ab_test": ab_test
        }
    
    async def get_campaign_stats(self, campaign_id: str) -> Dict:
        """
        Get statistics for a campaign
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        # This would normally fetch stats from an analytics service
        # For now, return placeholder stats
        return {
            "campaign_id": campaign_id,
            "sent": 0,
            "delivered": 0,
            "opened": 0,
            "clicked": 0,
            "conversion_rate": 0
        }
    
    async def preview_campaign(self, campaign_id: str, user_id: Optional[str] = None) -> Dict:
        """
        Generate a preview of the campaign for a specific user
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        # Verify template exists
        if not campaign.template_id:
            raise ValueError("Campaign requires a template for preview")
        
        template = await self.template_repo.get(campaign.template_id)
        if not template:
            raise ValueError(f"Template {campaign.template_id} not found")
        
        # If user_id provided, get user data for personalization
        user_data = {}
        if user_id:
            user = await self.user_repo.get(user_id)
            if user:
                user_data = {
                    "name": user.name,
                    "email": user.email,
                    "first_name": user.name.split()[0] if user.name else "",
                    **user.custom_attributes
                }
        
        # Generate preview with basic personalization
        title = template.title
        body = template.body
        
        # Apply basic personalization if user data available
        if user_data:
            for key, value in user_data.items():
                placeholder = f"{{{key}}}"
                if isinstance(value, (str, int, float)):
                    title = title.replace(placeholder, str(value))
                    body = body.replace(placeholder, str(value))
        
        return {
            "title": title,
            "body": body,
            "image_url": template.image_url,
            "action_url": template.action_url,
            "campaign_id": campaign_id,
            "template_id": template.id,
            "personalized": bool(user_id)
        }
    
    async def validate_campaign(self, campaign_id: str) -> Dict:
        """
        Validate that a campaign is ready to be scheduled or activated
        """
        # Verify campaign exists
        campaign = await self.campaign_repo.get(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign with ID {campaign_id} not found")
        
        errors = []
        warnings = []
        
        # Check for required components
        if not campaign.template_id:
            errors.append("Campaign requires a template")
        
        if not campaign.segment_id:
            errors.append("Campaign requires a target segment")
        
        # Check for scheduled time if not trigger-based
        if campaign.campaign_type != CampaignType.TRIGGER_BASED and not campaign.scheduled_time:
            errors.append("Campaign requires a scheduled delivery time")
        
        # Check for recurring pattern if recurring campaign
        if campaign.campaign_type == CampaignType.RECURRING and not campaign.recurrence_pattern:
            errors.append("Recurring campaign requires a recurrence pattern")
        
        # Check for A/B test configuration if A/B test campaign
        if campaign.campaign_type == CampaignType.AB_TEST:
            ab_tests = await self.ab_test_repo.get_by_campaign(campaign_id)
            if not ab_tests:
                errors.append("A/B test campaign requires an A/B test configuration")
            else:
                ab_test = ab_tests[0]
                variants = await self.ab_test_repo.get_variants(ab_test.id)
                if len(variants) < 2:
                    errors.append("A/B test requires at least two variants")
        
        # Check for trigger configuration if trigger-based
        if campaign.campaign_type == CampaignType.TRIGGER_BASED:
            triggers = await self.trigger_repo.get_by_campaign(campaign_id)
            if not triggers:
                errors.append("Trigger-based campaign requires at least one trigger")
        
        # Check target segment size
        if campaign.segment_id:
            segment = await self.segment_repo.get(campaign.segment_id)
            if segment:
                if segment.user_count == 0:
                    errors.append("Target segment contains no users")
                elif segment.user_count < 10:
                    warnings.append(f"Target segment only contains {segment.user_count} users")
        
        return {
            "campaign_id": campaign_id,
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
