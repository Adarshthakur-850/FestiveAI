import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.festival import FestivalDefinition, RegionalObservance
from app.models.campaign import PublishingCampaign, GeneratedCreative, PublishingAttempt
from app.schemas.campaign import (
    PublishingCampaignOut,
    GeneratedCreativeOut,
    PublishingAttemptOut,
    GenerateCampaignRequest,
    UpdateCampaignCreativeRequest
)
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.calendar_service import CalendarService
from app.services.image_gen_service import GreetingCompositor
from app.services.caption_gen_service import CaptionGenerator
from app.services.publishing_service import PublishingService

router = APIRouter(prefix="/campaigns", tags=["Content Studio & Campaigns"])

def map_campaign_to_dto(camp: PublishingCampaign) -> PublishingCampaignOut:
    creatives_dto = []
    active_creative_dto = None

    for c in camp.creatives:
        c_dto = GeneratedCreativeOut(
            id=c.id,
            campaign_id=c.campaign_id,
            version=c.version,
            image_url=c.image_url,
            local_image_path=c.local_image_path,
            caption_text=c.caption_text,
            hashtags=json.loads(c.hashtags or "[]"),
            width=c.width,
            height=c.height,
            aspect_ratio=c.aspect_ratio,
            post_pillar=getattr(c, "post_pillar", "festive_greeting") or "festive_greeting",
            model_used=c.model_used,
            prompt_used=c.prompt_used,
            quality_score=c.quality_score,
            quality_checks=json.loads(c.quality_checks or "{}"),
            is_selected=c.is_selected,
            created_at=c.created_at
        )
        creatives_dto.append(c_dto)
        if c.is_selected:
            active_creative_dto = c_dto

    attempts_dto = []
    for a in camp.attempts:
        attempts_dto.append(PublishingAttemptOut(
            id=a.id,
            campaign_id=a.campaign_id,
            attempt_number=a.attempt_number,
            started_at=a.started_at,
            finished_at=a.finished_at,
            status=a.status,
            platform_post_id=a.platform_post_id,
            platform_response=json.loads(a.platform_response or "{}"),
            error_code=a.error_code,
            error_traceback=a.error_traceback
        ))

    return PublishingCampaignOut(
        id=camp.id,
        social_account_id=camp.social_account_id,
        festival_id=camp.festival_id,
        festival_name=camp.festival.name if camp.festival else "",
        festival_slug=camp.festival.slug if camp.festival else "",
        platform=camp.social_account.platform if camp.social_account else "",
        account_username=camp.social_account.account_username if camp.social_account else "",
        year=camp.year,
        campaign_identifier=camp.campaign_identifier,
        scheduled_publish_time=camp.scheduled_publish_time,
        actual_publish_time=camp.actual_publish_time,
        status=camp.status,
        post_pillar=getattr(camp, "post_pillar", "festive_greeting") or "festive_greeting",
        error_message=camp.error_message,
        retry_count=camp.retry_count,
        is_approved=camp.is_approved,
        created_at=camp.created_at,
        updated_at=camp.updated_at,
        active_creative=active_creative_dto,
        creatives=creatives_dto,
        attempts=attempts_dto
    )

