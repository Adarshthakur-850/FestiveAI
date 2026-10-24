import json
import uuid
import re
import random
from datetime import date, datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.festival import FestivalDefinition, RegionalObservance, AccountFestivalPreference
from app.models.campaign import PublishingCampaign, GeneratedCreative
from app.schemas.festival import (
    FestivalDefinitionOut,
    UpcomingFestivalOut,
    AccountFestivalPreferenceUpdate,
    CreateCustomEventRequest,
    CreateRandomTestEventRequest,
    CustomEventResponseOut
)
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.calendar_service import CalendarService
from app.services.relevance_service import RelevanceEngine
from app.services.image_gen_service import GreetingCompositor
from app.services.caption_gen_service import CaptionGenerator
from app.services.publishing_service import PublishingService

router = APIRouter(prefix="/calendar", tags=["Festival Calendar & Relevance"])

RANDOM_EVENT_PRESETS = [
    {
        "name": "TechPulse Innovation Day 2026",
        "category": "milestone",
        "description": "Celebrating bold engineering breakthroughs, product milestones, and collective ambition.",
        "greetings": ["Happy Innovation Day", "Celebrating Tech Milestones & Forward Momentum"],
        "themes": ["innovation", "scaling", "breakthroughs", "team_culture"]
    },
    {
        "name": "Global Developers & Builders Appreciation",
        "category": "milestone",
        "description": "Honoring the software engineers, designers, and founders building modern digital ecosystems.",
        "greetings": ["Happy Developers Appreciation Day", "Saluting the Builders of Tomorrow"],
        "themes": ["code", "developers", "architecture", "gratitude"]
    },
    {
        "name": "Founder Milestone: 100K Community Milestone",
        "category": "milestone",
        "description": "A celebration of client trust, shared milestones, and customer success.",
        "greetings": ["Cheers to 100K Users", "Celebrating Scale, Community, and Trust"],
        "themes": ["milestone", "community", "scale", "excellence"]
    },
    {
        "name": "Annual Spring Technology Renaissance",
        "category": "cultural",
        "description": "Welcoming a season of new ideas, creative breakthroughs, and high growth.",
        "greetings": ["Happy Spring Renaissance", "Embracing Fresh Horizons & Visionary Ideas"],
        "themes": ["spring", "renewal", "creativity", "progress"]
    },
    {
        "name": "Enterprise Excellence & Impact Summit",
        "category": "corporate",
        "description": "Recognizing strategic leadership, partnership growth, and resilience.",
        "greetings": ["Celebrating Enterprise Excellence", "Here's to Strategic Leadership and Growth"],
        "themes": ["leadership", "partnerships", "strategy", "impact"]
    }
]

def _slugify(text: str) -> str:
    s = re.sub(r'[^a-zA-Z0-9\s_-]', '', text).strip().lower()
    return re.sub(r'[\s_-]+', '_', s)

@router.get("/festivals", response_model=ResponseBase[List[FestivalDefinitionOut]])
def list_all_festivals(db: Session = Depends(get_db)):
    festivals = db.query(FestivalDefinition).all()
    results = []
    for f in festivals:
        results.append(FestivalDefinitionOut(
            id=f.id,
            slug=f.slug,
            name=f.name,
            category=f.category,
            calculation_type=f.calculation_type,
            description=f.description,
            traditional_themes=json.loads(f.traditional_themes or "[]"),
            default_greeting_phrases=json.loads(f.default_greeting_phrases or "[]"),
            observances=[obs for obs in f.observances]
        ))
    return ResponseBase(success=True, data=results)

