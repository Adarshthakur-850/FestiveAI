import json
import random
from typing import Dict, Any, List, Optional, Tuple
from app.models.style_profile import StyleProfile
from app.models.festival import FestivalDefinition

# Authentic, culturally resonant template components by festival and language
FESTIVAL_CAPTION_CORPUS: Dict[str, Dict[str, Any]] = {
    "diwali": {
        "en": [
            "May the divine glow of countless diyas fill your life with eternal happiness, abundance, and peace. Wishing you and your family a luminous and prosperous Deepawali!",
            "As we celebrate the triumph of light over darkness and knowledge over ignorance, may this festive season inspire fresh milestones and endless success. Happy Diwali!",
            "Warmest thoughts and heartfelt greetings on the auspicious occasion of Diwali. May the year ahead shine bright with health, harmony, and growth."
        ],
        "hi": [
            "दीपों का यह पावन पर्व आपके जीवन में सुख, समृद्धि और नई ऊर्जा का संचार करे। दीपावली की हार्दिक शुभकामनाएं!",
            "अंधकार पर प्रकाश और अज्ञान पर ज्ञान की विजय के इस महापर्व पर आपको और आपके पूरे परिवार को शुभ दीपावली!",
            "माँ लक्ष्मी और विघ्नहर्ता गणेश का आशीर्वाद आप पर सदैव बना रहे। दीपावली की बहुत-बहुत बधाई!"
        ],
        "hinglish": [
            "Deepo ki roshni aur apno ke saath ke saath, ye Diwali laye aapke ghar dhero khushiyaan aur success. Wishing you all a very Happy Diwali!",
            "Iss festive season mein celebrate karte hain new beginnings aur shared milestones. Happy and prosperous Deepawali to you and your family!"
        ],
        "hashtags": ["#HappyDiwali", "#Deepawali", "#FestivalOfLights", "#Prosperity", "#FestiveSeason"]
    },
    "holi": {
        "en": [
            "May your world be painted with vibrant hues of joy, creative inspiration, and harmonious connections. Wishing you a thrilling and safe Happy Holi!",
            "Celebrating the arrival of spring and the triumph of joy over despair. May every splash of color bring happiness and renewed energy into your journey. Happy Holi!"
        ],
        "hi": [
            "रंगों, उमंगों और खुशियों का यह पावन पर्व आपके जीवन में नई उमंग और सकारात्मकता भरे। होली की हार्दिक शुभकामनाएं!",
            "गुलाल की खुशबू और अपनों का प्यार, सदा महकता रहे आपका संसार। शुभ होली!"
        ],
        "hinglish": [
            "Zindagi ke har canvas ko khoobsurat colors se bharne ka waqt aa gaya hai. Wishing everyone a vibrant and joyful Holi!",
            "Bura na mano, Holi hai! May this vibrant festival fill your days with laughter, togetherness, and colorful memories."
        ],
        "hashtags": ["#HappyHoli", "#FestivalOfColors", "#ColorsOfJoy", "#SpringCelebration", "#Togetherness"]
    },
    "eid_ul_fitr": {
        "en": [
            "May the blessings of the Almighty illuminate your path, enrich your soul, and bring enduring peace to your home. Eid Mubarak to you and your loved ones!",
            "On this blessed day of celebration and gratitude, may your heart be filled with joy, kindness, and fulfillment. Wishing you a peaceful and joyous Eid al-Fitr!"
        ],
        "hi": [
            "ईद का यह मुकद्दस त्यौहार आपके जीवन में खुशहाली, अमन और बरकत लेकर आए। आपको और आपके परिवार को ईद मुबारक!",
            "आपसी सौहार्द और मोहब्बत के इस पावन पर्व पर दिली मुबारकबाद। ईद-उल-फ़ितर मुबारक!"
        ],
        "hinglish": [
            "Aapko aur aapke poore parivar ko Eid Mubarak! May this beautiful occasion bring endless peace, happiness, and prosperity to your home."
        ],
        "hashtags": ["#EidMubarak", "#EidAlFitr", "#PeaceAndBlessings", "#Gratitude", "#Celebration"]
    },
    "christmas": {
        "en": [
            "May the spirit of Christmas bring peace to your home, love to your heart, and boundless inspiration to your endeavors. Wishing you a joyful holiday season and a Merry Christmas!",
            "Celebrating kindness, unity, and hope. May your festive days be filled with warm memories, cheerful moments, and good tidings. Merry Christmas to all!"
        ],
        "hi": [
            "क्रिसमस का यह पावन पर्व आपके जीवन में सुख, शांति और असीम खुशियाँ लेकर आए। मेरी क्रिसमस!",
            "प्रेम और सद्भाव का यह त्यौहार आपके घर-आंगन को रोशन करे। आपको और आपके परिवार को क्रिसमस की हार्दिक शुभकामनाएं!"
        ],
        "hinglish": [
            "May your holidays sparkle with joy, laughter, and warm moments with loved ones. Wishing everyone a Merry Christmas and joyful festive times!"
        ],
        "hashtags": ["#MerryChristmas", "#SeasonsGreetings", "#HolidaySpirit", "#PeaceAndJoy", "#Celebration"]
    },
    "new_year": {
        "en": [
            "Step into the new year with bold optimism, renewed purpose, and relentless dedication to your dreams. Wishing you 365 days of innovation, growth, and prosperity. Happy New Year!",
            "Here's to fresh chapters, impactful breakthroughs, and collaborative success. Thank you for being a vital part of our journey. Happy New Year!"
        ],
        "hi": [
            "नव वर्ष आपके जीवन में नई उमंग, अपार सफलता और उत्तम स्वास्थ्य लेकर आए। नए साल की हार्दिक शुभकामनाएं!",
            "नए संकल्पों और नई ऊंचाइयों के साथ नए साल का स्वागत करें। नव वर्ष मंगलमय हो!"
        ],
        "hinglish": [
            "Naya saal, nayi shuruat, aur dhero naye milestones! Wishing you and your team an inspiring, healthy, and successful New Year!"
        ],
        "hashtags": ["#HappyNewYear", "#NewBeginnings", "#Innovation", "#GrowthMindset", "#NewYearGoals"]
    },
    "independence_day_in": {
        "en": [
            "Celebrating the vibrant democratic spirit, rich heritage, and relentless pursuit of innovation that defines our great nation. Happy Independence Day to all!",
            "Saluting the visionaries and heroes who shaped our sovereign journey. Let us continue to build an empowered, inclusive, and forward-looking nation. Happy 79th Independence Day!"
        ],
        "hi": [
            "अनेकता में एकता ही हमारी सबसे बड़ी शक्ति है। स्वतंत्रता दिवस के पावन अवसर पर सभी देशवासियों को हार्दिक शुभकामनाएं। जय हिंद!",
            "राष्ट्र निर्माण और नवाचार के संकल्प के साथ स्वतंत्रता दिवस मनाएं। स्वतंत्रता दिवस की बहुत-बहुत बधाई!"
        ],
        "hinglish": [
            "Celebrating the pride, unity, and innovation of our nation. Wishing everyone a very Happy Independence Day! Jai Hind 🇮🇳"
        ],
        "hashtags": ["#IndependenceDay", "#PrideOfIndia", "#UnityInDiversity", "#InnovationIndia", "#JaiHind"]
    }
}

