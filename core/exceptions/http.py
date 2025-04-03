from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    """
    Exception raised when a requested resource is not found.
    """
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ForbiddenException(HTTPException):
    """
    Exception raised when access to a resource is forbidden.
    """
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class UnauthorizedException(HTTPException):
    """
    Exception raised when authentication is required but not provided or invalid.
    """
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)
