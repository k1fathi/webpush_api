import logging
import uuid
import json
from datetime import datetime
from typing import Dict, List, Optional, Any

import httpx
from fastapi.encoders import jsonable_encoder

from core.config import settings
from models.cdp_integration import CdpIntegration, CdpSyncStatus
from repositories.cdp_integration import CdpIntegrationRepository
from repositories.user import UserRepository
from utils.audit import audit_log

logger = logging.getLogger(__name__)

class CdpService:
    """
    Service for managing CDP (Customer Data Platform) integrations
    Implements the CDP integration flow documented in cdp_integration_flow.mmd
    """
    def __init__(self):
        self.cdp_repo = CdpIntegrationRepository()
        self.user_repo = UserRepository()
        self.api_url = settings.CDP_API_URL
        self.api_key = settings.CDP_API_KEY
        self.timeout = 30.0  # seconds
    
    def is_enabled(self) -> bool:
        """Check if CDP integration is enabled"""
        return bool(self.api_url and self.api_key)
    
    async def track_event(self, event_data: Dict[str, Any]) -> bool:
        """
        Send an event to the CDP
        
        Args:
            event_data: Dictionary containing event data (user_id, event_type, properties, etc.)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_enabled():
            logger.warning("CDP integration not enabled, skipping event tracking")
            return False
            
        try:
            # Normalize the event data
            normalized_data = self._normalize_event_data(event_data)
            
            # Send to CDP
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/events",
                    json=normalized_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"Event tracked successfully in CDP for user {event_data.get('user_id')}")
                
                # Update last sync timestamp for user
                await self._update_user_sync_timestamp(event_data.get('user_id'))
                
                return True
            else:
                logger.error(f"Failed to track event in CDP. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error tracking event in CDP: {str(e)}")
            return False
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user profile from the CDP
        
        Args:
            user_id: The user ID to retrieve
            
        Returns:
            Optional[Dict]: User profile data or None if not found/error
        """
        if not self.is_enabled():
            logger.warning("CDP integration not enabled, skipping profile retrieval")
            return None
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/users/{user_id}",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                
            if response.status_code == 200:
                user_profile = response.json()
                return user_profile
            elif response.status_code == 404:
                logger.info(f"User {user_id} not found in CDP")
                return None
            else:
                logger.error(f"Failed to get user profile from CDP. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user profile from CDP: {str(e)}")
            return None
    
    async def sync_user_data(self, user_id: str) -> bool:
        """
        Sync user data bidirectionally between WebPush and CDP
        
        Args:
            user_id: The user ID to sync
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Get user from local database
        user = await self.user_repo.get(user_id)
        if not user:
            logger.error(f"User {user_id} not found in database")
            return False
            
        # First push local user data to CDP
        user_data = {
            "user_id": str(user.id),
            "email": user.email,
            "name": user.name,
            "subscription_date": user.subscription_date.isoformat() if user.subscription_date else None,
            "opted_in": user.opted_in,
            "last_activity": user.last_activity.isoformat() if user.last_activity else None,
            "custom_attributes": user.custom_attributes
        }
        
        push_success = await self.update_cdp_profile(user_id, user_data)
        
        # Then pull CDP data to enrich local user
        cdp_profile = await self.get_user_profile(user_id)
        
        if cdp_profile:
            # Get existing CDP integration or create new one
            cdp_integration = await self.cdp_repo.get_by_user_id(user_id)
            
            if cdp_integration:
                # Update existing integration
                cdp_integration.user_profile_data = cdp_profile
                cdp_integration.last_synced = datetime.now()
                cdp_integration.sync_status = CdpSyncStatus.SUCCESS
                await self.cdp_repo.update(cdp_integration.id, cdp_integration)
            else:
                # Create new integration
                new_integration = CdpIntegration(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    user_profile_data=cdp_profile,
                    behavioral_data={},
                    last_synced=datetime.now(),
                    sync_status=CdpSyncStatus.SUCCESS
                )
                await self.cdp_repo.create(new_integration)
                
            # Update user's custom attributes with relevant CDP data
            if "segments" in cdp_profile:
                user.custom_attributes["cdp_segments"] = cdp_profile["segments"]
                
            if "scores" in cdp_profile:
                user.custom_attributes["cdp_scores"] = cdp_profile["scores"]
                
            await self.user_repo.update(user)
            
            audit_log(f"Synced user {user_id} data with CDP")
            return True
        else:
            logger.warning(f"No CDP profile found for user {user_id}")
            return push_success
    
    async def update_cdp_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update a user profile in the CDP
        
        Args:
            user_id: The user ID to update
            profile_data: Dictionary containing profile data
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_enabled():
            logger.warning("CDP integration not enabled, skipping profile update")
            return False
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.api_url}/users/{user_id}",
                    json=profile_data,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=self.timeout
                )
                
            if response.status_code >= 200 and response.status_code < 300:
                logger.info(f"User profile updated successfully in CDP for user {user_id}")
                return True
            else:
                logger.error(f"Failed to update profile in CDP. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating profile in CDP: {str(e)}")
            return False
    
    def _normalize_event_data(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize event data to ensure it meets CDP requirements"""
        # Create a copy to avoid modifying the original
        normalized = event_data.copy()
        
        # Ensure timestamp is in ISO format
        if "timestamp" not in normalized:
            normalized["timestamp"] = datetime.now().isoformat()
            
        # Ensure user_id is a string
        if "user_id" in normalized:
            normalized["user_id"] = str(normalized["user_id"])
            
        # Add source system identifier
        if "properties" not in normalized:
            normalized["properties"] = {}
            
        normalized["properties"]["source_system"] = "webpush_api"
        
        # Add context if not present
        if "context" not in normalized:
            normalized["context"] = {}
            
        return normalized
    
    async def _update_user_sync_timestamp(self, user_id: str) -> bool:
        """Update the last sync timestamp for a user"""
        if not user_id:
            return False
            
        try:
            # Get existing CDP integration
            cdp_integration = await self.cdp_repo.get_by_user_id(user_id)
            
            if cdp_integration:
                cdp_integration.last_synced = datetime.now()
                await self.cdp_repo.update(cdp_integration.id, cdp_integration)
            # We don't create a new integration here as we only want to update if it exists
                
            return True
        except Exception as e:
            logger.error(f"Error updating user sync timestamp: {str(e)}")
            return False
