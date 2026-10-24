from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class RegionalObservanceOut(BaseModel):
    id: str
    year: int
    observed_date: date
    region_code: str
    verification_source: str
    is_verified: bool
    model_config = ConfigDict(from_attributes=True)

class FestivalDefinitionOut(BaseModel):
    id: str
    slug: str
    name: str
    category: str
    calculation_type: str
    description: Optional[str] = None
    traditional_themes: List[str] = []
    default_greeting_phrases: List[str] = []
    observances: List[RegionalObservanceOut] = []
    model_config = ConfigDict(from_attributes=True)

class UpcomingFestivalOut(BaseModel):
    festival_id: str
    slug: str
    name: str
    category: str
    observed_date: date
    year: int
    days_until: int
    relevance_score: float
    is_enabled: bool
    status: str  # unscheduled, generating, scheduled, published
    campaign_id: Optional[str] = None
    verification_source: str

class AccountFestivalPreferenceUpdate(BaseModel):
    is_enabled: Optional[bool] = None
    relevance_score: Optional[float] = None
    custom_lead_days: Optional[int] = None
    custom_greeting_text: Optional[str] = None
    custom_visual_theme: Optional[str] = None

class CreateCustomEventRequest(BaseModel):
    name: str
    category: Optional[str] = "milestone"
    observed_date: Optional[date] = None
    description: Optional[str] = None
    traditional_themes: Optional[List[str]] = None
    default_greeting_phrases: Optional[List[str]] = None
    social_account_id: Optional[str] = None
    auto_publish_now: bool = False

class CreateRandomTestEventRequest(BaseModel):
    social_account_id: Optional[str] = None
    auto_publish_now: bool = True
    event_theme: Optional[str] = None

class CustomEventResponseOut(BaseModel):
    festival_id: str
    slug: str
    name: str
    category: str
    observed_date: date
    year: int
    published: bool
    platform: Optional[str] = None
    platform_post_id: Optional[str] = None
    campaign_id: Optional[str] = None
    message: str
