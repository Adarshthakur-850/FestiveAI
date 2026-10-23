from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class GeneratedCreativeOut(BaseModel):
    id: str
    campaign_id: str
    version: int
    image_url: str
    local_image_path: str
    caption_text: str
    hashtags: List[str] = []
    width: int
    height: int
    aspect_ratio: str
    post_pillar: Optional[str] = "festive_greeting"
    model_used: str
    prompt_used: Optional[str] = None
    quality_score: float
    quality_checks: Dict[str, Any] = {}
    is_selected: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PublishingAttemptOut(BaseModel):
    id: str
    campaign_id: str
    attempt_number: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    status: str
    platform_post_id: Optional[str] = None
    platform_response: Dict[str, Any] = {}
    error_code: Optional[str] = None
    error_traceback: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class PublishingCampaignOut(BaseModel):
    id: str
    social_account_id: str
    festival_id: str
    festival_name: Optional[str] = None
    festival_slug: Optional[str] = None
    platform: Optional[str] = None
    account_username: Optional[str] = None
    year: int
    campaign_identifier: str
    scheduled_publish_time: datetime
    actual_publish_time: Optional[datetime] = None
    status: str
    post_pillar: Optional[str] = "festive_greeting"
    error_message: Optional[str] = None
    retry_count: int
    is_approved: bool
    created_at: datetime
    updated_at: datetime
    active_creative: Optional[GeneratedCreativeOut] = None
    creatives: List[GeneratedCreativeOut] = []
    attempts: List[PublishingAttemptOut] = []
    model_config = ConfigDict(from_attributes=True)

class GenerateCampaignRequest(BaseModel):
    social_account_id: str
    festival_slug: str
    year: int
    post_pillar: Optional[str] = None  # None = auto-detect based on host persona, or explicit pillar
    custom_prompt_instructions: Optional[str] = None
    force_regenerate: bool = False

class UpdateCampaignCreativeRequest(BaseModel):
    caption_text: Optional[str] = None
    hashtags: Optional[List[str]] = None
    scheduled_publish_time: Optional[datetime] = None

class PreviewCompositeRequest(BaseModel):
    social_account_id: str
    festival_slug: str
    greeting_text: str
    brand_name: Optional[str] = None
    primary_color: str = "#1E3A8A"
    accent_color: str = "#D97706"
    theme: str = "elegant_traditional"
