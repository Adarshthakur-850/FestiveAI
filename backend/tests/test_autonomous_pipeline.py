import pytest
import uuid
from datetime import date, datetime, timezone
from app.models.auth import Organization, User
from app.models.account import SocialAccount, OAuthCredential
from app.models.automation import AutomationConfig
from app.models.campaign import PublishingCampaign
from app.core.encryption import encrypt_secret
from app.services.scheduler_service import SchedulerService
from app.api.v1.automation import (
    auto_post_now,
    get_automation_system_status,
    run_manual_automation_cycle,
    AutoPostNowRequest
)

def test_autonomous_config_defaults(db_session):
    unique = uuid.uuid4().hex[:6]
    org = Organization(name=f"Autonomous Org {unique}", slug=f"auto-org-{unique}")
    db_session.add(org)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="instagram",
        platform_account_id=f"auto_ig_{unique}",
        account_username=f"autouser_{unique}",
        display_name="Auto Brand",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    cfg = AutomationConfig(social_account_id=account.id)
    db_session.add(cfg)
    db_session.commit()

    assert cfg.mode == "autonomous"
    assert cfg.auto_post_pillars is True
    assert cfg.posting_cadence == "daily"
    assert cfg.auto_publish_immediate is True

def test_generate_and_publish_autonomous_post_instagram(db_session):
    unique = uuid.uuid4().hex[:6]
    org = Organization(name=f"Auto IG Org {unique}", slug=f"auto-ig-{unique}")
    db_session.add(org)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="instagram",
        platform_account_id=f"ig_{unique}",
        account_username=f"ig_tech_{unique}",
        display_name="Tech Innovator",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    creds = OAuthCredential(
        social_account_id=account.id,
        encrypted_access_token=encrypt_secret("mock_token_instagram_test")
    )
    db_session.add(creds)
    db_session.commit()

    result = SchedulerService.generate_and_publish_autonomous_post(
        db=db_session,
        account=account,
        force_pillar="thought_leadership",
        force_immediate=True
    )

    assert result["success"] is True
    assert result["status"] == "published"
    assert result["platform"] == "instagram"
    assert result["platform_post_id"].startswith("ig_media_")
    assert "instagram.com" in result["permalink"]
    assert result["post_pillar"] == "thought_leadership"
    assert result["image_url"].startswith("/static/generated/")

    # Check persistence
    camp = db_session.query(PublishingCampaign).filter_by(id=result["campaign_id"]).first()
    assert camp is not None
    assert camp.status == "published"
    assert camp.is_approved is True

def test_generate_and_publish_autonomous_post_linkedin(db_session):
    unique = uuid.uuid4().hex[:6]
    org = Organization(name=f"Auto LI Org {unique}", slug=f"auto-li-{unique}")
    db_session.add(org)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="linkedin",
        platform_account_id=f"li_{unique}",
        account_username=f"li_tech_{unique}",
        display_name="LinkedIn Leader",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    creds = OAuthCredential(
        social_account_id=account.id,
        encrypted_access_token=encrypt_secret("mock_token_linkedin_test")
    )
    db_session.add(creds)
    db_session.commit()

    result = SchedulerService.generate_and_publish_autonomous_post(
        db=db_session,
        account=account,
        force_pillar="product_showcase",
        force_immediate=True
    )

    assert result["success"] is True
    assert result["status"] == "published"
    assert result["platform"] == "linkedin"
    assert result["platform_post_id"].startswith("urn:li:share:")
    assert "linkedin.com" in result["permalink"]
    assert result["post_pillar"] == "product_showcase"

def test_auto_post_now_endpoint_and_status(db_session):
    unique = uuid.uuid4().hex[:6]
    org = Organization(name=f"Endpoint Org {unique}", slug=f"end-org-{unique}")
    db_session.add(org)
    db_session.flush()

    user = User(
        organization_id=org.id,
        email=f"auto_{unique}@example.com",
        hashed_password="testpasswordhash",
        full_name="Autonomous User",
        role="admin"
    )
    db_session.add(user)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="instagram",
        platform_account_id=f"endpoint_ig_{unique}",
        account_username=f"endpoint_user_{unique}",
        display_name="Endpoint Tester",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    creds = OAuthCredential(
        social_account_id=account.id,
        encrypted_access_token=encrypt_secret("mock_token_ig_endpoint")
    )
    db_session.add(creds)

    auto_cfg = AutomationConfig(
        social_account_id=account.id,
        mode="autonomous",
        auto_post_pillars=True
    )
    db_session.add(auto_cfg)
    db_session.commit()

    # 1. Trigger Auto Post Now via API function
    req = AutoPostNowRequest(
        account_id=str(account.id),
        post_pillar="educational"
    )
    res = auto_post_now(payload=req, db=db_session, user=user)
    assert res.success is True
    assert res.data["status"] == "published"
    assert res.data["platform_post_id"] is not None
    assert "instagram.com" in res.data["permalink"]

    # 2. Check System Status
    status_res = get_automation_system_status(db=db_session, user=user)
    assert status_res.success is True
    assert status_res.data["system_status"] == "ONLINE"
    assert status_res.data["autonomous_mode_count"] >= 1
    assert status_res.data["total_posts_published"] >= 1

    # 3. Check Cycle execution
    cycle_res = run_manual_automation_cycle(db=db_session, user=user)
    assert cycle_res.success is True
    assert "accounts_processed" in cycle_res.data
