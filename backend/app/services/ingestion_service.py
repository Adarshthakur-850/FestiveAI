import os
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.account import SocialAccount
from app.models.historical import HistoricalPost
from app.config import settings

class IngestionService:
    @staticmethod
    def import_posts_from_data(
        db: Session,
        social_account: SocialAccount,
        posts_data: List[Dict[str, Any]]
    ) -> int:
        """
        Imports historical posts from authorized API response or uploaded JSON export.
        Handles deduplication via unique (social_account_id, platform_post_id).
        """
        imported_count = 0
        for item in posts_data:
            post_id = str(item.get("platform_post_id") or item.get("id"))
            existing = db.query(HistoricalPost).filter_by(
                social_account_id=social_account.id,
                platform_post_id=post_id
            ).first()

            if existing:
                continue

            pub_at = item.get("published_at")
            if isinstance(pub_at, str):
                try:
                    pub_date = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
                except Exception:
                    pub_date = datetime.now(timezone.utc)
            elif isinstance(pub_at, datetime):
                pub_date = pub_at
            else:
                pub_date = datetime.now(timezone.utc)

            hashtags = item.get("hashtags", [])
            if isinstance(hashtags, str):
                try:
                    hashtags = json.loads(hashtags)
                except Exception:
                    hashtags = [h.strip() for h in hashtags.split() if h.startswith("#")]

            post = HistoricalPost(
                social_account_id=social_account.id,
                platform_post_id=post_id,
                published_at=pub_date,
                caption=item.get("caption", ""),
                hashtags=json.dumps(hashtags),
                media_type=item.get("media_type", "IMAGE"),
                media_url=item.get("media_url"),
                local_asset_path=item.get("local_asset_path"),
                image_width=item.get("image_width", 1080),
                image_height=item.get("image_height", 1080),
                language=item.get("language", "en")
            )
            db.add(post)
            imported_count += 1

        db.commit()
        return imported_count

    @staticmethod
    def seed_mock_account_historical_data(
        db: Session,
        social_account: SocialAccount
    ) -> int:
        """
        Seeds realistic multi-year historical social media posts for an account
        including Diwali, Holi, New Year, Independence Day, and standard company updates.
        """
        sample_posts = [
            {
                "platform_post_id": f"post_seed_diwali_2025_{social_account.platform}",
                "published_at": datetime(2025, 10, 20, 10, 30, 0, tzinfo=timezone.utc),
                "caption": "May the supreme light illuminate your path towards infinite prosperity and wisdom. Wishing everyone a joyous and auspicious Deepawali! ✨🪔 From all of us at TechPulse Innovations. #HappyDiwali #Deepawali #FestiveVibes #Innovation #Prosperity",
                "hashtags": ["#HappyDiwali", "#Deepawali", "#FestiveVibes", "#Innovation", "#Prosperity"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1512389142860-9c449e58a543?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_holi_2025_{social_account.platform}",
                "published_at": datetime(2025, 3, 14, 9, 15, 0, tzinfo=timezone.utc),
                "caption": "Draped in vibrant hues of joy, creativity, and togetherness! Wishing you and your loved ones a very Happy and colorful Holi! 🎨🌈 May this spring bring boundless inspiration. #HappyHoli #ColorsOfJoy #SpringCelebration #TeamTechPulse",
                "hashtags": ["#HappyHoli", "#ColorsOfJoy", "#SpringCelebration", "#TeamTechPulse"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_newyear_2025_{social_account.platform}",
                "published_at": datetime(2025, 1, 1, 0, 1, 0, tzinfo=timezone.utc),
                "caption": "Step into 2025 with bold ambition, resilient spirits, and ground-breaking breakthroughs! Cheers to another year of innovation and client excellence. Happy New Year! 🥂✨ #HappyNewYear2025 #NewBeginnings #TechPulse #FutureForward",
                "hashtags": ["#HappyNewYear2025", "#NewBeginnings", "#TechPulse", "#FutureForward"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_independenceday_2025_{social_account.platform}",
                "published_at": datetime(2025, 8, 15, 8, 0, 0, tzinfo=timezone.utc),
                "caption": "Honoring the spirit of unity, freedom, and relentless innovation that drives our nation forward. Happy 79th Independence Day to all citizens! 🇮🇳 #IndependenceDay #PrideOfIndia #Unity #TechPulse",
                "hashtags": ["#IndependenceDay", "#PrideOfIndia", "#Unity", "#TechPulse"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1532375810709-75b1da00537c?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_product_launch_{social_account.platform}",
                "published_at": datetime(2025, 6, 10, 14, 0, 0, tzinfo=timezone.utc),
                "caption": "We are proud to unveil our next-gen AI cloud orchestration engine. Designed for scale, speed, and uncompromising enterprise security. Read our whitepaper in bio! #TechPulse #AI #CloudComputing #Innovation",
                "hashtags": ["#TechPulse", "#AI", "#CloudComputing", "#Innovation"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_thought_leadership_{social_account.platform}",
                "published_at": datetime(2025, 5, 18, 11, 0, 0, tzinfo=timezone.utc),
                "caption": "Here's what building at scale taught us: clean architecture beats hasty features every single time. When you design for resilience and zero downtime, client trust follows naturally. What is your engineering philosophy? #ThoughtLeadership #SoftwareEngineering #TechFounder #CloudArchitecture",
                "hashtags": ["#ThoughtLeadership", "#SoftwareEngineering", "#TechFounder", "#CloudArchitecture"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_behind_scenes_{social_account.platform}",
                "published_at": datetime(2025, 4, 5, 16, 20, 0, tzinfo=timezone.utc),
                "caption": "Behind the code: 36 hours, 42 cups of coffee, and an unstoppable team during our quarterly hackathon sprint! Building the future is intense, but the shared passion is unforgettable. Proud of this crew! #BehindTheScenes #TeamCulture #LifeAtTechPulse #Builders",
                "hashtags": ["#BehindTheScenes", "#TeamCulture", "#LifeAtTechPulse", "#Builders"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            },
            {
                "platform_post_id": f"post_seed_educational_tip_{social_account.platform}",
                "published_at": datetime(2025, 2, 22, 10, 0, 0, tzinfo=timezone.utc),
                "caption": "Pro Tip: 3 critical rules to optimize your AI model inference latency in production: 1) Quantization without quality loss, 2) Batch tokenization pipelines, 3) Dynamic request caching. Bookmark this for your next sprint! #AIEngineering #DeveloperTips #MachineLearning #TechTutorial",
                "hashtags": ["#AIEngineering", "#DeveloperTips", "#MachineLearning", "#TechTutorial"],
                "media_type": "IMAGE",
                "media_url": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=1080",
                "image_width": 1080,
                "image_height": 1080,
                "language": "en"
            }
        ]
        return IngestionService.import_posts_from_data(db, social_account, sample_posts)
