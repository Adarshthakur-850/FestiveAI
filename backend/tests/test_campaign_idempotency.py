import pytest
import uuid
import json
from datetime import datetime, timezone
from app.models.auth import Organization
from app.models.account import SocialAccount, OAuthCredential
from app.models.festival import FestivalDefinition
from app.models.campaign import PublishingCampaign, GeneratedCreative
from app.services.publishing_service import PublishingService
from app.core.encryption import encrypt_secret

def test_campaign_duplicate_prevention_and_idempotency(db_session):
    # Setup organization & account
    org = Organization(name="Test Org", slug=f"test-org-{uuid.uuid4().hex[:6]}")
    db_session.add(org)
    db_session.flush()

    account = SocialAccount(
        organization_id=org.id,
        platform="instagram",
        platform_account_id=f"test_acc_{uuid.uuid4().hex[:6]}",
        account_username="test_brand",
        status="active"
    )
    db_session.add(account)
    db_session.flush()

    creds = OAuthCredential(
        social_account_id=account.id,
        encrypted_access_token=encrypt_secret("mock_token_123")
    )
    db_session.add(creds)

    festival = FestivalDefinition(
        slug="diwali",
        name="Diwali",
        category="cultural",
        calculation_type="lunisolar_hindu"
    )
    db_session.add(festival)
    db_session.flush()

    # Create campaign
    camp = PublishingCampaign(
        social_account_id=account.id,
        festival_id=festival.id,
        year=2026,
        campaign_identifier=f"CAMP-IG-TEST-DIWALI-2026",
        scheduled_publish_time=datetime.now(timezone.utc),
        status="generated"
    )
    db_session.add(camp)
    db_session.flush()

    creative = GeneratedCreative(
        campaign_id=camp.id,
        version=1,
        image_url="/static/generated/test.png",
        local_image_path="./media/generated/test.png",
        caption_text="Happy Diwali from Test Brand!",
        hashtags=json.dumps(["#Diwali"]),
        is_selected=True
    )
    db_session.add(creative)
    db_session.commit()

    # First publish attempt: should succeed and mark published
    res1 = PublishingService.publish_campaign(db_session, camp)
    assert res1["success"] is True
    assert res1["status"] == "published"
    assert camp.status == "published"
    assert camp.actual_publish_time is not None

    # Second publish attempt: must be intercepted by Idempotency Gatekeeper
    res2 = PublishingService.publish_campaign(db_session, camp)
    assert res2["success"] is True
    assert "Duplicate publish prevented" in res2["message"]
