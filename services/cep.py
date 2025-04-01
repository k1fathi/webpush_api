import logging
import json
import uuid
from datetime import datetime, time
from typing import Dict, List, Optional, Any, Tuple

import httpx
from fastapi.encoders import jsonable_encoder

from core.config import settings
from models.cep_decision import CepDecision, DecisionStatus
from repositories.cep_decision import CepDecisionRepository
from repositories.user import UserRepository
from repositories.analytics import AnalyticsRepository
from repositories.campaign import CampaignRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class CepService:
    """
    Service for Complex Event Processing (CEP) integrations
    Implements the CEP decision flow documented in cep_decision_flow.mmd
    """
    def __init__(self):
        self.cep_repo = CepDecisionRepository()
        self.user_repo = UserRepository()
        self.analytics_repo = AnalyticsRepository()
        self.campaign_repo = CampaignRepository()
        self.api_url = settings.CEP_API_URL
        self.api_key = settings.CEP_API_KEY
        self.timeout = 30.0  # seconds
        
        # Channel weights - could be dynamically configured
        self._channel_weights = {
            "webpush": 1.0,
            "email": 0.9,
            "sms": 0.8,
            "in_app": 0.85,
            "mobile_push": 0.95
        }
    
    def is_enabled(self) -> bool:
        """Check if CEP integration is enabled"""
        return bool(self.api_url and self.api_key)
    
    async def get_optimal_channel(
        self,
        user_id: str,
        campaign_id: Optional[str] = None,
        message_data: Optional[Dict] = None
    ) -> str:
        """
        Determine the optimal channel for a communication
        
        Args:
            user_id: The user ID to make a decision for
            campaign_id: Optional campaign ID for context
            message_data: Optional message data for context
            
        Returns:
            str: The selected channel (webpush, email, sms, etc.)
        """
        # If CEP is not enabled, default to webpush
        if not self.is_enabled():
            return "webpush"
        
        try:
            # Try to use external CEP service first
            external_decision = await self._get_external_decision(user_id, campaign_id, message_data)
            if external_decision:
                return external_decision
        except Exception as e:
            logger.warning(f"External CEP service failed, using local logic: {str(e)}")
            
        # Fall back to local decision logic if external service fails or returns None
        return await self._make_local_decision(user_id, campaign_id, message_data)
    
    async def _get_external_decision(
        self,
        user_id: str,
        campaign_id: Optional[str] = None,
        message_data: Optional[Dict] = None
    ) -> Optional[str]:
        """Get channel decision from external CEP service"""
        try:
            # Prepare request data
            request_data = {
                "user_id": user_id,
                "timestamp": datetime.now().isoformat(),
                "context": {
                    "campaign_id": campaign_id,
                    "message_data": message_data or {},
                    "platform": "webpush_api"
                }
            }
            
            # Call external CEP service
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/decide",
                    json=request_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                
            if response.status_code == 200:
                result = response.json()
                if "selected_channel" in result:
                    # Record the decision
                    await self.record_channel_decision(
                        user_id=user_id,
                        campaign_id=campaign_id,
                        selected_channel=result["selected_channel"],
                        score=result.get("score", 0.0),
                        factors=result.get("factors", {})
                    )
                    return result["selected_channel"]
            
            logger.warning(f"External CEP service returned invalid response: {response.text}")
            return None
                
        except Exception as e:
            logger.error(f"Error getting decision from external CEP service: {str(e)}")
            return None
    
    async def _make_local_decision(
        self,
        user_id: str,
        campaign_id: Optional[str] = None,
        message_data: Optional[Dict] = None
    ) -> str:
        """Make a channel decision using local logic"""
        # Get user data
        user = await self.user_repo.get(user_id)
        if not user:
            logger.warning(f"User {user_id} not found, defaulting to webpush")
            return "webpush"
            
        # Initialize channel scores
        channels = {
            "webpush": 0.0,
            "email": 0.0,
            "sms": 0.0,
            "in_app": 0.0,
            "mobile_push": 0.0
        }
        
        # Get analytics data for this user
        user_analytics = await self.analytics_repo.get_by_user(user_id)
        
        # Calculate channel scores based on engagement history
        for channel in channels.keys():
            # Base score from configuration
            channels[channel] = self._channel_weights.get(channel, 0.5)
            
            # Modify based on user preferences if available
            if user.custom_attributes and "channel_preferences" in user.custom_attributes:
                preference = user.custom_attributes["channel_preferences"].get(channel)
                if preference:
                    channels[channel] *= float(preference)
            
            # Modify based on historical engagement
            if channel == "webpush" and user.push_token:
                # User has webpush token, increase score
                channels[channel] *= 1.2
                
                # Check if they've clicked on webpush notifications
                webpush_clicks = sum(1 for a in user_analytics if a.clicked)
                if webpush_clicks > 0:
                    channels[channel] *= 1.0 + (min(webpush_clicks, 10) / 10)
            
            # Consider time of day
            channels[channel] *= self._get_time_factor(channel)
            
            # Device-specific adjustments
            if user.browser and channel == "webpush":
                # Check for browsers that support webpush well
                if user.browser.lower() in ("chrome", "firefox", "edge"):
                    channels[channel] *= 1.1
            
            # Campaign-specific adjustments
            if campaign_id and channel == "webpush":
                # For high-urgency campaigns, prioritize immediate channels
                campaign = await self.campaign_repo.get(campaign_id)
                if campaign and campaign.custom_attributes:
                    urgency = campaign.custom_attributes.get("urgency", "normal")
                    if urgency == "high":
                        channels[channel] *= 1.2
        
        # Find the channel with the highest score
        selected_channel, highest_score = max(channels.items(), key=lambda x: x[1])
        
        # Record the decision
        factors = {
            "user_has_token": bool(user.push_token),
            "browser": user.browser,
            "time_factor": self._get_time_factor("webpush"),
            "scores": channels
        }
        
        await self.record_channel_decision(
            user_id=user_id,
            campaign_id=campaign_id,
            selected_channel=selected_channel,
            score=highest_score,
            factors=factors
        )
        
        return selected_channel
    
    def _get_time_factor(self, channel: str) -> float:
        """Get a factor representing how optimal the current time is for a channel"""
        current_hour = datetime.now().hour
        
        # Default time factors by hour for each channel
        # These would ideally be based on analytics data
        
        # For webpush, best during working hours
        if channel == "webpush":
            if 9 <= current_hour <= 18:  # 9 AM - 6 PM
                return 1.2
            elif 7 <= current_hour <= 22:  # 7 AM - 10 PM (awake hours)
                return 1.0
            else:  # Late night hours
                return 0.5
        
        # For email, best in morning and evening
        elif channel == "email":
            if 8 <= current_hour <= 10:  # Morning
                return 1.3
            elif 17 <= current_hour <= 21:  # Evening
                return 1.2
            elif 7 <= current_hour <= 23:  # General awake hours
                return 1.0
            else:  # Late night
                return 0.7
        
        # For SMS, prioritize urgent times, avoid late night
        elif channel == "sms":
            if 22 <= current_hour or current_hour <= 7:  # Night time
                return 0.3  # Strongly avoid late night SMS
            else:
                return 1.0
                
        # Default time factor
        return 1.0
    
    async def record_channel_decision(
        self,
        user_id: str,
        campaign_id: Optional[str],
        selected_channel: str,
        score: float,
        factors: Dict
    ) -> CepDecision:
        """
        Record a channel selection decision
        
        Args:
            user_id: The user ID
            campaign_id: Optional campaign ID
            selected_channel: The selected channel
            score: The score of the selected channel
            factors: Dictionary of factors that influenced the decision
            
        Returns:
            CepDecision: The recorded decision
        """
        decision = CepDecision(
            id=str(uuid.uuid4()),
            user_id=user_id,
            campaign_id=campaign_id,
            decision_time=datetime.now(),
            selected_channel=selected_channel,
            score=score,
            decision_factors=factors,
            status=DecisionStatus.CREATED
        )
        
        created_decision = await self.cep_repo.create(decision)
        audit_log(f"Recorded CEP channel decision for user {user_id}: {selected_channel}")
        return created_decision
    
    async def record_decision_outcome(
        self,
        decision_id: str,
        outcome: Dict[str, Any]
    ) -> Optional[CepDecision]:
        """
        Record the outcome of a channel decision
        
        Args:
            decision_id: The decision ID
            outcome: Dictionary with outcome data (delivered, engaged, etc.)
            
        Returns:
            Optional[CepDecision]: The updated decision record
        """
        decision = await self.cep_repo.get(decision_id)
        if not decision:
            logger.error(f"Decision {decision_id} not found")
            return None
            
        decision.outcome = outcome
        decision.status = DecisionStatus.COMPLETED
        updated_decision = await self.cep_repo.update(decision_id, decision)
        
        audit_log(f"Updated CEP decision {decision_id} with outcome")
        return updated_decision
        
    async def get_optimal_send_time(
        self,
        user_id: str,
        channel: str = "webpush",
        max_delay_hours: int = 24
    ) -> datetime:
        """
        Determine the optimal time to send a notification
        
        Args:
            user_id: The user ID
            channel: The communication channel
            max_delay_hours: Maximum hours to delay the notification
            
        Returns:
            datetime: The optimal send time
        """
        # Get user data
        user = await self.user_repo.get(user_id)
        if not user:
            logger.warning(f"User {user_id} not found, using current time")
            return datetime.now()
            
        # If user has a preferred time in their profile, use that
        if (user.custom_attributes and 
            "preferred_notification_time" in user.custom_attributes):
            preferred_time = user.custom_attributes["preferred_notification_time"]
            
            # Convert string time to datetime for today
            try:
                hour, minute = map(int, preferred_time.split(':'))
                now = datetime.now()
                preferred_datetime = datetime.combine(now.date(), time(hour, minute))
                
                # If preferred time is in the past for today, use tomorrow
                if preferred_datetime < now:
                    preferred_datetime = preferred_datetime.replace(
                        day=now.day + 1
                    )
                
                # Ensure we're not delaying beyond max_delay_hours
                if (preferred_datetime - now).total_seconds() <= max_delay_hours * 3600:
                    return preferred_datetime
            except (ValueError, AttributeError) as e:
                logger.warning(f"Invalid preferred time format: {preferred_time}, {str(e)}")
        
        # Otherwise, use engagement history to find optimal time
        if channel == "webpush":
            # Get user's past webpush engagements
            notifications = await self.analytics_repo.get_by_user(user_id)
            
            # Extract hours when user engaged with notifications
            engaged_hours = []
            for notification in notifications:
                if notification.opened or notification.clicked:
                    if notification.event_time:
                        engaged_hours.append(notification.event_time.hour)
            
            if engaged_hours:
                # Find the most common engagement hour
                from collections import Counter
                hour_counts = Counter(engaged_hours)
                optimal_hour, _ = hour_counts.most_common(1)[0]
                
                # Create a datetime for this hour today
                now = datetime.now()
                optimal_time = now.replace(hour=optimal_hour, minute=0, second=0)
                
                # If optimal time is in the past, schedule for tomorrow
                if optimal_time < now:
                    optimal_time = optimal_time.replace(day=now.day + 1)
                
                # Ensure we're not delaying beyond max_delay_hours
                if (optimal_time - now).total_seconds() <= max_delay_hours * 3600:
                    return optimal_time
        
        # Default to current time if no better option found
        return datetime.now()
    
    async def optimize_notification_parameters(
        self,
        user_id: str,
        notification_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimize notification parameters for a specific user
        
        Args:
            user_id: The user ID
            notification_data: Original notification parameters
            
        Returns:
            Dict[str, Any]: Optimized notification parameters
        """
        # Make a copy to avoid modifying the original
        optimized_data = notification_data.copy()
        
        # Get user data
        user = await self.user_repo.get(user_id)
        if not user:
            return optimized_data
            
        # Get user's engagement history
        user_analytics = await self.analytics_repo.get_by_user(user_id)
        
        # Optimize title if possible
        if "title" in optimized_data:
            # Personal greeting
            if user.name and "{name}" not in optimized_data["title"]:
                # Insert name if title is not too long
                if len(optimized_data["title"]) < 30:
                    optimized_data["title"] = f"Hi {user.name.split()[0]}! {optimized_data['title']}"
        
        # Optimize timing - already handled by get_optimal_send_time
        
        # Add action buttons based on past behavior
        clicked_actions = {}
        for event in user_analytics:
            if event.clicked and event.user_action:
                # Extract action from user_action (e.g., "click:action_name")
                if ":" in event.user_action:
                    _, action = event.user_action.split(":", 1)
                    clicked_actions[action] = clicked_actions.get(action, 0) + 1
        
        # If user has clicked specific actions, prioritize them
        if clicked_actions:
            # Find most clicked action
            most_clicked = max(clicked_actions.items(), key=lambda x: x[1])[0]
            
            # Add or prioritize this action
            if "actions" in optimized_data and isinstance(optimized_data["actions"], list):
                # Move preferred action to front if it exists
                actions = optimized_data["actions"]
                for i, action in enumerate(actions):
                    if action.get("action") == most_clicked:
                        # Swap to first position
                        if i > 0:
                            actions[0], actions[i] = actions[i], actions[0]
                        break
        
        return optimized_data
