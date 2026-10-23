import sys
import requests
import json

# Ensure UTF-8 console output for Windows PowerShell
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000/api/v1"

def test_live_persona_feature():
    print("==================================================")
    print("Testing FestiveAI Host Persona & Post Type Add-on")
    print("==================================================")

    # 1. Register or Login
    auth_payload = {
        "email": "persona_test_founder@festiveai.internal",
        "password": "Password123!",
        "full_name": "Dr. Sarah Lin (Founder & CTO)",
        "organization_name": "Lin Quantum Technologies"
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=auth_payload)
    if r.status_code == 200:
        token = r.json()["data"]["access_token"]
        print("1. [OK] Registered new user.")
    else:
        # Try login with JSON payload
        r2 = requests.post(f"{BASE_URL}/auth/login", json={"email": auth_payload["email"], "password": auth_payload["password"]})
        assert r2.status_code == 200, f"Login failed: {r2.text}"
        token = r2.json()["data"]["access_token"]
        print("1. [OK] Logged in existing user.")

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Connect new account with seeded posts
    acc_payload = {
        "platform": "instagram",
        "account_type": "business",
        "account_username": "dr_sarah_lin",
        "display_name": "Dr. Sarah Lin | AI Systems",
        "brand_name": "Lin Quantum Tech",
        "seed_historical_posts": True
    }
    r_acc = requests.post(f"{BASE_URL}/accounts/connect/mock", json=acc_payload, headers=headers)
    assert r_acc.status_code == 200, f"Connect failed: {r_acc.text}"
    account = r_acc.json()["data"]
    account_id = account["id"]
    print(f"2. [OK] Connected account @{account['account_username']} (ID: {account_id})")

    # 3. Retrieve Historical Posts & Check Post Pillars
    r_posts = requests.get(f"{BASE_URL}/accounts/{account_id}/posts", headers=headers)
    assert r_posts.status_code == 200, f"Get posts failed: {r_posts.text}"
    posts = r_posts.json()["data"]
    print(f"3. [OK] Retrieved {len(posts)} analyzed historical posts.")
    pillars_seen = set()
    for p in posts[:4]:
        print(f"   - [{p.get('post_pillar')}] {p.get('post_archetype')}: {p.get('caption')[:60]}...")
        if p.get('post_pillar'):
            pillars_seen.add(p.get('post_pillar'))

    assert len(pillars_seen) >= 2, f"Expected multiple pillars, got {pillars_seen}"

    # 4. Fetch AI-Learned Host Persona Profile
    r_prof = requests.get(f"{BASE_URL}/accounts/{account_id}/profile", headers=headers)
    assert r_prof.status_code == 200, f"Get profile failed: {r_prof.text}"
    profile = r_prof.json()["data"]
    print(f"4. [OK] Style Profile with Host Persona:")
    print(f"   - Persona Archetype : {profile.get('persona_type')}")
    print(f"   - Industry Niche    : {profile.get('industry_niche')}")
    print(f"   - Target Audience   : {profile.get('target_audience')}")
    print(f"   - Visual Archetype  : {profile.get('visual_archetype')}")
    print(f"   - Content Pillars   : {profile.get('content_pillars')}")
    print(f"   - Signature Hooks   : {profile.get('signature_hooks')[:2]}")

    # 5. Generate Post with Host Post Type: Thought Leadership
    camp_payload = {
        "social_account_id": account_id,
        "festival_slug": "diwali",
        "year": 2026,
        "post_pillar": "thought_leadership",
        "force_regenerate": True
    }
    r_gen = requests.post(f"{BASE_URL}/campaigns/generate", json=camp_payload, headers=headers)
    assert r_gen.status_code == 200, f"Generate failed: {r_gen.text}"
    camp = r_gen.json()["data"]
    creative = camp.get("active_creative")
    assert creative is not None, "Missing active creative"

    print(f"5. [OK] Generated New Post Conditioned on Thought Leadership:")
    print(f"   - Post Pillar       : {creative.get('post_pillar')}")
    print(f"   - Graphic Image     : {creative.get('image_url')}")
    print(f"   - Tailored Caption  :")
    print(f"     ---------------------------------------------")
    for line in creative.get('caption_text', '').split('\n'):
        print(f"     {line}")
    print(f"     ---------------------------------------------")
    print(f"   - Curated Hashtags  : {' '.join(creative.get('hashtags', []))}")

    # 6. Generate Post with Host Post Type: Behind The Scenes
    camp_payload_bts = {
        "social_account_id": account_id,
        "festival_slug": "holi",
        "year": 2026,
        "post_pillar": "behind_the_scenes",
        "force_regenerate": True
    }
    r_gen_bts = requests.post(f"{BASE_URL}/campaigns/generate", json=camp_payload_bts, headers=headers)
    assert r_gen_bts.status_code == 200, f"Generate BTS failed: {r_gen_bts.text}"
    camp_bts = r_gen_bts.json()["data"]
    creative_bts = camp_bts.get("active_creative")
    assert creative_bts is not None

    print(f"6. [OK] Generated New Post Conditioned on Behind The Scenes:")
    print(f"   - Post Pillar       : {creative_bts.get('post_pillar')}")
    print(f"   - Graphic Image     : {creative_bts.get('image_url')}")
    print(f"   - Tailored Caption  :")
    print(f"     ---------------------------------------------")
    for line in creative_bts.get('caption_text', '').split('\n'):
        print(f"     {line}")
    print(f"     ---------------------------------------------")

    print("\n>>> ALL LIVE INTEGRATION CHECKS PASSED FOR HOST PERSONA ADD-ON! <<<")

if __name__ == "__main__":
    test_live_persona_feature()
