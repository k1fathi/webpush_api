from typing import Dict, Any, Optional

from fastapi import APIRouter, Depends, Request, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.security import APIKeyCookie

from services.external_auth import ExternalAuthService
from models.schemas.notification import DeliveryStatus
from services.notification import NotificationService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/embed/authenticate")
async def authenticate_external_app(
    request: Request,
    token: str,
    signature: str,
    timestamp: str,
    redirect_url: Optional[str] = None,
    auth_service: ExternalAuthService = Depends()
):
    """
    Authenticate a user from an external application
    
    This endpoint validates the external token, creates a session,
    and redirects to the dashboard or a specified URL
    """
    # Verify that request comes from an allowed external domain
    if not auth_service.verify_external_request(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin"
        )
    
    # Validate the token and get user data
    is_valid, customer_id = auth_service.validate_external_token(token, signature, timestamp)
    
    if not is_valid or not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication parameters"
        )
    
    # Get the user associated with this customer ID
    user = await auth_service.get_user_from_external_params({
        "token": token,
        "signature": signature,
        "timestamp": timestamp
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create an access token for internal use
    access_token = auth_service.create_access_token(
        data={"sub": user["id"], "customer_id": customer_id}
    )
    
    response = JSONResponse({
        "access_token": access_token,
        "token_type": "bearer",
        "customer_id": customer_id
    })
    
    # Set cookie for session management
    cookie_name = "webpush_session"
    cookie_value = access_token
    cookie_max_age = 1800  # 30 minutes
    
    response.set_cookie(
        key=cookie_name,
        value=cookie_value,
        max_age=cookie_max_age,
        httponly=True,
        samesite="none",  # Allow cross-site cookies for iframe
        secure=True       # Require HTTPS
    )
    
    return response

@router.get("/embed/dashboard", response_class=HTMLResponse)
async def embedded_dashboard(
    request: Request,
    customer_id: str,
    auth_service: ExternalAuthService = Depends()
):
    """
    Embedded dashboard for external applications
    
    This endpoint returns an HTML page that can be embedded in an iframe
    """
    # Verify session cookie or query parameters
    # This is a simplified example
    is_authenticated = True  # In real life, verify the token from cookie/params
    
    if not is_authenticated:
        return templates.TemplateResponse(
            "unauthorized.html", 
            {"request": request, "message": "Unauthorized access"}
        )
    
    return templates.TemplateResponse(
        "embedded_dashboard.html", 
        {"request": request, "customer_id": customer_id}
    )

@router.get("/embed/notifications")
async def get_customer_notifications(
    request: Request,
    customer_id: str,
    skip: int = 0,
    limit: int = 20,
    status: Optional[DeliveryStatus] = None,
    notification_service: NotificationService = Depends(),
    auth_service: ExternalAuthService = Depends()
):
    """
    Get notifications for a specific customer
    
    This endpoint returns notifications filtered by customer ID
    """
    # Verify the request origin
    if not auth_service.verify_external_request(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request origin"
        )
    
    # Get notifications for the customer
    notifications = await notification_service.get_notifications_by_customer_id(
        customer_id=customer_id,
        skip=skip,
        limit=limit,
        status=status
    )
    
    return {
        "customer_id": customer_id,
        "notifications": notifications,
        "total": len(notifications),
        "skip": skip,
        "limit": limit
    }
