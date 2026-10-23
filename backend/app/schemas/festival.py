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
