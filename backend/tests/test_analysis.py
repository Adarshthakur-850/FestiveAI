import pytest
from datetime import datetime, timezone
from app.services.analysis_service import AnalysisService
from app.models.historical import HistoricalPost

def test_festival_classifier_diwali():
    caption = "Wishing everyone a luminous and blessed Deepawali! May goddess Lakshmi bless your journey. #HappyDiwali #FestiveVibes"
    hashtags = ["#HappyDiwali", "#FestiveVibes"]
    is_greeting, slug, conf, evidence = AnalysisService.classify_post(
        caption, hashtags, datetime(2025, 10, 20, tzinfo=timezone.utc)
    )
    assert is_greeting is True
    assert slug == "diwali"
    assert conf >= 0.70
    assert "diwali" in evidence["matched_keywords"] or "deepawali" in evidence["matched_keywords"]

def test_festival_classifier_non_festival():
    caption = "Check out our latest Q3 earnings report and AI server infrastructure benchmarks."
    hashtags = ["#Tech", "#Cloud", "#Infrastructure"]
    is_greeting, slug, conf, evidence = AnalysisService.classify_post(
        caption, hashtags, datetime(2025, 7, 10, tzinfo=timezone.utc)
    )
    assert is_greeting is False
    assert slug is None

def test_writing_style_analysis_formality():
    posts = [
        HistoricalPost(caption="Honored to announce our partnership with esteemed enterprise leaders. Warm regards, Team TechPulse.", hashtags="[]"),
        HistoricalPost(caption="Cordially inviting all esteemed colleagues to our annual technology symposium.", hashtags="[]")
    ]
    style = AnalysisService.analyze_writing_style(posts)
    assert style["formality_score"] >= 0.65
    assert "en" in style["preferred_languages"]