# Post Pillar & Host Persona conditioned festival caption corpus
PILLAR_CAPTION_CORPUS: Dict[str, Dict[str, Dict[str, str]]] = {
    "thought_leadership": {
        "diwali": {
            "en": "Diwali is a profound reminder of clarity cutting through the noise. In engineering and entrepreneurship, every difficult problem solved is like lighting a diya in the dark. May this festive season ignite breakthrough architecture, zero downtime, and soaring milestones for your ventures.",
            "hi": "दीपावली का यह पावन पर्व हमें सिखाता है कि हर अंधकार पर ज्ञान और नवाचार का प्रकाश विजय प्राप्त करता है। आप सभी के संकल्पों और प्रयासों को नई ऊंचाइयां मिलें। शुभ दीपावली!",
            "hinglish": "Diwali sirf roshni ka festival nahi, ek mindset hai—noise se nikal kar clarity aur vision paane ka. In building great things, every milestone is like lighting a diya. Wishing you and your ventures limitless growth this Deepawali!"
        },
        "holi": {
            "en": "True innovation thrives at the intersection of diverse perspectives and bold experimentation. Just as Holi paints every canvas with vibrant energy, may this season bring fresh creativity, intellectual curiosity, and breakthrough thinking to your roadmap.",
            "hi": "रंगों का यह त्यौहार विविधता और रचनात्मकता का प्रतीक है। आपके विचारों और नवाचारों को नई ऊर्जा और दिशा मिले। होली की हार्दिक शुभकामनाएं!",
            "hinglish": "Innovation happens when diverse colors and bold ideas come together. Wishing your team a vibrant Holi filled with creative sparks aur naye milestones!"
        },
        "new_year": {
            "en": "As we step into this new year, the standard isn't merely setting goals—it's about compounding resilience, mastering execution, and building systems that endure. Here's to 365 days of relentless innovation and meaningful impact.",
            "hi": "नया वर्ष नए संकल्पों, मजबूत इच्छाशक्ति और निरंतर प्रगति का समय है। आइए मिलकर उत्कृष्टता और नवाचार की नई मिसाल कायम करें। नव वर्ष मंगलमय हो!",
            "hinglish": "New Year is all about compounding resilience aur relentless execution. May this year take your vision, projects, aur personal growth to unprecedented levels!"
        },
        "independence_day_in": {
            "en": "A nation's greatness is built by creators and builders who dare to craft solutions from zero. Celebrating the sovereign spirit of self-reliance, ethical innovation, and collaborative progress on this 79th Independence Day.",
            "hi": "आत्मनिर्भरता, नवाचार और अटूट संकल्प ही हमारे राष्ट्र की शक्ति है। स्वतंत्रता दिवस के पावन अवसर पर सभी नवप्रवर्तकों को हार्दिक शुभकामनाएं। जय हिंद!",
            "hinglish": "Saluting the spirit of builders aur visionaries who shape our sovereign digital future. Wishing everyone a proud, innovative Happy Independence Day! 🇮🇳"
        },
        "eid_ul_fitr": {
            "en": "Enduring leadership is grounded in empathy, integrity, and shared prosperity. On this blessed occasion of Eid, may your ventures be guided by purpose, harmony, and profound value for the community.",
            "hi": "सद्भाव, त्याग और सेवा का यह पावन पर्व आपके जीवन में नई रोशनी और बरकत लाए। ईद मुबारक!",
            "hinglish": "True success lies in empathy aur creating shared value for everyone. Aapko aur aapki team ko Eid-ul-Fitr Mubarak!"
        },
        "christmas": {
            "en": "The festive season offers an invaluable moment to reflect on our core purpose: delivering genuine value and earning lasting trust. Wishing you peace, perspective, and renewed ambition this holiday season.",
            "hi": "आशा, करुणा और सेवा का यह पर्व आपके जीवन में शांति और नई प्रेरणा लेकर आए। मेरी क्रिसमस!",
            "hinglish": "May this Christmas inspire reflection, gratitude aur purposeful innovation for the journey ahead. Merry Christmas!"
        }
    },
    "behind_the_scenes": {
        "diwali": {
            "en": "Behind every seamless release and late-night sprint is an extraordinary team that makes magic look effortless. Today, our screens give way to sweets, laughter, and festive camaraderie! Warmest Deepawali greetings from our work family to yours.",
            "hi": "हमारी हर सफलता के पीछे हमारी समर्पित टीम की अथक मेहनत है। आज काम के बीच खुशियों और मिठाइयों का उत्सव! आप सभी को हमारी पूरी टीम की ओर से शुभ दीपावली।",
            "hinglish": "Behind every green build aur sprint delivery, ek amazing team hoti hai. Today, we step back to celebrate sweet moments aur festive cheer together. Happy Diwali from our family to yours!"
        },
        "holi": {
            "en": "From debugging complex architectures to splashing vibrant gulal across the office! Work is an adventure best shared with teammates who bring joy and color to every single challenge. Happy Holi from all of us!",
            "hi": "काम की गंभीरता के बीच खुशियों के रंग! हमारी टीम की ओर से आप सभी को होली की रंगबिरंगी शुभकामनाएं।",
            "hinglish": "Sprints, standups, and now lots of gulal! Work is so much better with teammates who make every day colorful. Wishing everyone a super fun and Happy Holi!"
        },
        "new_year": {
            "en": "Another year of intense problem-solving, collaborative milestones, and unforgettable laughs with the team in the books. Celebrating the people who make the daily journey extraordinary. Happy New Year!",
            "hi": "बीते साल के हर साझा प्रयास और सीख के लिए टीम का आभार। आइए नई ऊर्जा के साथ नए साल का स्वागत करें। नव वर्ष की शुभकामनाएं!",
            "hinglish": "Cheers to another year of late-night debugs, shared wins, and coffee-fueled milestones! Grateful for this rockstar team. Happy New Year to everyone!"
        },
        "christmas": {
            "en": "Festive sweaters, warm coffee, and genuine gratitude for the remarkable crew that makes our work meaningful every day. Merry Christmas to all our partners, peers, and friends!",
            "hi": "साथ मिलकर काम करने और आगे बढ़ने की खुशी के साथ, आप सभी को क्रिसमस की हार्दिक बधाई।",
            "hinglish": "Celebrating the holidays with the team that makes every single day special. Warm wishes aur Merry Christmas to everyone!"
        }
    },
    "product_showcase": {
        "diwali": {
            "en": "As diyas illuminate homes this festive season, we take pride in crafting tools that empower our clients to shine and scale without limits. Wishing you flawless uptime, rapid growth, and radiant success this Deepawali.",
            "hi": "जैसे दीपक चारों ओर प्रकाश फैलाते हैं, वैसे ही आपकी प्रगति और व्यवसाय नए आयाम छुए। दीपावली की मंगलमय शुभकामनाएं!",
            "hinglish": "Lighting up workflows just like diyas light up the night! Wishing our amazing users and clients zero downtime aur soaring prosperity this Diwali."
        },
        "holi": {
            "en": "Bringing vibrant simplicity to complex business challenges! Just as Holi unites a spectrum of brilliant colors, our solutions are built to harmonize every aspect of your operations. Happy Holi!",
            "hi": "हर रंग में नई उमंग! आपके व्यवसाय को मिले नए अवसर और सफलता। शुभ होली!",
            "hinglish": "Vibrant solutions for ambitious teams! May this festival of colors bring dynamic energy aur high conversions to your products. Happy Holi!"
        },
        "new_year": {
            "en": "Empowering ambitious teams to turn bold 2026 roadmaps into operational reality. Thank you for making our platform a cornerstone of your growth journey. Happy New Year!",
            "hi": "नए साल में आपके व्यवसाय को मिले नई गति और असीम संभावनाएं। नव वर्ष की हार्दिक शुभकामनाएं!",
            "hinglish": "Ready to crush your goals in the new year! Thank you for trusting our technology. Wishing you unmatched scale aur growth ahead!"
        }
    },
    "community_engagement": {
        "diwali": {
            "en": "The festival of lights is the ultimate moment to honor our amazing community of builders, creators, and partners. What is one personal or professional milestone you're most grateful for this season? Drop your wins below! Wishing you joy and prosperity.",
            "hi": "प्रकाश का यह पावन पर्व कृतज्ञता का समय है। आप सभी का हमारे सफर में साथ अनमोल है। दीपावली की हार्दिक बधाई!",
            "hinglish": "Festival of lights is incomplete without celebrating our incredible community! What is one win you are proud of this year? Tell us in the comments! Happy Diwali to all!"
        },
        "holi": {
            "en": "Colors spark connection and remind us of the strength of community. Which new creative endeavor or collaboration are you most excited for this spring? Wishing everyone a joyful, harmonious Holi!",
            "hi": "रंगों का यह संगम हमें प्रेम और सहयोग का संदेश देता है। आप सभी को होली की ढेरों शुभकामनाएं!",
            "hinglish": "Colors bring us together! What colorful idea are you building next? Wishing our entire community a blessed aur joyful Holi!"
        },
        "new_year": {
            "en": "To our community of visionaries and problem solvers: thank you for inspiring our roadmap every single day. What is your #1 audacious goal for this year? Share it below!",
            "hi": "आपके विश्वास और समर्थन के लिए दिली धन्यवाद। नव वर्ष आपके सभी सपनों को साकार करे!",
            "hinglish": "To our awesome community: what is your biggest dream project for the year ahead? Drop it below and let's make it happen together! Happy New Year!"
        }
    },
    "educational": {
        "diwali": {
            "en": "Did you know? In classical design philosophy, the intricate symmetry of Diwali rangolis represents algorithmic balance and focal harmony—principles that directly parallel clean systems architecture. Wishing you a luminous and beautifully architected festive season!",
            "hi": "दीपावली की पारंपरिक कलाएं हमें संतुलन, अनुशासन और सकारात्मकता का पाठ पढ़ाती हैं। आप सभी को शुभ दीपावली!",
            "hinglish": "Did you know? The sacred geometry of traditional diyas and rangolis reflects ancient balance and focus principles—just like clean system design! Happy Diwali!"
        },
        "holi": {
            "en": "The psychology of color teaches us that vibrant palettes stimulate cognitive focus and creative problem-solving. May this festival of colors recharge your creative instincts and elevate your craft. Happy Holi!",
            "hi": "रंगों का प्रभाव हमारी ऊर्जा और सोच को सकारात्मक बनाता है। होली का यह पावन पर्व आपके जीवन में नई ताजगी भरे।",
            "hinglish": "Color psychology shows that diverse hues inspire high cognitive flow. May this Holi bring vibrant breakthroughs to your work and life!"
        }
    }
}

