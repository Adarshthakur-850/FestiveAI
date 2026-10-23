import json
import pytest
from datetime import datetime, timezone
from app.models.auth import Organization
from app.models.account import SocialAccount
from app.models.historical import HistoricalPost
from app.models.style_profile import StyleProfile
from app.models.festival import FestivalDefinition
from app.services.analysis_service import AnalysisService
from app.services.ingestion_service import IngestionService
from app.services.caption_gen_service import CaptionGenerator
from app.services.image_gen_service import GreetingCompositor

def test_host_persona_and_post_pillar_classification(db_session):
    # 1. Create Organization and Social Account
    org = Organization(name="TechAI Labs", slug="techai-labs")
    db_session.add(org)
    db_session.commit()

    account = SocialAccount(
        organization_id=org.id,
        platform="instagram",
        account_type="business",
        platform_account_id="insta_host_test_123",
        account_username="founder_techai",
        display_name="TechFounder AI",
        is_connected=True,
        status="active"
    )
    db_session.add(account)
    db_session.commit()

    # 2. Seed realistic posts spanning thought leadership, bts, product, and festivals
    IngestionService.seed_mock_account_historical_data(db_session, account)

    posts = db_session.query(HistoricalPost).filter_by(social_account_id=account.id).all()
    assert len(posts) >= 5

    # 3. Run full account analysis
    profile = AnalysisService.run_full_account_analysis(db_session, account)
    assert profile is not None

    # Verify that individual posts received post_pillar & post_archetype
    pillars_found = set()
    for p in posts:
        assert p.post_pillar is not None
        assert p.post_archetype is not None
        pillars_found.add(p.post_pillar)

    assert "festive_greeting" in pillars_found
    assert len(pillars_found) >= 2  # Has festival greetings and at least one host-specific pillar

    # 4. Verify host persona extraction
    assert profile.persona_type == "Tech Founder & Innovator"
    assert "Technology" in profile.industry_niche or "Artificial Intelligence" in profile.industry_niche
    assert profile.visual_archetype == "tech_innovator"

    content_pillars = json.loads(profile.content_pillars)
    assert isinstance(content_pillars, dict)
    assert "festive_greeting" in content_pillars
    assert sum(content_pillars.values()) > 0

    post_types = json.loads(profile.post_types)
    assert len(post_types) >= 3

    hooks = json.loads(profile.signature_hooks)
    assert len(hooks) >= 1

    # 5. Verify Persona & Pillar conditioned caption generation
    diwali_fest = FestivalDefinition(
        slug="diwali",
        name="Diwali",
        category="cultural",
        default_greeting_phrases='["Happy Diwali", "Shubh Deepawali"]'
    )

    # Generate Thought Leadership Celebration
    caption_tl, tags_tl = CaptionGenerator.generate_caption(
        festival=diwali_fest,
        style_profile=profile,
        account_name="TechFounder AI",
        post_pillar="thought_leadership"
    )
    assert any(term in caption_tl for term in ["Diwali", "Deepawali", "दीपावली", "दिवाली"])
    assert "TechFounder AI" in caption_tl
    assert any("ThoughtLeadership" in t or "Innovation" in t for t in tags_tl)

    # Generate Behind The Scenes Celebration
    caption_bts, tags_bts = CaptionGenerator.generate_caption(
        festival=diwali_fest,
        style_profile=profile,
        account_name="TechFounder AI",
        post_pillar="behind_the_scenes"
    )
    assert "team" in caption_bts.lower() or "sprint" in caption_bts.lower() or "family" in caption_bts.lower()
    assert any("BehindTheScenes" in t or "TeamCulture" in t for t in tags_bts)

    # 6. Verify Image Compositor with persona visual flourishes
    img_path, img_url, metrics = GreetingCompositor.generate_greeting_image(
        festival_slug="diwali",
        greeting_text="Happy Diwali",
        style_profile=profile,
        post_pillar="thought_leadership"
    )
    assert img_path is not None
    assert "/static/generated/" in img_url
    assert metrics["contrast_check"] == "PASSED (Dark-to-Gold High Contrast)"