@router.get("/upcoming", response_model=ResponseBase[List[UpcomingFestivalOut]])
def get_upcoming_festivals(
    account_id: Optional[str] = Query(None),
    days_ahead: int = Query(120),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    upcoming_data = CalendarService.get_upcoming_festivals(db, days_ahead=days_ahead)
    results = []

    account = None
    if account_id:
        account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        account = db.query(SocialAccount).filter_by(organization_id=user.organization_id, is_connected=True).first()

    for item in upcoming_data:
        relevance = 0.80
        is_enabled = True
        campaign_id = None
        status = "unscheduled"

        if account:
            pref = db.query(AccountFestivalPreference).filter_by(
                social_account_id=account.id,
                festival_id=item["festival_id"]
            ).first()
            if pref:
                relevance = pref.relevance_score
                is_enabled = pref.is_enabled

            # Check campaign status
            camp = db.query(PublishingCampaign).filter_by(
                social_account_id=account.id,
                festival_id=item["festival_id"],
                year=item["year"]
            ).first()
            if camp:
                campaign_id = camp.id
                status = camp.status

        results.append(UpcomingFestivalOut(
            festival_id=item["festival_id"],
            slug=item["slug"],
            name=item["name"],
            category=item["category"],
            observed_date=item["observed_date"],
            year=item["year"],
            days_until=item["days_until"],
            relevance_score=relevance,
            is_enabled=is_enabled,
            status=status,
            campaign_id=campaign_id,
            verification_source=item["verification_source"]
        ))

    return ResponseBase(success=True, data=results)

@router.put("/accounts/{account_id}/festivals/{festival_id}", response_model=ResponseBase[bool])
def update_account_festival_preference(
    account_id: str,
    festival_id: str,
    payload: AccountFestivalPreferenceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    pref = db.query(AccountFestivalPreference).filter_by(
        social_account_id=account.id,
        festival_id=festival_id
    ).first()

    if not pref:
        pref = AccountFestivalPreference(
            social_account_id=account.id,
            festival_id=festival_id,
            is_enabled=payload.is_enabled if payload.is_enabled is not None else True,
            relevance_score=payload.relevance_score if payload.relevance_score is not None else 0.7
        )
        db.add(pref)
    else:
        if payload.is_enabled is not None:
            pref.is_enabled = payload.is_enabled
        if payload.relevance_score is not None:
            pref.relevance_score = payload.relevance_score
        if payload.custom_lead_days is not None:
            pref.custom_lead_days = payload.custom_lead_days
        if payload.custom_greeting_text is not None:
            pref.custom_greeting_text = payload.custom_greeting_text
        if payload.custom_visual_theme is not None:
            pref.custom_visual_theme = payload.custom_visual_theme

    db.commit()
    return ResponseBase(success=True, message="Festival preference updated successfully", data=True)

@router.post("/custom-event", response_model=ResponseBase[CustomEventResponseOut])
def create_custom_event(
    payload: CreateCustomEventRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    event_name = (payload.name or "").strip()
    if not event_name:
        raise HTTPException(status_code=400, detail="Event name is required")

    # Generate unique slug
    base_slug = _slugify(event_name)[:40] or "custom_event"
    unique_suffix = uuid.uuid4().hex[:6]
    slug = f"custom_{base_slug}_{unique_suffix}"

    # Determine date
    obs_date = payload.observed_date or date.today()
    year = obs_date.year

    # Create festival definition
    themes = payload.traditional_themes or ["celebration", "milestone", "innovation", "gratitude"]
    greetings = payload.default_greeting_phrases or [f"Celebrating {event_name}!"]

    festival = FestivalDefinition(
        slug=slug,
        name=event_name,
        category=payload.category or "milestone",
        calculation_type="custom_host_event",
        description=payload.description or f"Custom host-created event: {event_name}",
        traditional_themes=json.dumps(themes),
        default_greeting_phrases=json.dumps(greetings)
    )
    db.add(festival)
    db.flush()

    # Create regional observance
    observance = RegionalObservance(
        festival_id=festival.id,
        year=year,
        observed_date=obs_date,
        region_code="IN",
        verification_source="Host Custom Event Verification",
        is_verified=True
    )
    db.add(observance)

    # Find account if specified or default
    account = None
    if payload.social_account_id:
        account = db.query(SocialAccount).filter_by(id=payload.social_account_id, organization_id=user.organization_id).first()
    if not account:
        account = db.query(SocialAccount).filter_by(organization_id=user.organization_id, is_connected=True).first()

    if account:
        pref = AccountFestivalPreference(
            social_account_id=account.id,
            festival_id=festival.id,
            is_enabled=True,
            relevance_score=0.98
        )
        db.add(pref)

    db.commit()

    # Auto-publish immediately if requested
    published = False
    platform = None
    platform_post_id = None
    campaign_id = None
    msg = f"Custom event '{event_name}' created successfully!"

    if payload.auto_publish_now and account:
        camp_identifier = f"CAMP-{account.platform.upper()}-{account.id[:8].upper()}-{festival.slug.upper()[:12]}-{year}"
        publish_dt = CalendarService.calculate_publish_datetime(obs_date, "09:00:00", "Asia/Kolkata")

        style_profile = account.style_profile
        effective_pillar = "thought_leadership"

        local_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
            festival_slug=festival.slug,
            greeting_text=greetings[0],
            style_profile=style_profile,
            post_pillar=effective_pillar
        )

        caption, hashtags = CaptionGenerator.generate_caption(
            festival=festival,
            style_profile=style_profile,
            account_name=account.display_name or account.account_username,
            post_pillar=effective_pillar
        )

        campaign = PublishingCampaign(
            social_account_id=account.id,
            festival_id=festival.id,
            year=year,
            campaign_identifier=camp_identifier,
            scheduled_publish_time=publish_dt,
            status="approved",
            post_pillar=effective_pillar,
            is_approved=True
        )
        db.add(campaign)
        db.flush()

        creative = GeneratedCreative(
            campaign_id=campaign.id,
            version=1,
            image_url=img_url,
            local_image_path=local_path,
            caption_text=caption,
            hashtags=json.dumps(hashtags),
            width=1080 if account.platform == "instagram" else 1200,
            height=1080 if account.platform == "instagram" else 628,
            aspect_ratio="1:1" if account.platform == "instagram" else "1.91:1",
            post_pillar=effective_pillar,
            model_used="Pillow Compositor v1.0",
            prompt_used=f"Custom celebration image for {event_name}",
            quality_score=0.95,
            quality_checks=json.dumps({"contrast": "passed", "brand_watermark": "verified"}),
            is_selected=True
        )
        db.add(creative)
        db.commit()

        # Execute publish now
        publish_res = PublishingService.publish_campaign(db, campaign)
        campaign_id = campaign.id
        platform = account.platform
        if publish_res.get("success"):
            published = True
            platform_post_id = publish_res.get("platform_post_id")
            msg = f"Custom event '{event_name}' synthesized and published automatically to @{account.account_username} on {account.platform.upper()}! (Platform Post ID: {platform_post_id})"
        else:
            msg = f"Custom event created and creative generated, but publish attempt reported: {publish_res.get('error')}"

    return ResponseBase(
        success=True,
        message=msg,
        data=CustomEventResponseOut(
            festival_id=festival.id,
            slug=festival.slug,
            name=festival.name,
            category=festival.category,
            observed_date=obs_date,
            year=year,
            published=published,
            platform=platform,
            platform_post_id=platform_post_id,
            campaign_id=campaign_id,
            message=msg
        )
    )

@router.post("/random-test-event", response_model=ResponseBase[CustomEventResponseOut])
def create_random_test_event(
    payload: CreateRandomTestEventRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    preset = random.choice(RANDOM_EVENT_PRESETS)
    custom_req = CreateCustomEventRequest(
        name=preset["name"],
        category=preset["category"],
        observed_date=date.today(),
        description=preset["description"],
        traditional_themes=preset["themes"],
        default_greeting_phrases=preset["greetings"],
        social_account_id=payload.social_account_id,
        auto_publish_now=payload.auto_publish_now
    )
    return create_custom_event(custom_req, db, user)
