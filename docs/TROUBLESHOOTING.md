# FestiveAI: Troubleshooting & Operations Guide

## Common Issues & Resolutions

### 1. Instagram Media Container Creation Fails
**Symptom**: `Media container creation failed: Invalid OAuth access token` (Code 190).
**Resolution**:
- Meta access tokens expire after 60 days. Navigate to **Connected Accounts**, click reconnect or re-authorize the Facebook Page connected to your Instagram Professional Account.
- Ensure the account is an **Instagram Business** or **Creator** account linked to a verified Facebook Page.

### 2. Sandbox/Mock Account Testing
**Scenario**: You want to test the entire end-to-end workflow immediately without waiting for Meta App Review approval.
**Resolution**:
- In the dashboard, go to **Connected Accounts** -> **Connect Account** -> click **Connect & Ingest Data**.
- A high-fidelity sandbox account will be provisioned with authentic historical posts for Diwali, Holi, and New Year.
- Open **Content Studio** to generate creatives, preview graphics, or test publishing.

### 3. Date Discrepancies in Lunisolar Festivals
**Symptom**: A festival falls on a different day depending on regional calendar observance (e.g. Diwali in southern vs northern India).
**Resolution**:
- Open **Festival Calendar**, select the festival, and adjust the custom lead days or override the date for your specific account preference.

### 4. Background Scheduler Cycle Verification
**Verification Command**:
```powershell
& "backend/.venv/Scripts/python.exe" -c "
import sys; sys.path.insert(0, 'backend')
from app.db.session import SessionLocal
from app.services.scheduler_service import SchedulerService
db = SessionLocal()
print(SchedulerService.run_automation_cycle(db))
db.close()
"
```
