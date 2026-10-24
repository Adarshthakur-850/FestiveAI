import os
import uuid
import random
import json
import logging
from datetime import datetime, date, timedelta, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.account import SocialAccount, OAuthCredential
from app.models.festival import FestivalDefinition, RegionalObservance, AccountFestivalPreference
from app.models.campaign import PublishingCampaign, GeneratedCreative, PublishingAttempt
from app.models.automation import AutomationConfig
from app.services.calendar_service import CalendarService
from app.services.relevance_service import RelevanceEngine
from app.services.image_gen_service import GreetingCompositor
from app.services.caption_gen_service import CaptionGenerator
from app.services.publishing_service import PublishingService

logger = logging.getLogger("FestiveAI.Scheduler")

class SchedulerService:
    @staticmethod
    def generate_and_publish_autonomous_post(
        db: Session,
        account: SocialAccount,
        force_pillar: Optional[str] = None,
        force_immediate: bool = True
    ) -> Dict[str, Any]:
        """
        Autonomously composes, generates artwork, crafts captions, and publishes
        content on its own to the connected Instagram or LinkedIn account.
        Selects upcoming festivals/milestones or routine host persona pillars.
        """
        if not account.is_connected:
            return {"success": False, "error": f"Account @{account.account_username} is not connected."}

        creds = db.query(OAuthCredential).filter_by(social_account_id=account.id).first()
        if not creds:
            return {"success": False, "error": f"No OAuth credentials found for @{account.account_username}."}

        today = date.today()
        year = today.year
        style_profile = account.style_profile

        # 1. Determine Effective Pillar
        effective_pillar = force_pillar
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

        # 2. Check for upcoming festival within 14 days without an existing campaign
        upcoming = CalendarService.get_upcoming_festivals(db, from_date=today, days_ahead=14)
        target_festival: Optional[FestivalDefinition] = None
        target_fest_slug = None
        greeting_title = None

        for fest_info in upcoming:
            camp_exists = db.query(PublishingCampaign).filter_by(
                social_account_id=account.id,
                festival_id=fest_info["festival_id"],
                year=fest_info["year"]
            ).first()
            if not camp_exists:
                target_festival = db.query(FestivalDefinition).filter_by(id=fest_info["festival_id"]).first()
                target_fest_slug = fest_info["slug"]
                greeting_phrases = json.loads(target_festival.default_greeting_phrases or "[]")
                greeting_title = greeting_phrases[0] if greeting_phrases else f"Happy {target_festival.name}"
                break

        # 3. If no pending festival, synthesize a routine host persona pillar event
        is_routine_pillar_post = False
        if not target_festival or force_pillar:
            is_routine_pillar_post = True
            persona_topics = {
                "thought_leadership": [
                    "Scalable Architecture 2026",
                    "Autonomous Systems Engineering",
                    "Decoupled Microservices",
                    "Engineering Velocity & Craft"
                ],
                "product_showcase": [
                    "Product Excellence Milestone",
                    "High-Throughput Workflows",
                    "Real-Time Intelligence",
                    "Zero-Latency Scale"
                ],
                "behind_the_scenes": [
                    "Inside The Engineering Lab",
                    "Sprint Culture & Craft",
                    "Late Night Debugging To Green Builds",
                    "Life Inside The Dev Team"
                ],
                "educational": [
                    "Pro Tip: Database Connection Pools",
                    "Idempotent API Design",
                    "Resilient Systems Checklist",
                    "Clean Code Paradigms"
                ],
                "community_engagement": [
                    "Community Builders Spotlight",
                    "Open Source & Collaborative Growth",
                    "Celebrating Our Builders",
                    "Weekly Milestone Retrospective"
                ]
            }
            topics = persona_topics.get(effective_pillar, persona_topics["thought_leadership"])
            greeting_title = random.choice(topics)
            target_fest_slug = f"persona_{effective_pillar}_{today.strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"

            target_festival = FestivalDefinition(
                slug=target_fest_slug,
                name=greeting_title,
                category=f"persona_{effective_pillar}",
                calculation_type="autonomous_persona_post",
                description=f"Autonomous Host Persona Content: {greeting_title}",
                traditional_themes=json.dumps([effective_pillar, "innovation", "technology", "scale"]),
                default_greeting_phrases=json.dumps([greeting_title])
            )
            db.add(target_festival)
            db.flush()

            observance = RegionalObservance(
                festival_id=target_festival.id,
                year=year,
                observed_date=today,
                region_code="IN",
                verification_source="Autonomous Pipeline Generator",
                is_verified=True
            )
            db.add(observance)
            db.flush()

        # 4. Generate Visual Artwork via Compositor
        try:
            local_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
                festival_slug=target_fest_slug,
                greeting_text=greeting_title,
                style_profile=style_profile,
                post_pillar=effective_pillar
            )
        except Exception as e:
            logger.error(f"Failed composing autonomous creative: {e}")
            return {"success": False, "error": f"Image composition failed: {str(e)}"}

        # 5. Generate Tailored Caption & Hashtags
        if is_routine_pillar_post:
            caption, hashtags = CaptionGenerator.generate_pillar_caption(
                post_pillar=effective_pillar,
                style_profile=style_profile,
                account_name=account.display_name or account.account_username,
                topic=greeting_title
            )
        else:
            caption, hashtags = CaptionGenerator.generate_caption(
                festival=target_festival,
                style_profile=style_profile,
                account_name=account.display_name or account.account_username,
                post_pillar=effective_pillar
            )

        # 6. Create Campaign
        camp_identifier = f"CAMP-{account.platform.upper()}-{account.id[:8].upper()}-{target_fest_slug[:14].upper()}-{year}-{uuid.uuid4().hex[:4].upper()}"
        campaign = PublishingCampaign(
            social_account_id=account.id,
            festival_id=target_festival.id,
            year=year,
            campaign_identifier=camp_identifier,
            scheduled_publish_time=datetime.now(timezone.utc),
            status="scheduled",
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
            post_pillar=effective_pillar,
            quality_score=1.0,
            quality_checks=json.dumps(metrics),
            is_selected=True
        )
        db.add(creative)
        db.commit()

        # 7. Publish immediately if requested
        if force_immediate:
            pub_res = PublishingService.publish_campaign(db, campaign)
            if pub_res.get("success"):
                platform_post_id = pub_res.get("platform_post_id")
                permalink = (
                    f"https://www.instagram.com/p/{platform_post_id}/"
                    if account.platform == "instagram"
                    else f"https://www.linkedin.com/feed/update/{platform_post_id}/"
                )
                return {
                    "success": True,
                    "message": f"Autonomous post published successfully to {account.platform.capitalize()} (@{account.account_username})!",
                    "campaign_id": campaign.id,
                    "campaign_identifier": campaign.campaign_identifier,
                    "platform": account.platform,
                    "account_username": account.account_username,
                    "headline": greeting_title,
                    "post_pillar": effective_pillar,
                    "caption": caption,
                    "hashtags": hashtags,
                    "image_url": img_url,
                    "platform_post_id": platform_post_id,
                    "permalink": permalink,
                    "status": "published",
                    "mode": "autonomous"
                }
            else:
                return {
                    "success": False,
                    "error": f"Generation succeeded but publishing failed: {pub_res.get('error')}",
                    "campaign_id": campaign.id,
                    "status": campaign.status
                }

        return {
            "success": True,
            "message": f"Autonomous post scheduled for {account.platform.capitalize()}.",
            "campaign_id": campaign.id,
            "status": "scheduled"
        }

    @staticmethod
    def run_automation_cycle(db: Session) -> Dict[str, Any]:
        """
        Orchestrates the autonomous cycle:
        1. Checks all active social accounts.
        2. Detects upcoming relevant festivals within the configured lead window (e.g. 7 days).
        3. Generates creatives and schedules campaigns if not already present (duplicate prevention).
        4. In Autonomous Mode:
           - Automatically auto-approves generated festival campaigns.
           - If auto_post_pillars is enabled and no post has been published today,
             autonomously generates and publishes a routine host persona pillar post.
        5. Publishes scheduled campaigns whose target publish timestamp has arrived:
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
        today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)

        for account in accounts:
            auto_config = account.automation_config
            lead_days = auto_config.lead_time_days if auto_config else 7
            is_autonomous_mode = (auto_config.mode == "autonomous") if auto_config else True
            target_time_str = str(auto_config.target_publish_time) if auto_config else "09:00:00"
            tz_str = auto_config.timezone if auto_config else "Asia/Kolkata"
            auto_post_pillars = getattr(auto_config, "auto_post_pillars", True) if auto_config else True

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

            # 2. In Autonomous Mode: Check if daily routine pillar post is due
            if is_autonomous_mode and auto_post_pillars:
                published_today = (
                    db.query(PublishingCampaign)
                    .filter(
                        PublishingCampaign.social_account_id == account.id,
                        PublishingCampaign.status == "published",
                        PublishingCampaign.actual_publish_time >= today_start
                    )
                    .first()
                )
                if not published_today:
                    logger.info(f"Account @{account.account_username} has no post published today. Autonomously creating routine pillar post.")
                    auto_res = SchedulerService.generate_and_publish_autonomous_post(
                        db=db,
                        account=account,
                        force_immediate=True
                    )
                    if auto_res.get("success"):
                        summary["campaigns_published"] += 1
                        summary["campaigns_generated"] += 1
                        logger.info(f"Successfully auto-published routine pillar post for @{account.account_username}: {auto_res.get('platform_post_id')}")
                    else:
                        summary["errors"].append(f"Autonomous routine post failed for @{account.account_username}: {auto_res.get('error')}")

            # 3. Check and publish ready scheduled campaigns
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
