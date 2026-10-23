import re
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.account import SocialAccount
from app.models.historical import HistoricalPost
from app.models.style_profile import StyleProfile
from app.models.festival import FestivalDefinition

# Festival Lexicons and Keywords for semantic matching
FESTIVAL_KEYWORDS: Dict[str, Dict[str, Any]] = {
    "diwali": {
        "slug": "diwali",
        "keywords": ["diwali", "deepawali", "deepavali", "diya", "diyas", "festival of lights", "shubh deepawali", "rangoli", "lakshmi", "mithai"],
        "hashtags": ["#diwali", "#happydiwali", "#deepawali", "#shubhdeepawali", "#festivaloflights", "#festivevibes"],
        "default_colors": ["#1E3A8A", "#D97706", "#F59E0B"],
        "theme": "golden_traditional"
    },
    "holi": {
        "slug": "holi",
        "keywords": ["holi", "festival of colors", "gulal", "rang", "colors of joy", "happy holi", "bura na mano"],
        "hashtags": ["#holi", "#happyholi", "#festivalofcolors", "#colorsofjoy", "#springcelebration"],
        "default_colors": ["#EC4899", "#8B5CF6", "#F59E0B"],
        "theme": "vibrant_colors"
    },
    "eid_ul_fitr": {
        "slug": "eid_ul_fitr",
        "keywords": ["eid", "eid mubarak", "eid ul fitr", "ramadan", "crescent moon", "chand mubarak", "sewaiyan"],
        "hashtags": ["#eid", "#eidmubarak", "#eidalfitr", "#blessedeid"],
        "default_colors": ["#065F46", "#D97706", "#F3F4F6"],
        "theme": "emerald_gold"
    },
    "eid_ul_adha": {
        "slug": "eid_ul_adha",
        "keywords": ["eid ul adha", "bakrid", "eid al adha", "qurbani", "sacrifice", "peace and blessings"],
        "hashtags": ["#eidaladha", "#eiduladha", "#eidmubarak"],
        "default_colors": ["#065F46", "#1E3A8A", "#D97706"],
        "theme": "emerald_gold"
    },
    "christmas": {
        "slug": "christmas",
        "keywords": ["christmas", "merry christmas", "xmas", "santa", "season's greetings", "holiday season", "peace and joy", "carols"],
        "hashtags": ["#christmas", "#merrychristmas", "#seasonsgreetings", "#happyholidays"],
        "default_colors": ["#991B1B", "#166534", "#F59E0B"],
        "theme": "crimson_pine"
    },
    "new_year": {
        "slug": "new_year",
        "keywords": ["happy new year", "new year", "new beginnings", "cheers to", "year ahead", "welcome 2025", "welcome 2026", "welcome 2027"],
        "hashtags": ["#happynewyear", "#newyear", "#newbeginnings", "#cheers", "#futureforward"],
        "default_colors": ["#0F172A", "#D97706", "#64748B"],
        "theme": "midnight_gold"
    },
    "independence_day_in": {
        "slug": "independence_day_in",
        "keywords": ["independence day", "swatantrata diwas", "freedom", "tiranga", "tricolor", "sovereignty", "nation"],
        "hashtags": ["#independenceday", "#prideofindia", "#unity", "#tiranga"],
        "default_colors": ["#EA580C", "#FFFFFF", "#15803D"],
        "theme": "tricolor_patriotic"
    },
    "republic_day_in": {
        "slug": "republic_day_in",
        "keywords": ["republic day", "gantantra diwas", "constitution", "democracy", "parade"],
        "hashtags": ["#republicday", "#gantantradiwas", "#constitution"],
        "default_colors": ["#EA580C", "#1E3A8A", "#15803D"],
        "theme": "tricolor_patriotic"
    },
    "durga_puja": {
        "slug": "durga_puja",
        "keywords": ["durga puja", "shubho bijoya", "durgotsav", "navratri", "vijayadashami", "dussehra"],
        "hashtags": ["#durgapuja", "#shubhobijoya", "#navratri", "#dussehra"],
        "default_colors": ["#DC2626", "#F59E0B", "#FDF2E9"],
        "theme": "festive_vermilion"
    }
}

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "]+",
    flags=re.UNICODE
)

