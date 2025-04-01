from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class DatabaseError(CustomException):
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class NotFoundError(CustomException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ValidationError(CustomException):
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

class AuthenticationError(CustomException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class PermissionDeniedError(CustomException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class DuplicateError(CustomException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class WebPushError(CustomException):
    def __init__(self, detail: str = "WebPush notification failed"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class IntegrationError(CustomException):
    def __init__(self, detail: str = "Integration error occurred"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

# Usage examples in comments:
"""
# Database error
raise DatabaseError("Failed to connect to database")

# Not found error
raise NotFoundError("User not found")

# Authentication error
raise AuthenticationError("Invalid credentials")

# Permission error
raise PermissionDeniedError("User does not have required permissions")

# Validation error
raise ValidationError("Invalid input data")

# Duplicate error
raise DuplicateError("Email already registered")

# WebPush error
raise WebPushError("Failed to send notification")

# Integration error
raise IntegrationError("CDP integration failed")
"""
