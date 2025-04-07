import hmac
import hashlib
import logging
import time
from typing import Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
from urllib.parse import parse_qs, urlparse

import jwt
from fastapi import Request, HTTPException, status

from core.config import settings
from repositories.user import UserRepository

logger = logging.getLogger(__name__)

class ExternalAuthService:
    """Service for handling authentication from external applications"""
    
    def __init__(self):
        self.user_repo = UserRepository()
        
    def verify_external_request(self, request: Request) -> bool:
        """
        Verify that the request comes from an authorized external application
        
        Args:
            request: The incoming request
            
        Returns:
            bool: True if the request is valid
        """
        # Check origin/referer against allowed domains
        origin = request.headers.get("origin") or request.headers.get("referer")
        if not origin:
            logger.warning("External request missing origin/referer header")
            return False
            
        parsed_origin = urlparse(origin)
        domain = f"{parsed_origin.scheme}://{parsed_origin.netloc}"
        
        if not settings.ALLOWED_EXTERNAL_DOMAINS:
            # If no domains are explicitly allowed, reject all external requests
            logger.warning(f"Request from {domain} rejected: no external domains allowed")
            return False
            
        if domain not in settings.ALLOWED_EXTERNAL_DOMAINS and "*" not in settings.ALLOWED_EXTERNAL_DOMAINS:
            logger.warning(f"Request from unauthorized domain: {domain}")
            return False
            
        # Additional validation could be added here
        return True
    
    def validate_external_token(self, token: str, signature: str, timestamp: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the token from an external application
        
        Args:
            token: The authentication token
            signature: The HMAC signature
            timestamp: The request timestamp
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, customer_id)
        """
        # Check if timestamp is recent (within 5 minutes)
        try:
            token_time = int(timestamp)
            current_time = int(time.time())
            if abs(current_time - token_time) > 300:  # 5 minutes
                logger.warning("External token timestamp expired")
                return False, None
        except ValueError:
            logger.error("Invalid timestamp format")
            return False, None
            
        # Validate signature
        msg = f"{token}:{timestamp}"
        expected_signature = hmac.new(
            settings.EXTERNAL_APP_SECRET_KEY.encode(),
            msg.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Invalid external token signature")
            return False, None
            
        # Extract customer ID from token
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            customer_id = payload.get("sub")
            return True, customer_id
        except jwt.PyJWTError as e:
            logger.error(f"JWT token validation error: {str(e)}")
            return False, None
    
    async def get_user_from_external_params(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get a user based on external authentication parameters
        
        Args:
            params: Query parameters from external request
            
        Returns:
            Optional[Dict[str, Any]]: User data if authenticated
        """
        token = params.get("token")
        signature = params.get("signature")
        timestamp = params.get("timestamp")
        
        if not all([token, signature, timestamp]):
            logger.warning("Missing required authentication parameters")
            return None
            
        is_valid, customer_id = self.validate_external_token(token, signature, timestamp)
        if not is_valid or not customer_id:
            return None
            
        # Find user associated with the customer ID
        # This assumes your User model has a customer_id field
        # If not, you'll need to adapt this logic
        user = await self.user_repo.get_by_customer_id(customer_id)
        if not user:
            logger.warning(f"No user found for customer ID: {customer_id}")
            return None
            
        return {
            "id": user.id,
            "email": user.email,
            "is_active": user.is_active,
            "customer_id": customer_id,
            "roles": [role.name for role in user.roles] if hasattr(user, "roles") else [],
        }
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT access token for authenticated sessions
        
        Args:
            data: Data to include in the token
            
        Returns:
            str: The encoded JWT token
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        
        return jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