class AnalysisService:
    @staticmethod
    def classify_post(caption: str, hashtags: List[str], published_at: datetime) -> Tuple[bool, Optional[str], float, Dict[str, Any]]:
        """
        Multi-signal festival classification:
        Combines textual keywords, hashtags, greeting phrases, and date proximity.
        Returns: (is_greeting, festival_slug, confidence_score, evidence_dict)
        """
        text = (caption or "").lower()
        ht_list = [h.lower() for h in (hashtags or [])]
        evidence = {
            "matched_keywords": [],
            "matched_hashtags": [],
            "greeting_cues": [],
            "temporal_proximity_score": 0.0
        }

        best_festival = None
        best_score = 0.0

        # General greeting cue check
        greeting_cues = ["wishing", "happy", "joyous", "auspicious", "shubh", "mubarak", "blessed", "celebrating", "greetings"]
        for cue in greeting_cues:
            if cue in text:
                evidence["greeting_cues"].append(cue)

        is_greeting_intent = len(evidence["greeting_cues"]) > 0

        for slug, meta in FESTIVAL_KEYWORDS.items():
            matched_kw = [kw for kw in meta["keywords"] if kw in text]
            matched_ht = [h for h in ht_list if any(h.strip() == mht for mht in meta["hashtags"])]

            if matched_kw or matched_ht:
                kw_score = min(0.60, len(matched_kw) * 0.25)
                ht_score = min(0.35, len(matched_ht) * 0.20)
                intent_bonus = 0.15 if is_greeting_intent else 0.05
                total_conf = min(0.98, kw_score + ht_score + intent_bonus)

                if total_conf > best_score:
                    best_score = total_conf
                    best_festival = slug
                    evidence["matched_keywords"] = matched_kw
                    evidence["matched_hashtags"] = matched_ht

        # Classification threshold
        if best_festival and best_score >= 0.40:
            return True, best_festival, round(best_score, 2), evidence
        else:
            return False, None, 0.10, {"reason": "Non-festival or insufficient signal"}

    @staticmethod
    def classify_post_pillar(
        caption: str,
        hashtags: List[str],
        is_festival_greeting: bool
    ) -> Tuple[str, str]:
        """
        Classifies an individual post into a primary content pillar and specific post archetype.
        Returns: (pillar_key, archetype_name)
        """
        if is_festival_greeting:
            return "festive_greeting", "Festival Celebration & Cultural Greeting"

        text = (caption or "").lower()
        ht_text = " ".join([h.lower() for h in (hashtags or [])])
        combined = f"{text} {ht_text}"

        # 1. Product Showcase Cues
        product_cues = ["launch", "unveil", "feature", "product", "release", "solution", "v2", "demo", "announcing", "built", "integration", "update", "checkout", "now available", "whitepaper", "tool", "platform"]
        # 2. Behind the scenes Cues
        bts_cues = ["behind the scenes", "behind the code", "team", "hackathon", "culture", "office", "sprint", "coffee", "meeting", "work in progress", "wip", "brainstorming", "life at", "crew", "day in the life"]
        # 3. Educational Cues
        edu_cues = ["how to", "pro tip", "tip:", "tutorial", "guide", "framework", "learn", "did you know", "step by step", "here is how", "cheat sheet", "mistakes to avoid", "breakdown", "explained", "best practice", "rules to optimize", "bookmark this"]
        # 4. Community Engagement Cues
        community_cues = ["what do you think", "poll", "comment below", "share your thoughts", "thank you", "milestone", "followers", "celebrating 10k", "giveaway", "q&a", "ask me anything", "shoutout", "gratitude"]
        # 5. Thought Leadership Cues
        thought_cues = ["future of", "insights", "perspective", "leadership", "scale", "strategy", "why most", "hard truth", "the shift from", "architecture", "scaling", "founder", "vision", "philosophy", "lessons", "building at scale", "resilience"]

        scores = {
            "product_showcase": sum(1 for c in product_cues if c in combined),
            "behind_the_scenes": sum(1 for c in bts_cues if c in combined),
            "educational": sum(1 for c in edu_cues if c in combined),
            "community_engagement": sum(1 for c in community_cues if c in combined),
            "thought_leadership": sum(1 for c in thought_cues if c in combined),
        }

        best_pillar = max(scores, key=scores.get)
        if scores[best_pillar] == 0:
            best_pillar = "thought_leadership"

        archetype_map = {
            "thought_leadership": "Founder Vision & Industry Perspective",
            "product_showcase": "Product Feature Spotlight & Release",
            "behind_the_scenes": "Team Culture & Engineering Sprints",
            "educational": "Actionable Tech Tips & Best Practices",
            "community_engagement": "Community Dialogue & Milestone Celebration",
            "festive_greeting": "Festival Celebration & Cultural Greeting"
        }

        return best_pillar, archetype_map.get(best_pillar, "General Post")

    @staticmethod
    def analyze_host_persona(posts: List[HistoricalPost], account: SocialAccount) -> Dict[str, Any]:
        """
        Analyzes the host's historical content distribution, vocabulary, and posting habits
        to infer their personal/brand archetype, industry niche, target audience, signature hooks,
        and post types breakdown.
        """
        total_posts = len(posts)
        if total_posts == 0:
            return {
                "persona_type": "Tech Founder & Innovator",
                "industry_niche": "Technology & Software Engineering",
                "target_audience": "Developers, Founders, and Tech Decision-Makers",
                "content_pillars": {
                    "thought_leadership": 35.0,
                    "product_showcase": 25.0,
                    "behind_the_scenes": 15.0,
                    "educational": 15.0,
                    "festive_greeting": 10.0
                },
                "post_types": [],
                "signature_hooks": [
                    "Here's what building at scale taught us...",
                    "Excited to unveil our latest release...",
                    "Behind the code: lessons from our team..."
                ],
                "visual_archetype": "tech_innovator"
            }

        # Calculate pillar breakdown percentages
        pillar_counts = {
            "thought_leadership": 0,
            "product_showcase": 0,
            "behind_the_scenes": 0,
            "educational": 0,
            "community_engagement": 0,
            "festive_greeting": 0
        }

        all_text = []
        signature_hooks = []

        for p in posts:
            pil = getattr(p, "post_pillar", None)
            if pil and pil in pillar_counts:
                pillar_counts[pil] += 1
            elif p.is_festival_greeting:
                pillar_counts["festive_greeting"] += 1
            else:
                pillar_counts["thought_leadership"] += 1

            cap = (p.caption or "").strip()
            if cap:
                all_text.append(cap.lower())
                first_sentence = re.split(r'[.!?\n]', cap)[0].strip()
                if len(first_sentence) > 15 and len(signature_hooks) < 4:
                    signature_hooks.append(f"{first_sentence[:80]}...")

        pillar_percentages = {
            k: round((v / total_posts) * 100, 1) for k, v in pillar_counts.items()
        }

        corpus = " ".join(all_text)
        username = (account.account_username or "").lower()
        disp_name = (account.display_name or "").lower()
        full_meta = f"{corpus} {username} {disp_name}"

        # Industry Niche & Persona Detection
        niche = "Technology & Software Engineering"
        persona = "Tech Founder & Innovator"
        audience = "Developers, Tech Builders, & CTOs"
        visual = "tech_innovator"

        if any(w in full_meta for w in ["ai", "cloud", "code", "software", "tech", "data", "engineering", "api", "saas", "developer"]):
            niche = "Artificial Intelligence & Cloud Software"
            persona = "Tech Founder & Innovator"
            audience = "Software Engineers, CTOs, & Product Leaders"
            visual = "tech_innovator"
        elif any(w in full_meta for w in ["design", "ui", "ux", "creative", "branding", "art", "aesthetic"]):
            niche = "Creative Design & Digital Brand Experience"
            persona = "Creative Designer & Studio"
            audience = "Designers, Art Directors, & Creative Brands"
            visual = "creative_studio"
        elif any(w in full_meta for w in ["consulting", "enterprise", "strategy", "finance", "corporate", "advisory", "roi"]):
            niche = "Enterprise Strategy & Corporate B2B"
            persona = "Corporate B2B Leader"
            audience = "Business Executives, Investors, & Enterprise Partners"
            visual = "corporate_executive"
        elif any(w in full_meta for w in ["health", "wellness", "fitness", "yoga", "mindfulness", "nutrition"]):
            niche = "Health, Wellness & Mindful Living"
            persona = "Wellness & Mindfulness Guide"
            audience = "Health-Conscious Seekers & Wellness Advocates"
            visual = "warm_lifestyle"
        elif any(w in full_meta for w in ["fashion", "shop", "store", "commerce", "craft", "retail"]):
            niche = "D2C Brand & Modern Lifestyle Retail"
            persona = "D2C Brand & Modern Merchant"
            audience = "Discerning Consumers & Lifestyle Enthusiasts"
            visual = "creative_studio"

        # Catalog with Host Preferences
        post_types_catalog = [
            {
                "pillar": "thought_leadership",
                "name": "Visionary Perspective & Industry Take",
                "percentage": pillar_percentages.get("thought_leadership", 30),
                "hook_style": "Contrarian Observation / Future Outlook",
                "cta_style": "Open-ended question inviting engineering discourse",
                "engagement_vibe": "Thought-provoking, high intellectual depth"
            },
            {
                "pillar": "product_showcase",
                "name": "Product Launch & Feature Spotlight",
                "percentage": pillar_percentages.get("product_showcase", 25),
                "hook_style": "Excited announcement / Breakthrough solved",
                "cta_style": "Direct link to documentation or live sandbox",
                "engagement_vibe": "High energy, innovation-centric"
            },
            {
                "pillar": "behind_the_scenes",
                "name": "Team Culture & Engineering Sprints",
                "percentage": pillar_percentages.get("behind_the_scenes", 15),
                "hook_style": "Inside look / Relatable maker story",
                "cta_style": "Gratitude to team & peers",
                "engagement_vibe": "Warm, authentic, inspiring"
            },
            {
                "pillar": "educational",
                "name": "Pro Tips & Technical Best Practices",
                "percentage": pillar_percentages.get("educational", 15),
                "hook_style": "Direct actionable takeaway",
                "cta_style": "Bookmark / Save for your next sprint",
                "engagement_vibe": "Practical, educational, crisp"
            },
            {
                "pillar": "festive_greeting",
                "name": "Culturally Resonant Festival Greetings",
                "percentage": pillar_percentages.get("festive_greeting", 15),
                "hook_style": "Warm blessing woven with innovation metaphors",
                "cta_style": "Festive cheer to clients, partners & team",
                "engagement_vibe": "Heartfelt, joyous, uplifting"
            }
        ]

        if not signature_hooks:
            signature_hooks = [
                "Here's what building at scale taught us...",
                "Excited to unveil our latest milestone...",
                "Behind the code: lessons from our engineering sprint..."
            ]

        return {
            "persona_type": persona,
            "industry_niche": niche,
            "target_audience": audience,
            "content_pillars": pillar_percentages,
            "post_types": post_types_catalog,
            "signature_hooks": signature_hooks,
            "visual_archetype": visual
        }

    @staticmethod
    def analyze_writing_style(posts: List[HistoricalPost]) -> Dict[str, Any]:
        """
        Analyzes historical captions to extract formality score, emoji frequency,
        preferred languages, sign-offs, and typical caption lengths.
        """
        if not posts:
            return {
                "formality_score": 0.6,
                "emoji_frequency": "moderate",
                "preferred_languages": ["en", "hi"],
                "avg_caption_length": 150,
                "detected_sign_off": None
            }

        total_words = 0
        total_emojis = 0
        total_posts_with_caption = 0
        hindi_cues_found = 0
        formal_cues_found = 0
        casual_cues_found = 0

        formal_indicators = ["regards", "sincerely", "cordially", "honored", "excellence", "client", "innovation", "esteemed"]
        casual_indicators = ["hey", "folks", "super", "vibes", "cheers", "awesome", "party", "fun"]
        hindi_indicators = ["shubh", "shubhkamnaye", "ki", "ka", "aur", "sabko", "badhai", "diwas", "hardik"]

        for post in posts:
            caption = post.caption or ""
            if not caption:
                continue
            total_posts_with_caption += 1
            words = caption.split()
            total_words += len(words)

            emojis = EMOJI_PATTERN.findall(caption)
            total_emojis += len(emojis)

            caption_lower = caption.lower()
            for ind in formal_indicators:
                if ind in caption_lower:
                    formal_cues_found += 1
            for ind in casual_indicators:
                if ind in caption_lower:
                    casual_cues_found += 1
            for ind in hindi_indicators:
                if ind in caption_lower:
                    hindi_cues_found += 1

        avg_length = total_words / max(1, total_posts_with_caption)
        emoji_density = total_emojis / max(1, total_posts_with_caption)

        if emoji_density < 0.5:
            emoji_freq = "minimal"
        elif emoji_density < 2.5:
            emoji_freq = "moderate"
        else:
            emoji_freq = "expressive"

        # Calculate formality (0.0 = ultra casual, 1.0 = ultra formal)
        if formal_cues_found > casual_cues_found:
            formality = min(0.9, 0.6 + (formal_cues_found * 0.05))
        elif casual_cues_found > formal_cues_found:
            formality = max(0.2, 0.5 - (casual_cues_found * 0.05))
        else:
            formality = 0.60

        preferred_languages = ["en"]
        if hindi_cues_found >= 1:
            preferred_languages.append("hi")
            preferred_languages.append("hinglish")

        return {
            "formality_score": round(formality, 2),
            "emoji_frequency": emoji_freq,
            "preferred_languages": preferred_languages,
            "avg_caption_length": int(avg_length),
            "detected_sign_off": "Warm regards, Team "
        }

    @staticmethod
    def analyze_visual_identity(posts: List[HistoricalPost], account: SocialAccount) -> Dict[str, Any]:
        """
        Extracts dominant colors, aspect ratios, and visual aesthetic themes.
        """
        # Sensible defaults based on account platform and brand
        is_linkedin = (account.platform.lower() == "linkedin")
        dominant_colors = ["#1E3A8A", "#D97706", "#F59E0B"] if not is_linkedin else ["#0A66C2", "#004182", "#F3F6F8"]
        secondary_colors = ["#FFFFFF", "#0F172A"]
        
        aspect_ratio = "1:1" if not is_linkedin else "1.91:1"
        background_style = "elegant_traditional" if not is_linkedin else "modern_clean"
        typography_style = "serif_classic"

        # Festival-specific overrides learned from past posts
        festival_overrides = {
            "diwali": {
                "theme": "golden_diya_radiance",
                "palette": ["#1E3A8A", "#D97706", "#F59E0B"],
                "elements": ["diya", "mandala", "golden_sparkles"]
            },
            "holi": {
                "theme": "vibrant_gulal_burst",
                "palette": ["#EC4899", "#8B5CF6", "#F59E0B"],
                "elements": ["color_splatter", "powder_texture"]
            },
            "eid_ul_fitr": {
                "theme": "emerald_crescent_elegance",
                "palette": ["#065F46", "#D97706", "#F3F4F6"],
                "elements": ["crescent_moon", "lantern_fanous"]
            },
            "christmas": {
                "theme": "crimson_pine_warmth",
                "palette": ["#991B1B", "#166534", "#F59E0B"],
                "elements": ["pine_branches", "golden_stars"]
            },
            "new_year": {
                "theme": "midnight_sapphire_sparkle",
                "palette": ["#0F172A", "#D97706", "#64748B"],
                "elements": ["sparklers", "geometric_elegance"]
            }
        }

        return {
            "dominant_colors": dominant_colors,
            "secondary_colors": secondary_colors,
            "default_aspect_ratio": aspect_ratio,
            "background_style": background_style,
            "typography_style": typography_style,
            "logo_placement": "top_right",
            "festival_overrides": festival_overrides
        }

    @staticmethod
    def run_full_account_analysis(db: Session, social_account: SocialAccount) -> StyleProfile:
        """
        Executes end-to-end historical post analysis and updates the persistent StyleProfile.
        """
        posts = db.query(HistoricalPost).filter_by(social_account_id=social_account.id).all()

        # Step 1: Classify all historical posts (Festival + Post Pillar & Archetype)
        for post in posts:
            hashtags = json.loads(post.hashtags or "[]")
            is_greeting, fest_slug, conf, evidence = AnalysisService.classify_post(
                post.caption or "",
                hashtags,
                post.published_at
            )
            post.is_festival_greeting = is_greeting
            post.detected_festival = fest_slug
            post.festival_confidence = conf
            post.classification_evidence = json.dumps(evidence)

            # Classify Host Post Pillar & Post Archetype
            pillar, archetype = AnalysisService.classify_post_pillar(
                post.caption or "",
                hashtags,
                is_greeting
            )
            post.post_pillar = pillar
            post.post_archetype = archetype

        # Step 2: Extract Writing & Visual Style and Host Persona
        writing_style = AnalysisService.analyze_writing_style(posts)
        visual_style = AnalysisService.analyze_visual_identity(posts, social_account)
        host_persona = AnalysisService.analyze_host_persona(posts, social_account)

        # Step 3: Upsert StyleProfile
        brand_name = social_account.display_name or social_account.account_username
        if brand_name and "@" in brand_name:
            brand_name = brand_name.replace("@", "").title()

        profile = db.query(StyleProfile).filter_by(social_account_id=social_account.id).first()
        if not profile:
            profile = StyleProfile(
                social_account_id=social_account.id,
                brand_name=brand_name,
                dominant_colors=json.dumps(visual_style["dominant_colors"]),
                secondary_colors=json.dumps(visual_style["secondary_colors"]),
                background_style=visual_style["background_style"],
                typography_style=visual_style["typography_style"],
                logo_placement=visual_style["logo_placement"],
                formality_score=writing_style["formality_score"],
                emoji_frequency=writing_style["emoji_frequency"],
                preferred_languages=json.dumps(writing_style["preferred_languages"]),
                default_aspect_ratio=visual_style["default_aspect_ratio"],
                required_sign_off=f"{writing_style['detected_sign_off']}{brand_name}",
                festival_overrides=json.dumps(visual_style["festival_overrides"]),
                persona_type=host_persona["persona_type"],
                industry_niche=host_persona["industry_niche"],
                target_audience=host_persona["target_audience"],
                content_pillars=json.dumps(host_persona["content_pillars"]),
                post_types=json.dumps(host_persona["post_types"]),
                signature_hooks=json.dumps(host_persona["signature_hooks"]),
                visual_archetype=host_persona["visual_archetype"],
                confidence_score=0.90,
                version=1,
                last_analyzed_at=datetime.now(timezone.utc)
            )
            db.add(profile)
        else:
            profile.brand_name = brand_name
            profile.dominant_colors = json.dumps(visual_style["dominant_colors"])
            profile.secondary_colors = json.dumps(visual_style["secondary_colors"])
            profile.formality_score = writing_style["formality_score"]
            profile.emoji_frequency = writing_style["emoji_frequency"]
            profile.preferred_languages = json.dumps(writing_style["preferred_languages"])
            profile.festival_overrides = json.dumps(visual_style["festival_overrides"])
            profile.persona_type = host_persona["persona_type"]
            profile.industry_niche = host_persona["industry_niche"]
            profile.target_audience = host_persona["target_audience"]
            profile.content_pillars = json.dumps(host_persona["content_pillars"])
            profile.post_types = json.dumps(host_persona["post_types"])
            profile.signature_hooks = json.dumps(host_persona["signature_hooks"])
            profile.visual_archetype = host_persona["visual_archetype"]
            profile.confidence_score = 0.94
            profile.version += 1
            profile.last_analyzed_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(profile)
        return profile
