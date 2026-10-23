import json
from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.festival import FestivalDefinition, AccountFestivalPreference
from app.models.campaign import PublishingCampaign
from app.schemas.festival import FestivalDefinitionOut, UpcomingFestivalOut, AccountFestivalPreferenceUpdate
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.calendar_service import CalendarService
from app.services.relevance_service import RelevanceEngine

router = APIRouter(prefix="/calendar", tags=["Festival Calendar & Relevance"])

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
