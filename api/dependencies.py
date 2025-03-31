from fastapi import Depends, HTTPException
from core.permissions import check_permission, is_admin
from typing import List

def verify_permissions(required_permissions: List[str] = None):
    async def permission_checker(current_user = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(status_code=401, detail="Not authenticated")
            
        # Admin users bypass all permission checks
        if is_admin(current_user):
            return current_user
            
        if required_permissions and not check_permission(current_user, required_permissions):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to perform this action"
            )
        
        return current_user
    return permission_checker
