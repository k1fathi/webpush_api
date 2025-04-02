from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import and_, or_, not_, column, text
from sqlalchemy.sql.expression import BinaryExpression, ClauseElement
from models.segment import SegmentOperator

def build_segment_query(
    criteria: Dict[str, Any], 
    table_name: str = "users"
) -> Tuple[str, Dict[str, Any]]:
    """
    Build a SQL query from segment criteria
    
    Args:
        criteria: Filter criteria
        table_name: The table to query
        
    Returns:
        Tuple[str, Dict]: SQL query string and parameters
    """
    conditions = []
    parameters = {}
    
    for field, value in criteria.items():
        # Skip special fields
        if field in ["operator", "rules"]:
            continue
            
        # Handle nested fields (e.g., custom_attributes.country)
        column_ref = field
        if "." in field:
            parts = field.split(".")
            if parts[0] == "custom_attributes":
                # Use JSONB for PostgreSQL
                column_ref = f"custom_attributes ->> '{parts[1]}'"
        
        # Handle operator if present
        operator = criteria.get("operator", "equals")
        condition, param = build_condition(column_ref, value, operator, len(parameters))
        conditions.append(condition)
        parameters.update(param)
    
    # Combine all conditions
    if conditions:
        where_clause = " AND ".join(conditions)
    else:
        where_clause = "TRUE"
    
    # Build the final query
    query = f"SELECT id FROM {table_name} WHERE {where_clause}"
    return query, parameters

def build_condition(
    field: str, 
    value: Any, 
    operator: str, 
    param_idx: int
) -> Tuple[str, Dict[str, Any]]:
    """
    Build an SQL condition from a field, value and operator
    
    Args:
        field: Field name
        value: Value to compare against
        operator: Comparison operator
        param_idx: Parameter index for named parameters
        
    Returns:
        Tuple[str, Dict]: SQL condition string and parameters
    """
    param_name = f"param_{param_idx}"
    params = {param_name: value}
    
    # Map segment operators to SQL operators
    if operator == SegmentOperator.EQUALS:
        return f"{field} = :{param_name}", params
    elif operator == SegmentOperator.NOT_EQUALS:
        return f"{field} != :{param_name}", params
    elif operator == SegmentOperator.GREATER_THAN:
        return f"{field} > :{param_name}", params
    elif operator == SegmentOperator.LESS_THAN:
        return f"{field} < :{param_name}", params
    elif operator == SegmentOperator.CONTAINS:
        params[param_name] = f"%{value}%"
        return f"{field} LIKE :{param_name}", params
    elif operator == SegmentOperator.NOT_CONTAINS:
        params[param_name] = f"%{value}%"
        return f"{field} NOT LIKE :{param_name}", params
    elif operator == SegmentOperator.STARTS_WITH:
        params[param_name] = f"{value}%"
        return f"{field} LIKE :{param_name}", params
    elif operator == SegmentOperator.ENDS_WITH:
        params[param_name] = f"%{value}"
        return f"{field} LIKE :{param_name}", params
    elif operator == SegmentOperator.EXISTS:
        return f"{field} IS NOT NULL", {}
    elif operator == SegmentOperator.NOT_EXISTS:
        return f"{field} IS NULL", {}
    elif operator == SegmentOperator.IN:
        # For array values
        return f"{field} = ANY(:{param_name})", params
    elif operator == SegmentOperator.NOT_IN:
        return f"NOT ({field} = ANY(:{param_name}))", params
    elif operator == SegmentOperator.BETWEEN:
        lower_param = f"param_{param_idx}_lower"
        upper_param = f"param_{param_idx}_upper"
        return f"{field} BETWEEN :{lower_param} AND :{upper_param}", {
            lower_param: value[0], 
            upper_param: value[1]
        }
    else:
        # Default to equality
        return f"{field} = :{param_name}", params
