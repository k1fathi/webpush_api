import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Any, Tuple

logger = logging.getLogger(__name__)

# Define enum types here instead of importing them
class SegmentType:
    STATIC = "static"
    DYNAMIC = "dynamic"
    BEHAVIOR = "behavior"
    COMPOSITE = "composite"

class SegmentOperator:
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    IN = "in"
    NOT_IN = "not_in"

class CompositeOperator:
    AND = "and"
    OR = "or"

# Basic Segment model
class Segment:
    def __init__(self, id, name, segment_type, filter_criteria=None):
        self.id = id
        self.name = name
        self.segment_type = segment_type
        self.filter_criteria = filter_criteria or {}

from repositories.segment import SegmentRepository
from repositories.user import UserRepository
from utils.audit import audit_log
from utils.query_builder import build_segment_query
from models.schemas.segment import SegmentRule, Segment, SegmentType, Criterion, CompositeRule, CompositeOperator

class SegmentExecutionService:
    """
    Service for executing segment queries and evaluations
    Implements the core logic for the segment_management_flow.mmd
    """
    
    def __init__(self):
        self.segment_repo = SegmentRepository()
        self.user_repo = UserRepository()
    
    async def execute_segment_query(
        self,
        segment_id: str,
        get_user_ids: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a segment query to find matching users
        
        Args:
            segment_id: ID of the segment to execute
            get_user_ids: Whether to return user IDs in result
            
        Returns:
            Dict with execution results
        """
        segment = await self.segment_repo.get(segment_id)
        if not segment:
            raise ValueError(f"Segment with ID {segment_id} not found")
        
        execution_start = datetime.now()
        logger.info(f"Executing segment {segment_id} - {segment.name}")
        
        try:
            user_ids = await self._get_matching_users(segment)
            
            # Update segment metadata
            segment.user_count = len(user_ids)
            segment.last_evaluated_at = datetime.now()
            await self.segment_repo.update(segment_id, segment)
            
            execution_time = (datetime.now() - execution_start).total_seconds()
            
            # Audit log the execution
            audit_log(
                message=f"Executed segment {segment.name} with {len(user_ids)} matching users",
                resource_type="segment", 
                resource_id=segment_id,
                action_type="execute",
                metadata={
                    "execution_time_seconds": execution_time,
                    "user_count": len(user_ids)
                }
            )
            
            result = {
                "segment_id": segment_id,
                "name": segment.name,
                "user_count": len(user_ids),
                "execution_time_seconds": execution_time,
                "execution_timestamp": datetime.now().isoformat()
            }
            
            # Include user IDs if requested
            if get_user_ids:
                result["user_ids"] = user_ids
                
            return result
            
        except Exception as e:
            logger.error(f"Error executing segment {segment_id}: {str(e)}")
            
            # Log the execution error
            audit_log(
                message=f"Segment execution failed: {segment.name}",
                resource_type="segment",
                resource_id=segment_id,
                action_type="execute_failed",
                metadata={"error": str(e)}
            )
            
            raise
    
    async def _get_matching_users(self, segment: Segment) -> List[str]:
        """
        Get users that match segment criteria
        
        Args:
            segment: The segment to evaluate
            
        Returns:
            List of matching user IDs
        """
        if segment.segment_type == SegmentType.STATIC:
            # Return the explicit user list for static segments
            return self._get_static_segment_users(segment)
            
        elif segment.segment_type == SegmentType.DYNAMIC:
            # Execute filter criteria for dynamic segments
            return await self._get_dynamic_segment_users(segment)
            
        elif segment.segment_type == SegmentType.BEHAVIORAL:
            # Execute behavior-based criteria
            return await self._get_behavioral_segment_users(segment)
            
        elif segment.segment_type == SegmentType.COMPOSITE:
            # Combine multiple segments
            return await self._get_composite_segment_users(segment)
            
        else:
            logger.warning(f"Unknown segment type: {segment.segment_type}")
            return []
    
    def _get_static_segment_users(self, segment: Segment) -> List[str]:
        """
        Get users for a static segment
        
        Args:
            segment: The static segment
            
        Returns:
            List of user IDs
        """
        if (segment.filter_criteria and 
            isinstance(segment.filter_criteria, dict) and
            "user_ids" in segment.filter_criteria):
            return segment.filter_criteria["user_ids"]
        else:
            logger.warning(f"Static segment {segment.id} has no user_ids defined")
            return []
    
    async def _get_dynamic_segment_users(self, segment: Segment) -> List[str]:
        """
        Get users for a dynamic segment based on filter criteria
        
        Args:
            segment: The dynamic segment
            
        Returns:
            List of user IDs
        """
        if not segment.filter_criteria and not segment.rules:
            logger.warning(f"Dynamic segment {segment.id} has no filter criteria or rules")
            return []
            
        matching_users = []
        
        # Use rules if provided (more structured approach)
        if segment.rules:
            matching_users = await self._execute_segment_rules(segment.rules)
        # Otherwise use filter_criteria (simple approach)
        elif segment.filter_criteria:
            matching_users = await self._execute_filter_criteria(segment.filter_criteria)
            
        return matching_users
    
    async def _execute_filter_criteria(self, criteria: Dict[str, Any]) -> List[str]:
        """
        Execute filter criteria to find matching users
        
        Args:
            criteria: Filter criteria dictionary
            
        Returns:
            List of matching user IDs
        """
        # This would normally build and execute an actual database query
        # For this implementation, we'll use a simplified approach
        
        # Build an SQL query from criteria
        query, params = build_segment_query(criteria, table_name="users")
        logger.debug(f"Generated query: {query}, params: {params}")
        
        # Execute query using repository
        users = await self.user_repo.execute_raw_query(query, params)
        return [str(user.id) for user in users]
    
    async def _execute_segment_rules(self, rules: List[SegmentRule]) -> List[str]:
        """
        Execute structured segment rules to find matching users
        
        Args:
            rules: List of segment rules to execute
            
        Returns:
            List of matching user IDs
        """
        # For multiple rules, we need to handle them based on their operator
        # This is a placeholder for what would be a more complex implementation
        all_matching_users = []
        
        for rule in rules:
            rule_users = await self._execute_single_rule(rule)
            all_matching_users.extend(rule_users)
            
        # Remove duplicates if multiple rules matched the same users
        return list(set(all_matching_users))
    
    async def _execute_single_rule(self, rule: SegmentRule) -> List[str]:
        """
        Execute a single segment rule
        
        Args:
            rule: The rule to execute
            
        Returns:
            List of matching user IDs
        """
        # Convert rule to criteria for execution
        criteria = {}
        
        for criterion in rule.criteria:
            criteria[criterion.field] = criterion.value
            if criterion.operator != SegmentOperator.EQUALS:
                # Include the operator if it's not the default
                criteria["operator"] = criterion.operator
                
        return await self._execute_filter_criteria(criteria)
    
    async def _get_behavioral_segment_users(self, segment: Segment) -> List[str]:
        """
        Get users for a behavioral segment based on their past actions
        
        Args:
            segment: The behavioral segment
            
        Returns:
            List of user IDs
        """
        # In a real implementation, this would query analytics or event data
        # to find users who have performed specific actions
        
        # This is a placeholder implementation
        logger.info(f"Executing behavioral segment {segment.id}")
        
        # For now, we'll just return an empty list
        return []
    
    async def _get_composite_segment_users(self, segment: Segment) -> List[str]:
        """
        Get users for a composite segment by combining other segments
        
        Args:
            segment: The composite segment
            
        Returns:
            List of user IDs
        """
        if not segment.composite_rule or not segment.composite_rule.segment_ids:
            logger.warning(f"Composite segment {segment.id} has no segment IDs defined")
            return []
            
        # Get users from all referenced segments
        segment_ids = segment.composite_rule.segment_ids
        operator = segment.composite_rule.operator
        
        # Lists to hold users from each segment
        segment_users = []
        
        for seg_id in segment_ids:
            try:
                # Get the referenced segment
                ref_segment = await self.segment_repo.get(seg_id)
                if not ref_segment:
                    logger.warning(f"Referenced segment {seg_id} not found")
                    continue
                
                # Execute the referenced segment to get its users
                users = await self._get_matching_users(ref_segment)
                segment_users.append(set(users))
                
            except Exception as e:
                logger.error(f"Error processing referenced segment {seg_id}: {str(e)}")
                # Continue with other segments even if one fails
        
        if not segment_users:
            logger.warning(f"No valid referenced segments found for composite segment {segment.id}")
            return []
            
        # Apply the composite operator to combine the user lists
        if operator == CompositeOperator.UNION:
            # Union - users in any of the segments
            result = set().union(*segment_users)
            
        elif operator == CompositeOperator.INTERSECTION:
            # Intersection - users in all segments
            result = set.intersection(*segment_users)
            
        elif operator == CompositeOperator.DIFFERENCE:
            # Difference - users in first segment but not in others
            if len(segment_users) > 1:
                result = segment_users[0].difference(*segment_users[1:])
            else:
                result = segment_users[0]
        else:
            logger.warning(f"Unknown composite operator: {operator}")
            result = set()
            
        return list(result)
