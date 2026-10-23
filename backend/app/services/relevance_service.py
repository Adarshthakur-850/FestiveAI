import json
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.account import SocialAccount
from app.models.historical import HistoricalPost
from app.models.festival import FestivalDefinition, AccountFestivalPreference
from app.models.style_profile import StyleProfile

class RelevanceEngine:
    """
    Multi-signal relevance scoring engine that calculates the affinity of an account
    for specific festivals based on empirical historical postings, brand profile,
    and user-configured preferences.
    """

    @staticmethod
    def calculate_festival_relevance(
        db: Session,
        social_account: SocialAccount,
        festival: FestivalDefinition
    ) -> float:
        # Check if user has an explicit preference set
        pref = db.query(AccountFestivalPreference).filter_by(
            social_account_id=social_account.id,
            festival_id=festival.id
        ).first()

        if pref and pref.relevance_score is not None:
            # If user has manually modified the score, honor it
            return pref.relevance_score

        # 1. Historical Post Evidence
        historical_posts = db.query(HistoricalPost).filter_by(
            social_account_id=social_account.id
        ).all()

        festival_post_count = 0
        total_posts = len(historical_posts)

        if total_posts > 0:
            for post in historical_posts:
                if post.detected_festival == festival.slug and post.is_festival_greeting:
                    festival_post_count += 1
                elif post.caption:
                    caption_lower = post.caption.lower()
                    if festival.slug.replace("_", " ") in caption_lower or festival.name.lower() in caption_lower:
                        festival_post_count += 1

        # Calculate historical evidence ratio
        historical_score = 0.0
        if total_posts > 0:
            if festival_post_count >= 1:
                # Strong signal: The account has celebrated this before!
                historical_score = min(0.95, 0.65 + (festival_post_count * 0.15))
            else:
                historical_score = 0.35
        else:
            # No historical posts ingested yet - fallback to category baseline
            historical_score = 0.50

        # 2. Category & Brand Alignment
        category_score = 0.70
        if festival.category == "national":
            # National days (Independence Day, Republic Day) are universally high relevance
            category_score = 0.85
        elif festival.category == "cultural":
            # Widely celebrated cultural festivals (Diwali, Holi, New Year)
            if festival.slug in ["diwali", "holi", "new_year"]:
                category_score = 0.90
            else:
                category_score = 0.65

        # 3. Language & Regional match
        lang_score = 0.70
        style = social_account.style_profile
        if style:
            try:
                preferred_langs = json.loads(style.preferred_languages) if isinstance(style.preferred_languages, str) else (style.preferred_languages or [])
            except Exception:
                preferred_langs = ["en"]
            if "hi" in preferred_langs or "hinglish" in preferred_langs:
                if festival.calculation_type == "lunisolar_hindu":
                    lang_score = 0.85
            if "en" in preferred_langs and festival.slug in ["new_year", "christmas"]:
                lang_score = 0.90

        # Weighted composite score
        # Historical evidence is heavily weighted (50%), Category (30%), Language (20%)
        composite = (0.50 * historical_score) + (0.30 * category_score) + (0.20 * lang_score)
        return round(composite, 2)

    @staticmethod
    def sync_account_festival_preferences(
        db: Session,
        social_account: SocialAccount
    ) -> List[AccountFestivalPreference]:
        """
        Evaluates all festivals in the system and upserts relevance preferences
        for the given social account.
        """
        all_festivals = db.query(FestivalDefinition).all()
        preferences = []

        for festival in all_festivals:
            pref = db.query(AccountFestivalPreference).filter_by(
                social_account_id=social_account.id,
                festival_id=festival.id
            ).first()

            score = RelevanceEngine.calculate_festival_relevance(db, social_account, festival)
            # Default enabled threshold: relevance >= 0.50
            is_enabled_default = score >= 0.50

            if not pref:
                pref = AccountFestivalPreference(
                    social_account_id=social_account.id,
                    festival_id=festival.id,
                    is_enabled=is_enabled_default,
                    relevance_score=score
                )
                db.add(pref)
            else:
                # Update relevance score if not explicitly customized
                pref.relevance_score = score
            preferences.append(pref)

        db.commit()
        return preferences
