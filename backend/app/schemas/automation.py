from datetime import time, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class AutomationConfigBase(BaseModel):
    mode: str = "autonomous"  # autonomous, approval
    auto_post_pillars: bool = True
    posting_cadence: str = "daily"
    auto_publish_immediate: bool = True
    lead_time_days: int = 7
    target_publish_time: time = time(9, 0, 0)
    timezone: str = "Asia/Kolkata"
    auto_regenerate_on_rejection: bool = True
    max_retry_attempts: int = 3
    notify_email: Optional[str] = None
    notify_on_generation: bool = True
    notify_on_publish: bool = True

class AutomationConfigUpdate(BaseModel):
    mode: Optional[str] = None
    auto_post_pillars: Optional[bool] = None
    posting_cadence: Optional[str] = None
    auto_publish_immediate: Optional[bool] = None
    lead_time_days: Optional[int] = None
    target_publish_time: Optional[time] = None
    timezone: Optional[str] = None
    auto_regenerate_on_rejection: Optional[bool] = None
    max_retry_attempts: Optional[int] = None
    notify_email: Optional[str] = None
    notify_on_generation: Optional[bool] = None
    notify_on_publish: Optional[bool] = None

class AutomationConfigOut(AutomationConfigBase):
    id: str
    social_account_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class DashboardAnalyticsOut(BaseModel):
    total_accounts: int
    connected_accounts: int
    upcoming_festivals_30d: int
    posts_generated: int
    posts_scheduled: int
    posts_published: int
    failed_attempts: int
    autonomous_mode_enabled_count: int
    system_health: str = "HEALTHY"
