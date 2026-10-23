import requests
import json
import sys

# Ensure UTF-8 output on Windows terminal
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"

print("1. Testing Health...")
r = requests.get(f"{BASE_URL}/health")
assert r.status_code == 200, f"Health check failed: {r.text}"
print(f"   Health check passed: {r.json()}")

print("2. Connecting Mock Instagram Account...")
mock_payload = {
    "platform": "instagram",
    "account_type": "business",
    "account_username": "techpulse_official",
    "display_name": "TechPulse Innovations",
    "brand_name": "TechPulse",
    "seed_historical_posts": True
}
r = requests.post(f"{BASE_URL}/api/v1/accounts/connect/mock", json=mock_payload)
assert r.status_code == 200, f"Connect account failed: {r.text}"
account_data = r.json()["data"]
account_id = account_data["id"]
print(f"   Account Connected: @{account_data['account_username']} (ID: {account_id})")
print(f"   Historical posts ingested & analyzed: {account_data['historical_posts_count']}")

print("3. Fetching Learned Style Profile...")
r = requests.get(f"{BASE_URL}/api/v1/accounts/{account_id}/profile")
assert r.status_code == 200, f"Get profile failed: {r.text}"
profile = r.json()["data"]
print(f"   Brand: {profile['brand_name']}")
print(f"   Formality: {profile['formality_score']}, Emoji Frequency: {profile['emoji_frequency']}")
print(f"   Dominant Colors: {profile['dominant_colors']}")
print(f"   Sign-off: {profile['required_sign_off']}")

print("4. Fetching Upcoming Festival Calendar...")
r = requests.get(f"{BASE_URL}/api/v1/calendar/upcoming", params={"account_id": account_id, "days_ahead": 120})
assert r.status_code == 200, f"Get calendar failed: {r.text}"
upcoming = r.json()["data"]
print(f"   Upcoming festivals found: {len(upcoming)}")
for f in upcoming[:3]:
    print(f"   - {f['name']} on {f['observed_date']} ({f['days_until']} days away, relevance={f['relevance_score']*100:.0f}%)")

print("5. Generating Personalized Greeting Creative for Diwali...")
gen_payload = {
    "social_account_id": account_id,
    "festival_slug": "diwali",
    "year": 2026,
    "force_regenerate": True
}
r = requests.post(f"{BASE_URL}/api/v1/campaigns/generate", json=gen_payload)
assert r.status_code == 200, f"Generate creative failed: {r.text}"
campaign = r.json()["data"]
campaign_id = campaign["id"]
creative = campaign["active_creative"]
print(f"   Campaign ID: {campaign_id}")
print(f"   Creative Image URL: {creative['image_url']}")
print(f"   Caption Preview: {creative['caption_text'][:65]}...")
print(f"   Hashtags: {creative['hashtags']}")

print("6. Verifying Image Asset on Disk...")
img_resp = requests.get(f"{BASE_URL}{creative['image_url']}")
assert img_resp.status_code == 200, f"Image fetch failed: {img_resp.status_code}"
assert len(img_resp.content) > 10000, "Image content too small"
print(f"   Image streamed successfully ({len(img_resp.content)} bytes)")

print("7. Testing Immediate Autonomous Publishing...")
r = requests.post(f"{BASE_URL}/api/v1/campaigns/{campaign_id}/publish-now")
assert r.status_code == 200, f"Publish failed: {r.text}"
pub_result = r.json()["data"]
print(f"   Publish Success: {pub_result['success']}")
print(f"   Platform Post ID: {pub_result['platform_post_id']}")

print("8. Verifying Idempotency (Prevent Duplicate Publish)...")
r_dup = requests.post(f"{BASE_URL}/api/v1/campaigns/{campaign_id}/publish-now")
assert r_dup.status_code == 200
assert "already been published" in r_dup.json()["data"]["message"]
print(f"   Duplicate Prevention Verified: {r_dup.json()['data']['message']}")

print("9. Fetching Analytics Dashboard Overview...")
r = requests.get(f"{BASE_URL}/api/v1/analytics/overview")
assert r.status_code == 200, f"Analytics failed: {r.text}"
analytics = r.json()["data"]
print(f"   Analytics Overview: Published={analytics['posts_published']}, Generated={analytics['posts_generated']}, Connected={analytics['connected_accounts']}")

print("\n--- ALL 9 END-TO-END WORKFLOW VERIFICATIONS PASSED SUCCESSFULLY! ---")
