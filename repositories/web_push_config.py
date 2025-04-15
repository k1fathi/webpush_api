from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.domain.web_push_config import WebPushConfigModel
from models.schemas.web_push_config import WebPushConfigCreate, WebPushConfig, WebPushConfigUpdate

class WebPushConfigRepository:
    """Repository for web push configuration operations"""
    
    def __init__(self, db: Optional[Session] = None):
        self.db = db
    
    def create(self, config: WebPushConfigCreate) -> WebPushConfig:
        """Create a new web push configuration"""
        db_config = WebPushConfigModel(
            name=config.name,
            description=config.description,
            default_icon_url=config.default_icon_url,
            default_badge_url=config.default_badge_url,
            default_image_url=config.default_image_url,
            default_time_to_live=config.default_time_to_live,
            default_vibrate_pattern=config.default_vibrate_pattern,
            default_require_interaction=config.default_require_interaction,
            default_silent=config.default_silent,
            default_renotify=config.default_renotify,
            default_priority=config.default_priority,
            prompt_strategy=config.prompt_strategy,
            prompt_delay_seconds=config.prompt_delay_seconds,
            min_visits_before_prompt=config.min_visits_before_prompt,
            service_worker_path=config.service_worker_path,
            service_worker_scope=config.service_worker_scope,
            vapid_public_key=config.vapid_public_key,
            vapid_private_key=config.vapid_private_key,
            vapid_subject=config.vapid_subject,
            custom_prompt_options=config.custom_prompt_options,
            custom_styles=config.custom_styles,
            is_active=config.is_active,
            is_default=config.is_default,
            created_by=config.created_by
        )
        
        # If this is set as the default config, unset any existing defaults
        if db_config.is_default:
            existing_defaults = (
                self.db.query(WebPushConfigModel)
                .filter(WebPushConfigModel.is_default == True)
                .all()
            )
            for existing in existing_defaults:
                existing.is_default = False
        
        self.db.add(db_config)
        self.db.commit()
        self.db.refresh(db_config)
        
        return WebPushConfig.from_orm(db_config)
    
    def get(self, config_id: Union[UUID, str]) -> Optional[WebPushConfig]:
        """Get a web push configuration by ID"""
        if isinstance(config_id, str):
            config_id = UUID(config_id)
        
        db_config = self.db.query(WebPushConfigModel).filter(WebPushConfigModel.id == config_id).first()
        if db_config is None:
            return None
        
        return WebPushConfig.from_orm(db_config)
    
    def get_default(self) -> Optional[WebPushConfig]:
        """Get the default web push configuration"""
        db_config = self.db.query(WebPushConfigModel).filter(WebPushConfigModel.is_default == True).first()
        if db_config is None:
            return None
        
        return WebPushConfig.from_orm(db_config)
    
    def update(self, config_id: Union[UUID, str], config: WebPushConfigUpdate) -> Optional[WebPushConfig]:
        """Update an existing web push configuration"""
        if isinstance(config_id, str):
            config_id = UUID(config_id)
        
        db_config = self.db.query(WebPushConfigModel).filter(WebPushConfigModel.id == config_id).first()
        if db_config is None:
            return None
        
        # Update fields
        update_data = config.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_config, key, value)
        
        # If this is set as the default config, unset any existing defaults
        if update_data.get('is_default', False) and db_config.is_default:
            existing_defaults = (
                self.db.query(WebPushConfigModel)
                .filter(WebPushConfigModel.is_default == True)
                .filter(WebPushConfigModel.id != config_id)
                .all()
            )
            for existing in existing_defaults:
                existing.is_default = False
        
        self.db.commit()
        self.db.refresh(db_config)
        
        return WebPushConfig.from_orm(db_config)
    
    def delete(self, config_id: Union[UUID, str]) -> bool:
        """Delete a web push configuration"""
        if isinstance(config_id, str):
            config_id = UUID(config_id)
        
        db_config = self.db.query(WebPushConfigModel).filter(WebPushConfigModel.id == config_id).first()
        if db_config is None:
            return False
        
        # Don't allow deleting the default configuration
        if db_config.is_default:
            return False
        
        self.db.delete(db_config)
        self.db.commit()
        
        return True
    
    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[WebPushConfig]:
        """List web push configurations with optional filtering"""
        query = self.db.query(WebPushConfigModel)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(WebPushConfigModel, key):
                    query = query.filter(getattr(WebPushConfigModel, key) == value)
        
        # Apply pagination
        db_configs = query.offset(skip).limit(limit).all()
        
        return [WebPushConfig.from_orm(config) for config in db_configs]
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count web push configurations with optional filtering"""
        query = self.db.query(WebPushConfigModel)
        
        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                if hasattr(WebPushConfigModel, key):
                    query = query.filter(getattr(WebPushConfigModel, key) == value)
        
        return query.count()
    
    def set_as_default(self, config_id: Union[UUID, str]) -> bool:
        """Set a configuration as the default"""
        if isinstance(config_id, str):
            config_id = UUID(config_id)
        
        db_config = self.db.query(WebPushConfigModel).filter(WebPushConfigModel.id == config_id).first()
        if db_config is None:
            return False
        
        # Unset any existing defaults
        existing_defaults = (
            self.db.query(WebPushConfigModel)
            .filter(WebPushConfigModel.is_default == True)
            .all()
        )
        for existing in existing_defaults:
            existing.is_default = False
        
        # Set this config as default
        db_config.is_default = True
        
        self.db.commit()
        return True