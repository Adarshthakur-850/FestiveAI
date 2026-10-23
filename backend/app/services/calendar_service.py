import json
from datetime import date, datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import pytz
from sqlalchemy.orm import Session
from app.models.festival import FestivalDefinition, RegionalObservance

# Reputable astronomical & verified festival calendar dataset (2025 - 2027)
# References: Indian Astronomical Ephemeris & Positional Astronomy Centre,
# Ministry of Culture, Govt. of India / Islamic Fiqh Council / Gregorian Calendar
FESTIVAL_CATALOG: List[Dict[str, Any]] = [
    {
        "slug": "diwali",
        "name": "Diwali (Deepawali)",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Festival of Lights celebrating the victory of light over darkness and knowledge over ignorance.",
        "traditional_themes": ["diya", "golden_lights", "rangoli", "fireworks", "mandala", "prosperity"],
        "default_greeting_phrases": ["Happy Diwali", "Shubh Deepawali", "Wishing You a Joyous and Prosperous Diwali"],
        "dates": {
            2025: date(2025, 10, 20),
            2026: date(2026, 11, 8),
            2027: date(2027, 10, 29)
        },
        "verification_source": "Positional Astronomy Centre, India"
    },
    {
        "slug": "holi",
        "name": "Holi (Festival of Colors)",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Spring festival celebrating colors, love, joy, and the arrival of harvest season.",
        "traditional_themes": ["vibrant_gulal", "color_splatter", "spring_flowers", "joyous_celebration", "festive_sweets"],
        "default_greeting_phrases": ["Happy Holi", "Bura Na Mano Holi Hai", "Wishing You a Colorful & Vibrant Holi"],
        "dates": {
            2025: date(2025, 3, 14),
            2026: date(2026, 3, 4),
            2027: date(2027, 3, 22)
        },
        "verification_source": "Positional Astronomy Centre, India"
    },
    {
        "slug": "eid_ul_fitr",
        "name": "Eid al-Fitr",
        "category": "religious",
        "calculation_type": "islamic_hijri",
        "description": "Festival of Breaking the Fast concluding the holy month of Ramadan.",
        "traditional_themes": ["crescent_moon", "lantern_fanous", "islamic_geometry", "emerald_and_gold", "stars"],
        "default_greeting_phrases": ["Eid Mubarak", "Wishing You a Blessed Eid", "Eid Sa'id"],
        "dates": {
            2025: date(2025, 3, 31),
            2026: date(2026, 3, 20),
            2027: date(2027, 3, 10)
        },
        "verification_source": "Islamic Crescent Observation Project"
    },
    {
        "slug": "eid_ul_adha",
        "name": "Eid al-Adha",
        "category": "religious",
        "calculation_type": "islamic_hijri",
        "description": "Feast of the Sacrifice honoring devotion, charitable giving, and gratitude.",
        "traditional_themes": ["crescent_moon", "geometric_arabesque", "gratitude", "white_and_gold"],
        "default_greeting_phrases": ["Eid al-Adha Mubarak", "Wishing You a Peaceful and Blessed Eid"],
        "dates": {
            2025: date(2025, 6, 6),
            2026: date(2026, 5, 27),
            2027: date(2027, 5, 17)
        },
        "verification_source": "Islamic Crescent Observation Project"
    },
    {
        "slug": "christmas",
        "name": "Christmas",
        "category": "religious",
        "calculation_type": "fixed_gregorian",
        "default_fixed_month": 12,
        "default_fixed_day": 25,
        "description": "Annual festival commemorating peace, generosity, goodwill, and seasonal joy.",
        "traditional_themes": ["christmas_tree", "pine_wreath", "golden_stars", "snow_frost", "warm_candles", "crimson_and_gold"],
        "default_greeting_phrases": ["Merry Christmas", "Warm Season's Greetings", "Wishing You Peace and Joy this Christmas"],
        "dates": {
            2025: date(2025, 12, 25),
            2026: date(2026, 12, 25),
            2027: date(2027, 12, 25)
        },
        "verification_source": "Standard Gregorian Calendar"
    },
    {
        "slug": "new_year",
        "name": "New Year's Day",
        "category": "cultural",
        "calculation_type": "fixed_gregorian",
        "default_fixed_month": 1,
        "default_fixed_day": 1,
        "description": "Celebration of new beginnings, visionary goals, and year-ahead growth.",
        "traditional_themes": ["sparklers", "champagne_gold", "confetti", "geometric_elegance", "vision_forward", "midnight_blue"],
        "default_greeting_phrases": ["Happy New Year", "Wishing You a Year of Innovation & Success", "Cheers to New Beginnings"],
        "dates": {
            2025: date(2025, 1, 1),
            2026: date(2026, 1, 1),
            2027: date(2027, 1, 1)
        },
        "verification_source": "Standard Gregorian Calendar"
    },
    {
        "slug": "durga_puja",
        "name": "Durga Puja (Vijayadashami)",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Majestic festival honoring divine feminine energy, courage, and triumph over evil.",
        "traditional_themes": ["dhunuchi", "dhaak", "kash_flowers", "alpana", "divine_lotus", "vermilion_red"],
        "default_greeting_phrases": ["Shubho Bijoya", "Happy Durga Puja", "Warm Wishes on Durga Puja"],
        "dates": {
            2025: date(2025, 10, 2),
            2026: date(2026, 10, 20),
            2027: date(2027, 10, 9)
        },
        "verification_source": "Positional Astronomy Centre, India"
    },
    {
        "slug": "independence_day_in",
        "name": "Independence Day (India)",
        "category": "national",
        "calculation_type": "fixed_gregorian",
        "default_fixed_month": 8,
        "default_fixed_day": 15,
        "description": "Celebration of national sovereignty, unity, freedom, and technological progress.",
        "traditional_themes": ["tricolor", "ashoka_chakra", "saffron_white_green", "modern_nation", "sovereignty"],
        "default_greeting_phrases": ["Happy Independence Day", "Celebrating 79th Independence Day", "Swatantrata Diwas Ki Shubhkamnaye"],
        "dates": {
            2025: date(2025, 8, 15),
            2026: date(2026, 8, 15),
            2027: date(2027, 8, 15)
        },
        "verification_source": "National Calendar of India"
    },
    {
        "slug": "republic_day_in",
        "name": "Republic Day (India)",
        "category": "national",
        "calculation_type": "fixed_gregorian",
        "default_fixed_month": 1,
        "default_fixed_day": 26,
        "description": "Honoring the adoption of the Constitution and democratic spirit of India.",
        "traditional_themes": ["constitution", "tricolor_ribbons", "india_gate", "national_pride", "democracy"],
        "default_greeting_phrases": ["Happy Republic Day", "Gantantra Diwas Ki Hardik Shubhkamnaye"],
        "dates": {
            2025: date(2025, 1, 26),
            2026: date(2026, 1, 26),
            2027: date(2027, 1, 26)
        },
        "verification_source": "National Calendar of India"
    },
    {
        "slug": "raksha_bandhan",
        "name": "Raksha Bandhan",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Celebration of fraternal bond, mutual protection, affection, and lifelong family support.",
        "traditional_themes": ["rakhi_thread", "rooli_chawal", "festive_sweets", "silk_threads", "gold_filigree"],
        "default_greeting_phrases": ["Happy Raksha Bandhan", "Celebrating the Bond of Love & Protection"],
        "dates": {
            2025: date(2025, 8, 9),
            2026: date(2026, 8, 28),
            2027: date(2027, 8, 17)
        },
        "verification_source": "Positional Astronomy Centre, India"
    },
    {
        "slug": "ganesh_chaturthi",
        "name": "Ganesh Chaturthi",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Celebration of wisdom, auspicious beginnings, and remover of obstacles.",
        "traditional_themes": ["modak", "lotus_blossom", "auspicious_red", "festive_marigold", "divine_silhouette"],
        "default_greeting_phrases": ["Happy Ganesh Chaturthi", "Ganpati Bappa Morya", "Wishing You Prosperity & Wisdom"],
        "dates": {
            2025: date(2025, 8, 27),
            2026: date(2026, 9, 14),
            2027: date(2027, 9, 4)
        },
        "verification_source": "Positional Astronomy Centre, India"
    },
    {
        "slug": "onam",
        "name": "Onam",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Harvest festival of Kerala celebrating cultural harmony, prosperity, and unity.",
        "traditional_themes": ["pookalam_floral_rangoli", "kathakali", "kasavu_gold_cream", "banana_leaf", "boat_race"],
        "default_greeting_phrases": ["Happy Onam", "Warm Onam Greetings", "Wishing You Abundance & Joy this Onam"],
        "dates": {
            2025: date(2025, 9, 5),
            2026: date(2026, 8, 26),
            2027: date(2027, 9, 12)
        },
        "verification_source": "Govt. of Kerala Almanac"
    },
    {
        "slug": "pongal",
        "name": "Pongal (Makar Sankranti)",
        "category": "cultural",
        "calculation_type": "lunisolar_hindu",
        "description": "Thanksgiving harvest festival honoring the Sun, nature, and agrarian abundance.",
        "traditional_themes": ["clay_pot", "sugarcane", "sun_rays", "kolam", "overflowing_prosperity", "yellow_gold"],
        "default_greeting_phrases": ["Happy Pongal", "Happy Makar Sankranti", "Pongal O Pongal"],
        "dates": {
            2025: date(2025, 1, 14),
            2026: date(2026, 1, 14),
            2027: date(2027, 1, 15)
        },
        "verification_source": "Tamil Solar Almanac / Ephemeris"
    }
]

