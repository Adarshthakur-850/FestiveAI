from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict

class SocialAccountBase(BaseModel):
    platform: str
    account_type: str = "business"
    account_username: str
    display_name: Optional[str] = None
    profile_picture_url: Optional[str] = None

class SocialAccountCreateMock(BaseModel):
    platform: str = "instagram"  # instagram, linkedin
    account_type: str = "business"
    account_username: str = "techpulse_official"
    display_name: str = "TechPulse Innovations"
    brand_name: str = "TechPulse"
    seed_historical_posts: bool = True

class SocialAccountOut(SocialAccountBase):
    id: str
    organization_id: str
    platform_account_id: str
    is_connected: bool
    status: str
    created_at: datetime
    updated_at: datetime
    has_credentials: bool = False
    historical_posts_count: int = 0
    has_style_profile: bool = False
    automation_mode: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class HistoricalPostOut(BaseModel):
    id: str
    platform_post_id: str
    published_at: datetime
    caption: Optional[str] = None
    hashtags: List[str] = []
    media_type: str
    media_url: Optional[str] = None
    local_asset_path: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    detected_festival: Optional[str] = None
    is_festival_greeting: bool = False
    festival_confidence: float = 0.0
    classification_evidence: Dict[str, Any] = {}
    visual_features: Dict[str, Any] = {}
    language: str = "en"
    post_pillar: Optional[str] = "thought_leadership"
    post_archetype: Optional[str] = "Industry Insight"
    model_config = ConfigDict(from_attributes=True)

class HistoricalPostImportItem(BaseModel):
    platform_post_id: str
    published_at: datetime
    caption: Optional[str] = None
    hashtags: List[str] = []
    media_url: Optional[str] = None
    image_width: Optional[int] = None
    image_height: Optional[int] = None
    media_type: str = "IMAGE"

class HistoricalPostImportRequest(BaseModel):
    posts: List[HistoricalPostImportItem]