class CaptionGenerator:
    @staticmethod
    def generate_caption(
        festival: FestivalDefinition,
        style_profile: Optional[StyleProfile] = None,
        account_name: Optional[str] = None,
        post_pillar: Optional[str] = None
    ) -> Tuple[str, List[str]]:
        """
        Synthesizes an authentic, tailored caption matching the account's formality score,
        emoji preferences, language settings, host persona, post pillar, and required brand sign-off.
        """
        slug = festival.slug

        # 1. Determine Language Preference
        preferred_langs = ["en"]
        if style_profile and style_profile.preferred_languages:
            try:
                preferred_langs = json.loads(style_profile.preferred_languages)
            except Exception:
                preferred_langs = ["en"]

        selected_lang = "en"
        if "hi" in preferred_langs and random.random() > 0.5:
            selected_lang = "hi"
        elif "hinglish" in preferred_langs and random.random() > 0.6:
            selected_lang = "hinglish"

        # 2. Determine Post Pillar from Request or Learned Profile
        effective_pillar = post_pillar
        if not effective_pillar or effective_pillar in ["auto", "default"]:
            if style_profile and style_profile.content_pillars:
                try:
                    pillars_dict = json.loads(style_profile.content_pillars) if isinstance(style_profile.content_pillars, str) else style_profile.content_pillars
                    # Pick highest pillar other than festive_greeting if available
                    sorted_pillars = sorted(pillars_dict.items(), key=lambda x: x[1], reverse=True)
                    if sorted_pillars:
                        effective_pillar = sorted_pillars[0][0]
                except Exception:
                    effective_pillar = "thought_leadership"
            else:
                effective_pillar = "thought_leadership"

        # 3. Select Base Caption Text from Pillar Corpus or General Festival Corpus
        body_text = None
        pillar_entry = PILLAR_CAPTION_CORPUS.get(effective_pillar, {}).get(slug, {})
        if pillar_entry:
            body_text = pillar_entry.get(selected_lang, pillar_entry.get("en"))

        if not body_text:
            corpus_entry = FESTIVAL_CAPTION_CORPUS.get(slug, FESTIVAL_CAPTION_CORPUS["diwali"])
            options = corpus_entry.get(selected_lang, corpus_entry.get("en", []))
            body_text = random.choice(options) if options else f"Warm festival greetings on {festival.name}!"

        # 4. Emoji integration according to emoji_frequency
        emoji_freq = style_profile.emoji_frequency if style_profile else "moderate"
        emojis_map = {
            "diwali": ["✨", "🪔", "🌟"],
            "holi": ["🎨", "🌈", "🌸"],
            "eid_ul_fitr": ["🌙", "✨", "🤲"],
            "eid_ul_adha": ["🌙", "✨", "🕊️"],
            "christmas": ["🎄", "⭐", "❄️"],
            "new_year": ["🥂", "✨", "🚀"],
            "independence_day_in": ["🇮🇳", "🕊️", "✨"]
        }
        fest_emojis = emojis_map.get(slug, ["✨", "🎉"])

        if emoji_freq == "none":
            body_text = body_text  # no emoji added
        elif emoji_freq == "minimal":
            body_text = f"{fest_emojis[0]} {body_text}"
        elif emoji_freq == "expressive":
            body_text = f"{fest_emojis[0]} {body_text} {' '.join(fest_emojis)} 🎉"
        else:  # moderate default
            body_text = f"{body_text} {' '.join(fest_emojis[:2])}"

        # 5. Add Brand Sign-off
        brand = style_profile.brand_name if (style_profile and style_profile.brand_name) else (account_name or "FestiveAI")
        sign_off = style_profile.required_sign_off if (style_profile and style_profile.required_sign_off) else f"Warm wishes from Team {brand}."

        final_caption = f"{body_text}\n\n{sign_off}"

        # 6. Hashtag curation (avoiding prohibited terms and adding pillar-specific tags)
        corpus_entry = FESTIVAL_CAPTION_CORPUS.get(slug, FESTIVAL_CAPTION_CORPUS["diwali"])
        base_hashtags = corpus_entry.get("hashtags", [f"#{festival.slug.capitalize()}", "#FestiveSeason"])
        brand_tag = f"#{brand.replace(' ', '')}"

        pillar_tags = {
            "thought_leadership": ["#ThoughtLeadership", "#Innovation", "#Leadership"],
            "behind_the_scenes": ["#BehindTheScenes", "#TeamCulture", "#Builders"],
            "product_showcase": ["#ProductExcellence", "#TechSolutions"],
            "community_engagement": ["#CommunityFirst", "#TogetherWeGrow"],
            "educational": ["#ProTips", "#TechInsights"]
        }
        extra_tags = pillar_tags.get(effective_pillar, [])
        curated_hashtags = list(dict.fromkeys(base_hashtags + extra_tags + [brand_tag]))

        # Check prohibited terms
        prohibited = []
        if style_profile and style_profile.prohibited_terms:
            try:
                prohibited = json.loads(style_profile.prohibited_terms) if isinstance(style_profile.prohibited_terms, str) else style_profile.prohibited_terms
            except Exception:
                pass

        for bad_word in prohibited:
            if bad_word.lower() in final_caption.lower():
                final_caption = final_caption.replace(bad_word, "").replace("  ", " ")

        return final_caption, curated_hashtags
