import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from croniter import croniter
from fastapi.encoders import jsonable_encoder

from core.config import settings
from models.trigger import (
    Trigger, TriggerStatus, TriggerType, TriggerAction,
    ScheduleConfig, ActionConfig
)
from repositories.trigger import TriggerRepository
from repositories.notification import NotificationRepository
from repositories.campaign import CampaignRepository
from repositories.segment import SegmentRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class TriggerService:
    """Service for trigger management according to trigger_based_flow.mmd"""
    
    def __init__(self):
        self.trigger_repo = TriggerRepository()
        self.notification_repo = NotificationRepository()
        self.campaign_repo = CampaignRepository()
        self.segment_repo = SegmentRepository()

    async def create_trigger(self, trigger_data: Dict, user_id: str = None) -> Trigger:
        """Create a new trigger"""
        # Create trigger object
        trigger = Trigger(
            id=str(uuid.uuid4()),
            status=TriggerStatus.ACTIVE,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **trigger_data
        )

        # Validate schedule if provided
        if trigger.schedule:
            self._validate_schedule(trigger.schedule)

        # Validate action configuration
        await self._validate_action_config(trigger.action)

        # Save to repository
        created_trigger = await self.trigger_repo.create(trigger)

        # Log creation
        audit_log(
            message=f"Created trigger {created_trigger.name}",
            user_id=user_id,
            action_type="create_trigger",
            resource_type="trigger",
            resource_id=created_trigger.id
        )

        return created_trigger

    async def update_trigger(
        self,
        trigger_id: str,
        trigger_data: Dict,
        user_id: str = None
    ) -> Trigger:
        """Update an existing trigger"""
        # Get existing trigger
        trigger = await self.trigger_repo.get(trigger_id)
        if not trigger:
            raise ValueError(f"Trigger with ID {trigger_id} not found")

        # Update fields
        for key, value in trigger_data.items():
            if hasattr(trigger, key):
                setattr(trigger, key, value)

        # Validate if schedule was updated
        if "schedule" in trigger_data and trigger.schedule:
            self._validate_schedule(trigger.schedule)

        # Validate if action was updated
        if "action" in trigger_data:
            await self._validate_action_config(trigger.action)

        trigger.updated_at = datetime.now()

        # Save updates
        updated_trigger = await self.trigger_repo.update(trigger_id, trigger)

        # Log update
        audit_log(
            message=f"Updated trigger {updated_trigger.name}",
            user_id=user_id,
            action_type="update_trigger",
            resource_type="trigger",
            resource_id=trigger_id
        )

        return updated_trigger

    def _validate_schedule(self, schedule: ScheduleConfig) -> None:
        """Validate trigger schedule configuration"""
        if not schedule.frequency:
            raise ValueError("Schedule frequency is required")

        # Validate cron expression
        try:
            croniter(schedule.frequency)
        except ValueError as e:
            raise ValueError(f"Invalid cron expression: {str(e)}")

        # Validate dates
        if schedule.start_date and schedule.end_date:
            if schedule.start_date >= schedule.end_date:
                raise ValueError("End date must be after start date")

    async def _validate_action_config(self, action: ActionConfig) -> None:
        """Validate trigger action configuration"""
        if action.action_type == TriggerAction.SEND_NOTIFICATION:
            if not action.template_id:
                raise ValueError("Template ID is required for notification actions")
                
            # Verify template exists
            template = await self.template_repo.get(action.template_id)
            if not template:
                raise ValueError(f"Template {action.template_id} not found")

        elif action.action_type == TriggerAction.START_CAMPAIGN:
            if not action.campaign_id:
                raise ValueError("Campaign ID is required for campaign actions")
                
            # Verify campaign exists
            campaign = await self.campaign_repo.get(action.campaign_id)
            if not campaign:
                raise ValueError(f"Campaign {action.campaign_id} not found")

        elif action.action_type == TriggerAction.UPDATE_SEGMENT:
            if not action.segment_id:
                raise ValueError("Segment ID is required for segment actions")
                
            # Verify segment exists
            segment = await self.segment_repo.get(action.segment_id)
            if not segment:
                raise ValueError(f"Segment {action.segment_id} not found")

        elif action.action_type == TriggerAction.WEBHOOK:
            if not action.webhook_url:
                raise ValueError("Webhook URL is required for webhook actions")

    async def process_event(self, event_data: Dict) -> List[Dict]:
        """Process an event and execute matching triggers"""
        # Get all active triggers
        active_triggers = await self.trigger_repo.get_active_triggers()
        
        results = []
        for trigger in active_triggers:
            if await self._should_execute_trigger(trigger, event_data):
                try:
                    result = await self._execute_trigger(trigger, event_data)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error executing trigger {trigger.id}: {str(e)}")
                    await self.trigger_repo.record_execution(
                        trigger.id,
                        success=False,
                        error=str(e)
                    )
                    
        return results

    async def _should_execute_trigger(self, trigger: Trigger, event_data: Dict) -> bool:
        """Check if a trigger should be executed for an event"""
        # Check if trigger is enabled
        if not trigger.enabled:
            return False

        # Check cooldown period
        if trigger.last_triggered_at and trigger.cooldown_period:
            cooldown_ends = trigger.last_triggered_at + trigger.cooldown_period
            if datetime.now() < cooldown_ends:
                return False

        # Check daily limit
        if trigger.max_triggers_per_day:
            today_count = await self._get_trigger_count_today(trigger.id)
            if today_count >= trigger.max_triggers_per_day:
                return False

        # Match event against trigger rules
        return self._event_matches_rules(event_data, trigger.rules)

    def _event_matches_rules(self, event_data: Dict, rules: List[Dict]) -> bool:
        """Check if an event matches trigger rules"""
        # Implementation would depend on your rule matching logic
        # This is a simplified version
        for rule in rules:
            if not self._match_single_rule(event_data, rule):
                return False
        return True

    def _match_single_rule(self, event_data: Dict, rule: Dict) -> bool:
        """Match an event against a single rule"""
        # Simple rule matching logic
        # Would be more sophisticated in a real implementation
        for condition in rule.get('conditions', []):
            field_value = event_data.get(condition['field'])
            if not self._check_condition(field_value, condition):
                return False
        return True

    def _check_condition(self, value: Any, condition: Dict) -> bool:
        """Check a value against a condition"""
        operator = condition.get('operator', 'equals')
        test_value = condition.get('value')

        if operator == 'equals':
            return value == test_value
        elif operator == 'not_equals':
            return value != test_value
        elif operator == 'contains':
            return test_value in value if value else False
        elif operator == 'greater_than':
            return value > test_value if value is not None else False
        elif operator == 'less_than':
            return value < test_value if value is not None else False
        
        return False

    async def _execute_trigger(self, trigger: Trigger, event_data: Dict) -> Dict:
        """Execute a trigger's action"""
        action = trigger.action
        result = None
        error = None

        try:
            if action.action_type == TriggerAction.SEND_NOTIFICATION:
                result = await self._execute_notification_action(action, event_data)
            elif action.action_type == TriggerAction.START_CAMPAIGN:
                result = await self._execute_campaign_action(action, event_data)
            elif action.action_type == TriggerAction.UPDATE_SEGMENT:
                result = await self._execute_segment_action(action, event_data)
            elif action.action_type == TriggerAction.WEBHOOK:
                result = await self._execute_webhook_action(action, event_data)

            success = True
        except Exception as e:
            success = False
            error = str(e)
            raise

        finally:
            # Record execution
            await self.trigger_repo.record_execution(
                trigger.id,
                success=success,
                action_result=result,
                error=error
            )

        return {
            "trigger_id": trigger.id,
            "action_type": action.action_type,
            "success": success,
            "result": result,
            "error": error
        }

    async def _execute_notification_action(self, action: ActionConfig, event_data: Dict) -> Dict:
        """Execute a notification action"""
        # Implementation would create and send a notification
        # This is a placeholder
        return {"status": "notification_sent"}

    async def _execute_campaign_action(self, action: ActionConfig, event_data: Dict) -> Dict:
        """Execute a campaign action"""
        # Implementation would start a campaign
        # This is a placeholder
        return {"status": "campaign_started"}

    async def _execute_segment_action(self, action: ActionConfig, event_data: Dict) -> Dict:
        """Execute a segment update action"""
        # Implementation would update a segment
        # This is a placeholder
        return {"status": "segment_updated"}

    async def _execute_webhook_action(self, action: ActionConfig, event_data: Dict) -> Dict:
        """Execute a webhook action"""
        # Implementation would call a webhook
        # This is a placeholder
        return {"status": "webhook_called"}

    async def _get_trigger_count_today(self, trigger_id: str) -> int:
        """Get the number of times a trigger has been executed today"""
        # Implementation would count today's executions
        # This is a placeholder
        return 0
