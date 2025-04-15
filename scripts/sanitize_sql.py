import re
import logging
from typing import List, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("sql_sanitizer")

class SQLSanitizer:
    """
    A utility class to sanitize SQL queries and prevent SQL injection attacks.
    """
    
    # Patterns that might indicate an SQL injection attempt
    DANGEROUS_PATTERNS = [
        r';\s*DROP\s+',
        r';\s*DELETE\s+',
        r';\s*UPDATE\s+',
        r';\s*INSERT\s+',
        r';\s*ALTER\s+',
        r';\s*CREATE\s+',
        r';\s*TRUNCATE\s+',
        r'--',
        r'/\*.*\*/',
        r'EXEC\s*\(',
        r'EXECUTE\s*\(',
        r'UNION\s+SELECT',
        r'UNION\s+ALL\s+SELECT',
        r'FROM\s+PROGRAM',
        r'INTO\s+OUTFILE',
        r'COPY.*FROM\s+PROGRAM',
    ]
    
    @classmethod
    def is_safe_query(cls, query: str) -> bool:
        """
        Check if a SQL query is safe (doesn't contain injection patterns).
        
        Args:
            query: The SQL query to check
            
        Returns:
            bool: True if the query appears safe, False otherwise
        """
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"Dangerous SQL pattern detected: {pattern}")
                return False
        return True
    
    @classmethod
    def validate_table_name(cls, table_name: str) -> bool:
        """
        Validate that a table name contains only allowed characters.
        
        Args:
            table_name: The table name to validate
            
        Returns:
            bool: True if the table name is valid, False otherwise
        """
        # Table names should only contain alphanumeric chars, underscores and period (for schema)
        return bool(re.match(r'^[a-zA-Z0-9_\.]+$', table_name))
    
    @classmethod
    def sanitize_query(cls, query: str) -> Optional[str]:
        """
        Attempt to sanitize a SQL query by removing potentially dangerous parts.
        
        Args:
            query: The SQL query to sanitize
            
        Returns:
            Optional[str]: The sanitized query, or None if it cannot be sanitized
        """
        if cls.is_safe_query(query):
            return query
            
        # Try to sanitize by removing multiple statements
        sanitized = re.sub(r';.*', ';', query)
        
        # If still unsafe, return None
        if not cls.is_safe_query(sanitized):
            logger.error(f"Could not sanitize SQL query: {query}")
            return None
            
        return sanitized

if __name__ == "__main__":
    # Test the sanitizer
    test_queries = [
        "SELECT * FROM users WHERE id = 1",
        "SELECT * FROM users; DROP TABLE users;",
        "SELECT * FROM users WHERE id = 1; -- Comment",
        "SELECT * FROM users UNION SELECT username, password FROM admin",
        "COPY users FROM PROGRAM 'echo malicious'",
    ]
    
    for query in test_queries:
        is_safe = SQLSanitizer.is_safe_query(query)
        sanitized = SQLSanitizer.sanitize_query(query)
        
        print(f"Query: {query}")
        print(f"Is Safe: {is_safe}")
        print(f"Sanitized: {sanitized}")
        print("---")
