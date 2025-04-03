from enum import Enum

class TemplateCategory(str, Enum):
    """Categories for campaign templates"""
    PROMOTIONAL = "promotional"
    TRANSACTIONAL = "transactional"
    INFORMATIONAL = "informational"
    REMINDER = "reminder"
    SURVEY = "survey"
    
class TemplateStatus(str, Enum):
    """Status values for templates"""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DEPRECATED = "deprecated"
