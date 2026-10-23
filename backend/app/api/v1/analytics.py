import json
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app.models.account import SocialAccount
from app.models.festival import RegionalObservance
from app.models.campaign import PublishingCampaign, PublishingAttempt
from app.models.automation import AutomationConfig
from app.schemas.automation import DashboardAnalyticsOut
from app.schemas.campaign import PublishingAttemptOut
from app.schemas.common import ResponseBase
from app.api.deps import get_current_user
from app.services.scheduler_service import SchedulerService

router = APIRouter(tags=["Analytics, Scheduler & Publishing History"])

@router.get("/analytics/overview", response_model=ResponseBase[DashboardAnalyticsOut])
def get_analytics_overview(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    accounts = db.query(SocialAccount).filter_by(organization_id=user.organization_id).all()
    account_ids = [a.id for a in accounts]

    total_acc = len(accounts)
    connected_acc = sum(1 for a in accounts if a.is_connected)

    today = date.today()
    in_30_days = today + timedelta(days=30)
    upcoming_30d = (
        db.query(RegionalObservance)
        .filter(RegionalObservance.observed_date >= today, RegionalObservance.observed_date <= in_30_days)
        .count()
    )

    campaigns = db.query(PublishingCampaign).filter(PublishingCampaign.social_account_id.in_(account_ids)).all() if account_ids else []
    generated_count = len(campaigns)
    scheduled_count = sum(1 for c in campaigns if c.status in ["scheduled", "generated"])
    published_count = sum(1 for c in campaigns if c.status == "published")
    failed_count = sum(1 for c in campaigns if c.status == "failed")

    auto_configs = db.query(AutomationConfig).filter(AutomationConfig.social_account_id.in_(account_ids)).all() if account_ids else []
    auto_count = sum(1 for cfg in auto_configs if cfg.mode == "autonomous")

    return ResponseBase(
        success=True,
        data=DashboardAnalyticsOut(
            total_accounts=total_acc,
            connected_accounts=connected_acc,
            upcoming_festivals_30d=upcoming_30d,
            posts_generated=generated_count,
            posts_scheduled=scheduled_count,
            posts_published=published_count,
            failed_attempts=failed_count,
            autonomous_mode_enabled_count=auto_count,
            system_health="HEALTHY"
        )
    )

@router.post("/scheduler/run-cycle", response_model=ResponseBase[dict])
def trigger_scheduler_cycle(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Manually triggers the background autonomous pipeline cycle
    (detects upcoming festivals, plans campaigns, generates creatives, and publishes scheduled posts).
    """
    summary = SchedulerService.run_automation_cycle(db)
    return ResponseBase(
        success=True,
        message="Autonomous cycle executed successfully",
        data=summary
    )

@router.get("/history/attempts", response_model=ResponseBase[List[PublishingAttemptOut]])
def list_publishing_attempts(
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    accounts = db.query(SocialAccount).filter_by(organization_id=user.organization_id).all()
    account_ids = [a.id for a in accounts]

    attempts = (
        db.query(PublishingAttempt)
        .join(PublishingCampaign)
        .filter(PublishingCampaign.social_account_id.in_(account_ids))
        .order_by(PublishingAttempt.started_at.desc())
        .limit(limit)
        .all()
    ) if account_ids else []

    results = []
    for a in attempts:
        results.append(PublishingAttemptOut(
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

    return ResponseBase(success=True, data=results)
