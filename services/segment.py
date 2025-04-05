import logging
import uuid
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any, Tuple, Union

from core.config import settings
from models.schemas.segment import Segment, SegmentType, SegmentOperator, CompositeOperator
from repositories.segment import SegmentRepository
from repositories.user import UserRepository
from repositories.campaign import CampaignRepository
from utils.audit import audit_log
from utils.query_builder import build_segment_query

logger = logging.getLogger(__name__)

class SegmentService:
    """Service for segment management according to segment_management_flow.mmd"""
    
    def __init__(self):
        self.segment_repo = SegmentRepository()
        self.user_repo = UserRepository()
        self.campaign_repo = CampaignRepository()
        
    async def create_segment(self, segment_data: Dict) -> Segment:
        """
        Create a new user segment
        
        Args:
            segment_data: Dictionary with segment data
            
        Returns:
            Segment: The created segment
        """
        # Create segment with initial user count of 0
        segment = Segment(
            id=str(uuid.uuid4()),
            user_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            **segment_data
        )
        
        # Save to repository
        created_segment = await self.segment_repo.create(segment)
        
        # Log creation
        audit_log(f"Created segment {created_segment.id} - {created_segment.name}")
        
        # For static segments with pre-defined users, we don't need evaluation
        # For other types, queue an evaluation job
        if segment.segment_type != SegmentType.STATIC:
            # Queue evaluation task to calculate initial user count
            from tasks.segment_tasks import evaluate_segment
            evaluate_segment.delay(str(created_segment.id))
        
        return created_segment
    
    async def update_segment(self, segment_id: str, segment_data: Dict) -> Segment:
        """
        Update an existing segment
        
        Args:
            segment_id: The segment ID
            segment_data: Dictionary with updated segment data
            
        Returns:
            Segment: The updated segment
        """
        # Get existing segment
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        
        # Update fields
        for key, value in segment_data.items():
            if hasattr(segment, key):
                setattr(segment, key, value)
        
        segment.updated_at = datetime.now()
        
        # Save updated segment
        updated_segment = await self.segment_repo.update(segment_id, segment)
        
        # Log update
        audit_log(f"Updated segment {segment_id} - {updated_segment.name}")
        
        # Queue re-evaluation since criteria may have changed
        if segment.segment_type != SegmentType.STATIC:
            from tasks.segment_tasks import evaluate_segment
            evaluate_segment.delay(segment_id)
            
        return updated_segment
    
    async def delete_segment(self, segment_id: str) -> bool:
        """
        Delete a segment
        
        Args:
            segment_id: The segment ID
            
        Returns:
            bool: True if deleted, False otherwise
        """
        # Check if segment is used by any campaigns
        campaigns_using_segment = await self.campaign_repo.get_by_segment(segment_id)
        if campaigns_using_segment:
            raise ValueError(
                f"Cannot delete segment {segment_id} as it is used by "
                f"{len(campaigns_using_segment)} campaign(s)"
            )
            
        # Delete the segment
        result = await self.segment_repo.delete(segment_id)
        if result:
            audit_log(f"Deleted segment {segment_id}")
            
        return result
    
    async def get_segment(self, segment_id: str) -> Optional[Segment]:
        """
        Get a segment by ID
        
        Args:
            segment_id: The segment ID
            
        Returns:
            Optional[Segment]: The segment if found
        """
        return await self.segment_repo.get(segment_id)
    
    async def get_all_segments(
        self, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = False
    ) -> Tuple[List[Segment], int]:
        """
        Get all segments with pagination
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            active_only: Whether to return only active segments
            
        Returns:
            Tuple[List[Segment], int]: List of segments and total count
        """
        segments = await self.segment_repo.get_all(skip, limit, active_only)
        total = await self.segment_repo.count_segments()
        return segments, total
    
    async def evaluate_segment(
        self, 
        segment_id: str,
        get_matched_users: bool = False
    ) -> Dict:
        """
        Evaluate a segment to determine matching users
        
        Args:
            segment_id: The segment ID
            get_matched_users: Whether to return the list of matching user IDs
            
        Returns:
            Dict: Evaluation results with user count and optionally user list
        """
        # Get the segment
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
            
        matched_user_ids = []
            
        # Process based on segment type
        if segment.segment_type == SegmentType.STATIC:
            # Static segments contain explicit user lists in filter_criteria
            if segment.filter_criteria and "user_ids" in segment.filter_criteria:
                user_ids = segment.filter_criteria.get("user_ids", [])
                user_count = len(user_ids)
                matched_user_ids = user_ids
            else:
                user_count = 0
                
        elif segment.segment_type == SegmentType.DYNAMIC:
            # Dynamic segments have criteria to query users
            # This is a simplified version - in a real implementation, you'd build
            # and execute a proper database query based on criteria
            matched_user_ids = await self._evaluate_dynamic_segment(segment)
            user_count = len(matched_user_ids)
            
        elif segment.segment_type == SegmentType.BEHAVIORAL:
            # Behavioral segments are based on user actions/behavior
            matched_user_ids = await self._evaluate_behavioral_segment(segment)
            user_count = len(matched_user_ids)
            
        elif segment.segment_type == SegmentType.COMPOSITE:
            # Composite segments combine other segments
            matched_user_ids = await self._evaluate_composite_segment(segment)
            user_count = len(matched_user_ids)
            
        else:
            user_count = 0
            
        # Update segment user count
        segment.user_count = user_count
        segment.last_evaluated_at = datetime.now()
        await self.segment_repo.update(segment_id, segment)
        
        audit_log(f"Evaluated segment {segment_id}, found {user_count} users")
        
        # Return results
        result = {
            "segment_id": segment_id,
            "user_count": user_count,
            "evaluation_time": datetime.now()
        }
        
        # Include matched users if requested
        if get_matched_users:
            result["matched_users"] = matched_user_ids
            
        return result
    
    async def _evaluate_dynamic_segment(self, segment: Segment) -> List[str]:
        """
        Evaluate a dynamic segment based on filter criteria
        
        Args:
            segment: The segment to evaluate
            
        Returns:
            List[str]: List of matching user IDs
        """
        # Get all users - this is a simplified approach
        all_users = await self.user_repo.get_all()
        
        # No criteria means no matches
        if not segment.filter_criteria:
            return []
            
        # Filter users based on criteria
        matched_users = []
        for user in all_users:
            if self._user_matches_criteria(user, segment.filter_criteria):
                matched_users.append(str(user.id))
                
        return matched_users
    
    def _user_matches_criteria(self, user: Any, criteria: Dict) -> bool:
        """
        Check if a user matches segment criteria
        
        Args:
            user: The user to check
            criteria: The filter criteria
            
        Returns:
            bool: Whether the user matches the criteria
        """
        # Simplified criteria matching logic
        # In a real implementation, this would be more sophisticated
        
        # Basic field match
        for field, value in criteria.items():
            # Skip special fields
            if field in ["operator", "rules"]:
                continue
                
            # Handle nested fields with dot notation (e.g., "custom_attributes.country")
            if "." in field:
                parts = field.split(".")
                field_value = user
                for part in parts:
                    if hasattr(field_value, part):
                        field_value = getattr(field_value, part)
                    elif isinstance(field_value, dict) and part in field_value:
                        field_value = field_value[part]
                    else:
                        field_value = None
                        break
            else:
                # Direct attribute
                field_value = getattr(user, field, None)
                
            # Simple equality check - in practice you'd have different operators
            if field_value != value:
                # Check for specific operators if defined
                operator = criteria.get("operator", "equals")
                if not self._check_with_operator(field_value, value, operator):
                    return False
        
        return True
    
    def _check_with_operator(self, field_value: Any, test_value: Any, operator: str) -> bool:
        """
        Check a field value against a test value using the specified operator
        
        Args:
            field_value: The field value to check
            test_value: The value to test against
            operator: The operator to use
            
        Returns:
            bool: Whether the check passes
        """
        if operator == SegmentOperator.EQUALS:
            return field_value == test_value
        elif operator == SegmentOperator.NOT_EQUALS:
            return field_value != test_value
        elif operator == SegmentOperator.GREATER_THAN:
            return field_value > test_value
        elif operator == SegmentOperator.LESS_THAN:
            return field_value < test_value
        elif operator == SegmentOperator.CONTAINS:
            return test_value in field_value if field_value else False
        elif operator == SegmentOperator.NOT_CONTAINS:
            return test_value not in field_value if field_value else True
        elif operator == SegmentOperator.STARTS_WITH:
            return field_value.startswith(test_value) if field_value else False
        elif operator == SegmentOperator.ENDS_WITH:
            return field_value.endswith(test_value) if field_value else False
        elif operator == SegmentOperator.EXISTS:
            return field_value is not None
        elif operator == SegmentOperator.NOT_EXISTS:
            return field_value is None
        elif operator == SegmentOperator.IN:
            return field_value in test_value
        elif operator == SegmentOperator.NOT_IN:
            return field_value not in test_value
        elif operator == SegmentOperator.BETWEEN:
            return test_value[0] <= field_value <= test_value[1]
        else:
            # Default to equality
            return field_value == test_value
    
    async def _evaluate_behavioral_segment(self, segment: Segment) -> List[str]:
        """
        Evaluate a behavioral segment based on user actions
        
        Args:
            segment: The segment to evaluate
            
        Returns:
            List[str]: List of matching user IDs
        """
        # This would normally query an analytics system to find users
        # who have performed specific actions
        # For now, return an empty list as a placeholder
        return []
    
    async def _evaluate_composite_segment(self, segment: Segment) -> List[str]:
        """
        Evaluate a composite segment by combining other segments
        
        Args:
            segment: The segment to evaluate
            
        Returns:
            List[str]: List of matching user IDs
        """
        # Check for composite rule
        if not segment.composite_rule or not segment.composite_rule.segment_ids:
            return []
            
        segment_ids = segment.composite_rule.segment_ids
        operator = segment.composite_rule.operator
        
        # Get user lists from each referenced segment
        user_lists = []
        for seg_id in segment_ids:
            evaluation = await self.evaluate_segment(seg_id, get_matched_users=True)
            user_lists.append(set(evaluation.get("matched_users", [])))
            
        if not user_lists:
            return []
            
        # Apply the composite operator
        if operator == CompositeOperator.UNION:
            # Union - users in any segment
            result = set.union(*user_lists)
        elif operator == CompositeOperator.INTERSECTION:
            # Intersection - users in all segments
            result = set.intersection(*user_lists)
        elif operator == CompositeOperator.DIFFERENCE:
            # Difference - users in first segment but not in others
            if len(user_lists) > 1:
                result = user_lists[0] - set.union(*user_lists[1:])
            else:
                result = user_lists[0]
        else:
            result = set()
            
        return list(result)
    
    async def add_users_to_static_segment(
        self, 
        segment_id: str, 
        user_ids: List[str]
    ) -> Dict:
        """
        Add users to a static segment
        
        Args:
            segment_id: The segment ID
            user_ids: List of user IDs to add
            
        Returns:
            Dict: Result with updated user count
        """
        # Get the segment
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
            
        # Only static segments support direct user addition
        if segment.segment_type != SegmentType.STATIC:
            raise ValueError(
                f"Cannot add users directly to a {segment.segment_type} segment. "
                "Only static segments support this operation."
            )
            
        # Get current user list
        current_users = set(segment.filter_criteria.get("user_ids", []))
        
        # Add new users
        current_users.update(user_ids)
        
        # Update segment
        segment.filter_criteria["user_ids"] = list(current_users)
        segment.user_count = len(current_users)
        segment.updated_at = datetime.now()
        
        # Save changes
        await self.segment_repo.update(segment_id, segment)
        
        audit_log(f"Added {len(user_ids)} users to segment {segment_id}")
        
        return {
            "segment_id": segment_id,
            "added_users": len(user_ids),
            "total_users": len(current_users)
        }
    
    async def remove_users_from_static_segment(
        self, 
        segment_id: str, 
        user_ids: List[str]
    ) -> Dict:
        """
        Remove users from a static segment
        
        Args:
            segment_id: The segment ID
            user_ids: List of user IDs to remove
            
        Returns:
            Dict: Result with updated user count
        """
        # Get the segment
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
            
        # Only static segments support direct user removal
        if segment.segment_type != SegmentType.STATIC:
            raise ValueError(
                f"Cannot remove users directly from a {segment.segment_type} segment. "
                "Only static segments support this operation."
            )
            
        # Get current user list
        current_users = set(segment.filter_criteria.get("user_ids", []))
        remove_users = set(user_ids)
        
        # Remove users
        updated_users = current_users - remove_users
        
        # Update segment
        segment.filter_criteria["user_ids"] = list(updated_users)
        segment.user_count = len(updated_users)
        segment.updated_at = datetime.now()
        
        # Save changes
        await self.segment_repo.update(segment_id, segment)
        
        audit_log(f"Removed {len(user_ids)} users from segment {segment_id}")
        
        return {
            "segment_id": segment_id,
            "removed_users": len(user_ids),
            "total_users": len(updated_users)
        }
        
    async def get_segment_stats(self, segment_id: str) -> Dict:
        """
        Get statistics for a segment
        
        Args:
            segment_id: The segment ID
            
        Returns:
            Dict: Segment statistics
        """
        # Get segment
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        
        # Get campaigns using this segment
        campaigns = await self.campaign_repo.get_by_segment(segment_id)
        
        # Calculate growth rate - compare current user count with count from a week ago
        # In a real implementation, you'd query historical data
        growth_rate = 0.0  # Placeholder
        
        return {
            "segment_id": segment_id,
            "user_count": segment.user_count,
            "campaigns_using": len(campaigns),
            "user_growth_rate": growth_rate,
            "last_updated": segment.updated_at
        }
        
    async def search_segments(self, query: str, limit: int = 10) -> List[Segment]:
        """
        Search for segments by name or description
        
        Args:
            query: The search query
            limit: Maximum number of results
            
        Returns:
            List[Segment]: Matching segments
        """
        return await self.segment_repo.search_segments(query, limit)