@router.get("", response_model=ResponseBase[List[PublishingCampaignOut]])
def list_campaigns(
    account_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = (
        db.query(PublishingCampaign)
        .join(SocialAccount)
        .filter(SocialAccount.organization_id == user.organization_id)
    )
    if account_id:
        query = query.filter(PublishingCampaign.social_account_id == account_id)
    if status:
        query = query.filter(PublishingCampaign.status == status)

    campaigns = query.order_by(PublishingCampaign.scheduled_publish_time.desc()).all()
    return ResponseBase(success=True, data=[map_campaign_to_dto(c) for c in campaigns])

@router.get("/{campaign_id}", response_model=ResponseBase[PublishingCampaignOut])
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    camp = (
        db.query(PublishingCampaign)
        .join(SocialAccount)
        .filter(PublishingCampaign.id == campaign_id, SocialAccount.organization_id == user.organization_id)
        .first()
    )
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return ResponseBase(success=True, data=map_campaign_to_dto(camp))

@router.post("/generate", response_model=ResponseBase[PublishingCampaignOut])
def generate_festival_campaign(
    payload: GenerateCampaignRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    account = db.query(SocialAccount).filter_by(id=payload.social_account_id, organization_id=user.organization_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")

    festival = db.query(FestivalDefinition).filter_by(slug=payload.festival_slug).first()
    if not festival:
        raise HTTPException(status_code=404, detail=f"Festival '{payload.festival_slug}' not found")

    # Check for existing campaign
    existing = db.query(PublishingCampaign).filter_by(
        social_account_id=account.id,
        festival_id=festival.id,
        year=payload.year
    ).first()

    if existing and not payload.force_regenerate:
        return ResponseBase(
            success=True,
            message="Campaign already exists for this festival and year. Returned existing campaign.",
            data=map_campaign_to_dto(existing)
        )

    # Calculate scheduled publish datetime
    obs = db.query(RegionalObservance).filter_by(festival_id=festival.id, year=payload.year).first()
    obs_date = obs.observed_date if obs else datetime.now(timezone.utc).date()
    auto_config = account.automation_config
    target_time_str = str(auto_config.target_publish_time) if auto_config else "09:00:00"
    tz_str = auto_config.timezone if auto_config else "Asia/Kolkata"
    publish_dt = CalendarService.calculate_publish_datetime(obs_date, target_time_str, tz_str)

    camp_identifier = f"CAMP-{account.platform.upper()}-{account.id[:8].upper()}-{festival.slug.upper()}-{payload.year}"

    # Determine post pillar (host-personalized archetype)
    effective_pillar = payload.post_pillar
    style_profile = account.style_profile
    if not effective_pillar or effective_pillar in ["auto", "default"]:
        if style_profile and style_profile.content_pillars:
            try:
                pillars_dict = json.loads(style_profile.content_pillars) if isinstance(style_profile.content_pillars, str) else style_profile.content_pillars
                sorted_pillars = sorted(pillars_dict.items(), key=lambda x: x[1], reverse=True)
                if sorted_pillars:
                    effective_pillar = sorted_pillars[0][0]
            except Exception:
                effective_pillar = "thought_leadership"
        else:
            effective_pillar = "thought_leadership"

    # Generate Image Creative conditioned on host visual archetype & post pillar
    greetings = json.loads(festival.default_greeting_phrases or "[]")
    greeting_title = greetings[0] if greetings else f"Happy {festival.name}"

    local_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
        festival_slug=festival.slug,
        greeting_text=greeting_title,
        style_profile=style_profile,
        post_pillar=effective_pillar
    )

    # Generate Caption & Hashtags conditioned on host persona & post pillar
    caption, hashtags = CaptionGenerator.generate_caption(
        festival=festival,
        style_profile=style_profile,
        account_name=account.display_name or account.account_username,
        post_pillar=effective_pillar
    )

    if not existing:
        camp = PublishingCampaign(
            social_account_id=account.id,
            festival_id=festival.id,
            year=payload.year,
            campaign_identifier=camp_identifier,
            scheduled_publish_time=publish_dt,
            status="generated",
            post_pillar=effective_pillar,
            is_approved=False
        )
        db.add(camp)
        db.flush()
        version = 1
    else:
        camp = existing
        camp.post_pillar = effective_pillar
        version = len(camp.creatives) + 1
        # Deselect older creatives
        for old_c in camp.creatives:
            old_c.is_selected = False

    creative = GeneratedCreative(
        campaign_id=camp.id,
        version=version,
        image_url=img_url,
        local_image_path=local_path,
        caption_text=caption,
        hashtags=json.dumps(hashtags),
        post_pillar=effective_pillar,
        quality_score=1.0,
        quality_checks=json.dumps(metrics),
        is_selected=True
    )
    db.add(creative)
    db.commit()
    db.refresh(camp)

    return ResponseBase(
        success=True,
        message=f"Greeting creative generated successfully for {festival.name}!",
        data=map_campaign_to_dto(camp)
    )

@router.put("/{campaign_id}", response_model=ResponseBase[PublishingCampaignOut])
def update_campaign_content(
    campaign_id: str,
    payload: UpdateCampaignCreativeRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    camp = (
        db.query(PublishingCampaign)
        .join(SocialAccount)
        .filter(PublishingCampaign.id == campaign_id, SocialAccount.organization_id == user.organization_id)
        .first()
    )
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    creative = (
        db.query(GeneratedCreative)
        .filter_by(campaign_id=camp.id, is_selected=True)
        .first()
    )
    if creative:
        if payload.caption_text is not None:
            creative.caption_text = payload.caption_text
        if payload.hashtags is not None:
            creative.hashtags = json.dumps(payload.hashtags)

    if payload.scheduled_publish_time is not None:
        camp.scheduled_publish_time = payload.scheduled_publish_time

    db.commit()
    db.refresh(camp)
    return ResponseBase(success=True, message="Campaign updated successfully", data=map_campaign_to_dto(camp))

@router.post("/{campaign_id}/approve", response_model=ResponseBase[PublishingCampaignOut])
def approve_campaign(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    camp = (
        db.query(PublishingCampaign)
        .join(SocialAccount)
        .filter(PublishingCampaign.id == campaign_id, SocialAccount.organization_id == user.organization_id)
        .first()
    )
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    camp.is_approved = True
    camp.approved_by_user_id = user.id
    if camp.status == "generated":
        camp.status = "scheduled"
    db.commit()
    db.refresh(camp)
    return ResponseBase(success=True, message="Campaign approved and scheduled for autonomous publication", data=map_campaign_to_dto(camp))

@router.post("/{campaign_id}/publish-now", response_model=ResponseBase[dict])
def publish_campaign_now(
    campaign_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    camp = (
        db.query(PublishingCampaign)
        .join(SocialAccount)
        .filter(PublishingCampaign.id == campaign_id, SocialAccount.organization_id == user.organization_id)
        .first()
    )
    if not camp:
        raise HTTPException(status_code=404, detail="Campaign not found")

    result = PublishingService.publish_campaign(db, camp)
    return ResponseBase(success=result.get("success", False), message="Publishing executed", data=result)