class CalendarService:
    @staticmethod
    def seed_festival_definitions(db: Session) -> None:
        """Seed or update all standard festival definitions and multi-year observances."""
        for item in FESTIVAL_CATALOG:
            festival = db.query(FestivalDefinition).filter_by(slug=item["slug"]).first()
            if not festival:
                festival = FestivalDefinition(
                    slug=item["slug"],
                    name=item["name"],
                    category=item["category"],
                    calculation_type=item["calculation_type"],
                    default_fixed_month=item.get("default_fixed_month"),
                    default_fixed_day=item.get("default_fixed_day"),
                    description=item.get("description"),
                    traditional_themes=json.dumps(item.get("traditional_themes", [])),
                    default_greeting_phrases=json.dumps(item.get("default_greeting_phrases", []))
                )
                db.add(festival)
                db.flush()
            
            # Seed observances for years 2025, 2026, 2027
            for year, obs_date in item.get("dates", {}).items():
                existing_obs = db.query(RegionalObservance).filter_by(
                    festival_id=festival.id,
                    year=year,
                    region_code="IN"
                ).first()
                if not existing_obs:
                    observance = RegionalObservance(
                        festival_id=festival.id,
                        year=year,
                        observed_date=obs_date,
                        region_code="IN",
                        verification_source=item.get("verification_source", "Astronomical Ephemeris"),
                        is_verified=True
                    )
                    db.add(observance)
        db.commit()

    @staticmethod
    def get_upcoming_festivals(
        db: Session,
        from_date: Optional[date] = None,
        days_ahead: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Retrieves all verified upcoming festivals within the specified window.
        """
        if from_date is None:
            from_date = date.today()
        
        to_date = from_date + timedelta(days=days_ahead)
        current_year = from_date.year

        observances = (
            db.query(RegionalObservance, FestivalDefinition)
            .join(FestivalDefinition, RegionalObservance.festival_id == FestivalDefinition.id)
            .filter(
                RegionalObservance.observed_date >= from_date,
                RegionalObservance.observed_date <= to_date
            )
            .order_by(RegionalObservance.observed_date.asc())
            .all()
        )

        results = []
        for obs, fest in observances:
            days_until = (obs.observed_date - from_date).days
            results.append({
                "festival_id": fest.id,
                "slug": fest.slug,
                "name": fest.name,
                "category": fest.category,
                "year": obs.year,
                "observed_date": obs.observed_date,
                "days_until": days_until,
                "verification_source": obs.verification_source,
                "traditional_themes": json.loads(fest.traditional_themes or "[]"),
                "default_greeting_phrases": json.loads(fest.default_greeting_phrases or "[]")
            })
        return results

    @staticmethod
    def calculate_publish_datetime(
        festival_date: date,
        target_publish_time_str: str = "09:00:00",
        timezone_str: str = "Asia/Kolkata"
    ) -> datetime:
        """
        Computes the exact UTC timestamp for publishing on the festival day at the desired local time.
        """
        tz = pytz.timezone(timezone_str)
        # Cleanly parse HH:MM:SS even if microseconds or extra spaces are present
        clean_time_str = str(target_publish_time_str).split(".")[0].strip()
        time_parts = [int(p) for p in clean_time_str.split(":")]
        local_dt = tz.localize(datetime(
            year=festival_date.year,
            month=festival_date.month,
            day=festival_date.day,
            hour=time_parts[0] if len(time_parts) > 0 else 9,
            minute=time_parts[1] if len(time_parts) > 1 else 0,
            second=time_parts[2] if len(time_parts) > 2 else 0
        ))
        return local_dt.astimezone(pytz.utc)
