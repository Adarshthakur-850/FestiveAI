import os
import json
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.account import SocialAccount
from app.models.festival import FestivalDefinition, RegionalObservance, AccountFestivalPreference
from app.models.campaign import PublishingCampaign, GeneratedCreative
from app.models.automation import AutomationConfig
from app.services.calendar_service import CalendarService
from app.services.relevance_service import RelevanceEngine
from app.services.image_gen_service import GreetingCompositor
from app.services.caption_gen_service import CaptionGenerator
from app.services.publishing_service import PublishingService

logger = logging.getLogger("FestiveAI.Scheduler")

class SchedulerService:
    @staticmethod
    def run_automation_cycle(db: Session) -> Dict[str, Any]:
        """
        Orchestrates the autonomous cycle:
        1. Checks all active social accounts.
        2. Detects upcoming relevant festivals within the configured lead window (e.g. 7 days).
        3. Generates creatives and schedules campaigns if not already present (duplicate prevention).
        4. Publishes scheduled campaigns whose target publish timestamp has arrived:
           - In Autonomous Mode: Publishes automatically without manual intervention.
           - In Approval Mode: Only publishes if approved by an administrator.
        """
        accounts = db.query(SocialAccount).filter_by(is_connected=True).all()
        summary = {
            "accounts_processed": len(accounts),
            "campaigns_generated": 0,
            "campaigns_published": 0,
            "skipped_duplicates": 0,
            "awaiting_approval": 0,
            "errors": []
        }

        today = date.today()
        now_utc = datetime.now(timezone.utc)

        for account in accounts:
            auto_config = account.automation_config
            lead_days = auto_config.lead_time_days if auto_config else 7
            is_autonomous_mode = (auto_config.mode == "autonomous") if auto_config else False
            target_time_str = str(auto_config.target_publish_time) if auto_config else "09:00:00"
            tz_str = auto_config.timezone if auto_config else "Asia/Kolkata"

            # 1. Discover upcoming festivals within the lead window
            upcoming = CalendarService.get_upcoming_festivals(db, from_date=today, days_ahead=lead_days + 1)

            for fest_info in upcoming:
                fest_slug = fest_info["slug"]
                fest_year = fest_info["year"]
                fest_id = fest_info["festival_id"]
                fest_date = fest_info["observed_date"]

                # Check account preference & relevance
                pref = db.query(AccountFestivalPreference).filter_by(
                    social_account_id=account.id,
                    festival_id=fest_id
                ).first()

                if pref and not pref.is_enabled:
                    continue  # Disabled by user

                # DUPLICATE GATEKEEPER: Check if campaign already exists for (account, festival, year)
                existing_campaign = db.query(PublishingCampaign).filter_by(
                    social_account_id=account.id,
                    festival_id=fest_id,
                    year=fest_year
                ).first()

                if existing_campaign:
                    summary["skipped_duplicates"] += 1
                    continue

                # Plan & Generate creative
                try:
                    camp_identifier = f"CAMP-{account.platform.upper()}-{account.id[:8].upper()}-{fest_slug.upper()}-{fest_year}"
                    target_publish_dt = CalendarService.calculate_publish_datetime(
                        fest_date,
                        target_publish_time_str=target_time_str,
                        timezone_str=tz_str
                    )

                    festival = db.query(FestivalDefinition).filter_by(id=fest_id).first()
                    style_profile = account.style_profile

                    # Determine host post pillar from profile
                    effective_pillar = "thought_leadership"
                    if style_profile and style_profile.content_pillars:
                        try:
                            pillars_dict = json.loads(style_profile.content_pillars) if isinstance(style_profile.content_pillars, str) else style_profile.content_pillars
                            sorted_pillars = sorted(pillars_dict.items(), key=lambda x: x[1], reverse=True)
                            if sorted_pillars:
                                effective_pillar = sorted_pillars[0][0]
                        except Exception:
                            effective_pillar = "thought_leadership"

                    # Compose greeting image
                    greeting_phrases = json.loads(festival.default_greeting_phrases or '["Warm Greetings"]')
                    greeting_title = greeting_phrases[0] if greeting_phrases else f"Happy {festival.name}"
                    
                    local_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
                        festival_slug=fest_slug,
                        greeting_text=greeting_title,
                        style_profile=style_profile,
                        post_pillar=effective_pillar
                    )

                    # Compose caption & hashtags
                    caption, hashtags = CaptionGenerator.generate_caption(
                        festival=festival,
                        style_profile=style_profile,
                        account_name=account.display_name or account.account_username,
                        post_pillar=effective_pillar
                    )

                    # Create campaign
                    initial_status = "scheduled" if is_autonomous_mode else "generated"
                    campaign = PublishingCampaign(
                        social_account_id=account.id,
                        festival_id=fest_id,
                        year=fest_year,
                        campaign_identifier=camp_identifier,
                        scheduled_publish_time=target_publish_dt,
                        status=initial_status,
                        post_pillar=effective_pillar,
                        is_approved=is_autonomous_mode
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
                        post_pillar=effective_pillar,
                        quality_score=1.0,
                        quality_checks=json.dumps(metrics),
                        is_selected=True
                    )
                    db.add(creative)
                    db.commit()

                    summary["campaigns_generated"] += 1
                    if not is_autonomous_mode:
                        summary["awaiting_approval"] += 1

                except Exception as e:
                    db.rollback()
                    summary["errors"].append(f"Failed generating campaign for {fest_slug} ({account.account_username}): {str(e)}")

            # 2. Check and publish ready campaigns
            ready_campaigns = (
                db.query(PublishingCampaign)
                .filter(
                    PublishingCampaign.social_account_id == account.id,
                    PublishingCampaign.status.in_(["scheduled", "generated"]),
                    PublishingCampaign.scheduled_publish_time <= now_utc
                )
                .all()
            )

            for camp in ready_campaigns:
                if not camp.is_approved and not is_autonomous_mode:
                    # In approval mode and not approved yet
                    continue

                pub_res = PublishingService.publish_campaign(db, camp)
                if pub_res.get("success"):
                    summary["campaigns_published"] += 1
                else:
                    summary["errors"].append(f"Publish failed for {camp.campaign_identifier}: {pub_res.get('error')}")

        return summary
