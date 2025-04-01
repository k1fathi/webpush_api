import logging
from datetime import datetime, timedelta
from typing import List, Optional

from core.celery_app import celery_app
from repositories.user import UserRepository
from repositories.cdp_integration import CdpIntegrationRepository
from services.cdp import CdpService
from models.cdp_integration import CdpSyncStatus

logger = logging.getLogger(__name__)

@celery_app.task
def sync_user_with_cdp(user_id: str) -> bool:
    """
    Sync a user's data with the CDP
    
    Args:
        user_id: The ID of the user to sync
        
    Returns:
        bool: Success status
    """
    logger.info(f"Syncing user {user_id} with CDP")
    
    cdp_service = CdpService()
    
    if not cdp_service.is_enabled():
        logger.warning("CDP integration not enabled, skipping sync")
        return False
    
    try:
        # Sync the user data
        result = cdp_service.sync_user_data(user_id)
        return result
    except Exception as e:
        logger.error(f"Error syncing user {user_id} with CDP: {str(e)}")
        
        # Mark the sync as failed in the integration repository
        try:
            cdp_repo = CdpIntegrationRepository()
            integration = cdp_repo.get_by_user_id(user_id)
            if integration:
                integration.sync_status = CdpSyncStatus.FAILED
                integration.sync_error = str(e)
                cdp_repo.update(integration.id, integration)
        except Exception as inner_e:
            logger.error(f"Error updating CDP integration status: {str(inner_e)}")
        
        return False
        
@celery_app.task
def sync_all_users_with_cdp() -> dict:
    """
    Sync all users' data with the CDP
    
    Returns:
        dict: Success and failure counts
    """
    logger.info("Starting bulk user sync with CDP")
    
    user_repo = UserRepository()
    cdp_service = CdpService()
    
    if not cdp_service.is_enabled():
        logger.warning("CDP integration not enabled, skipping sync")
        return {"success": 0, "failed": 0, "skipped": 0}
    
    # Get all users
    users = user_repo.get_all()
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    # Process users in batches
    batch_size = 100
    for i in range(0, len(users), batch_size):
        user_batch = users[i:i+batch_size]
        
        for user in user_batch:
            # Queue individual sync tasks
            if user.opted_in:
                sync_user_with_cdp.delay(str(user.id))
                success_count += 1
            else:
                # Skip users who haven't opted in
                skipped_count += 1
    
    logger.info(f"Queued CDP sync for {success_count} users, skipped {skipped_count} users")
    return {
        "success": success_count,
        "failed": failed_count,
        "skipped": skipped_count
    }

@celery_app.task
def sync_inactive_users() -> int:
    """
    Sync users who haven't been synced in the last X days
    
    Returns:
        int: Number of users queued for sync
    """
    logger.info("Syncing inactive users with CDP")
    
    cdp_repo = CdpIntegrationRepository()
    user_repo = UserRepository()
    
    # Get users who haven't been synced in 7 days
    cutoff_date = datetime.now() - timedelta(days=7)
    
    # Get all CDP integrations that need updating
    outdated_integrations = cdp_repo.get_outdated_integrations(cutoff_date)
    
    count = 0
    for integration in outdated_integrations:
        # Check if user still exists and is opted in
        user = user_repo.get(integration.user_id)
        if user and user.opted_in:
            # Queue sync task
            sync_user_with_cdp.delay(str(user.id))
            count += 1
    
    logger.info(f"Queued {count} inactive users for CDP sync")
    return count

@celery_app.task
def retry_failed_cdp_syncs() -> int:
    """
    Retry previously failed CDP syncs
    
    Returns:
        int: Number of syncs retried
    """
    logger.info("Retrying failed CDP syncs")
    
    cdp_repo = CdpIntegrationRepository()
    
    # Get all failed integrations
    failed_integrations = cdp_repo.get_by_status(CdpSyncStatus.FAILED)
    
    count = 0
    for integration in failed_integrations:
        # Queue sync task
        sync_user_with_cdp.delay(str(integration.user_id))
        count += 1
    
    logger.info(f"Queued {count} failed CDP syncs for retry")
    return count

@celery_app.task
def cleanup_stale_cdp_data() -> int:
    """
    Clean up stale CDP integration data for users who have unsubscribed
    
    Returns:
        int: Number of records cleaned up
    """
    logger.info("Cleaning up stale CDP data")
    
    cdp_repo = CdpIntegrationRepository()
    user_repo = UserRepository()
    
    # Get all CDP integrations
    all_integrations = cdp_repo.get_all()
    
    count = 0
    for integration in all_integrations:
        # Check if user still exists and is still subscribed
        user = user_repo.get(integration.user_id)
        if not user or not user.opted_in:
            # Delete the integration
            cdp_repo.delete(integration.id)
            count += 1
    
    logger.info(f"Cleaned up {count} stale CDP integration records")
    return count
