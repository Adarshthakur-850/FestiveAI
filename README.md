# FestiveAI 🪔✨
### AI-Powered Social Media Profile Analysis, Personalized Festival Greeting Generation, and Autonomous Publishing Platform

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.161-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-cyan.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-purple.svg)](https://vitejs.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Adarshthakur-850/FestiveAI)

FestiveAI is an enterprise-grade social media automation platform that eliminates the need for organizations and individuals to manually create and publish routine festival greetings every year.

It studies the historical posts of an authorized **Instagram** or **LinkedIn** account, learns its visual identity (color palette, typography, logo placement) and communication style (formality, emoji frequency, multilingual tone), identifies upcoming astronomical and regional festivals, synthesizes original personalized greetings, and autonomously publishes them on schedule via official platform APIs.

---

## 🌟 Key Features

1. **Official Platform Integrations**:
   - **Meta Instagram Graph API**: Two-step container creation, asynchronous status polling, and feed publishing.
   - **LinkedIn REST API**: Digital media asset registration, binary upload, and UGC post creation.
   - **Sandbox / Mock Adapter**: Realistic simulation mode enabling instant end-to-end verification without live API credentials.

2. **AI-Powered Profile & Host Persona Learning**:
   - **Host Persona Extraction**: Analyzes historical posts to infer host archetype (*Tech Founder*, *Corporate B2B Leader*, *Creative Designer*, *Wellness Guide*, etc.), industry niche, target audience, and signature opening hooks.
   - **Content Pillar Breakdown**: Automatically categorizes past posts into *Thought Leadership*, *Product Showcase*, *Behind the Scenes*, *Educational Tips*, and *Festivals*, tracking distribution percentages.
   - **Multi-Signal Festival Classification**: Identifies previous festival greetings (Diwali, Holi, Eid, Christmas, New Year, Durga Puja, etc.) using semantic NLP, hashtag taxonomies, and calendar proximity.
   - **Visual Style Extraction**: Extracts dominant 5-color palettes, layout density, contrast ratios, and logo positioning.
   - **Writing Style Extraction**: Evaluates formality indices, emoji frequencies, multilingual preferences (English, Hindi, Hinglish), and mandatory brand sign-offs.

3. **Intelligent Lunisolar Festival Calendar**:
   - Supports variable astronomical festivals (Hindu Lunisolar, Islamic Hijri) and fixed Gregorian dates for 2025–2027.
   - Multi-signal Bayesian relevance scoring tailored to each account's posting history and brand category.
   - Timezone-aware date calculations and configurable preparation windows (e.g., 7 days ahead).

4. **Deterministic Pillow Graphics Compositor**:
   - Solves generative AI text spelling hallucinations by deterministically rendering greetings, borders, and brand logos over high-resolution cultural motif backgrounds.
   - Generates pixel-perfect 1080×1080 (Instagram) and 1200×628 (LinkedIn) creatives.

5. **Autonomous Publishing & Zero-Duplicate Guarantee**:
   - Unique database constraints `UNIQUE(social_account_id, festival_id, year)` prevent duplicate posts.
   - **Dual Operating Modes**:
     - **Autonomous Mode**: Content is generated and published unattended at the scheduled time.
     - **Approval Mode**: Content is generated in advance and awaits review in Content Studio.
   - Bounded exponential backoff for transient network errors.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+ (or [uv](https://astral.sh/uv))
- Node.js 18+ and npm

### 1. Clone & Configure Environment
```bash
cp .env.example .env
```

### 2. Backend Setup
```powershell
# Create virtual environment and install dependencies
uv venv backend/.venv
uv pip install --python backend/.venv -r backend/requirements.txt

# Run Database Initialization & Migrations (SQLite default, PostgreSQL supported)
& "backend/.venv/Scripts/python.exe" -c "
import sys; sys.path.insert(0, 'backend')
from app.db.session import engine, SessionLocal
from app.models import Base
from app.services.calendar_service import CalendarService
Base.metadata.create_all(bind=engine)
db = SessionLocal()
CalendarService.seed_festival_definitions(db)
db.close()
print('FestiveAI Database Initialized!')
"

# Start FastAPI Backend Server
& "backend/.venv/Scripts/python.exe" backend/run.py
```
*API will be live at `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).*

### 3. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
*Dashboard will be live at `http://localhost:5173`.*

---

## 🐳 Docker Deployment

To launch the full production stack (FastAPI Backend, React SPA, PostgreSQL, Redis, and Persistent Scheduler):

```bash
docker-compose up --build -d
```
- Frontend Dashboard: `http://localhost`
- Backend API Docs: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`

---

## 🧪 Automated Test Suite

FestiveAI includes a comprehensive automated test suite covering unit tests, image composition, calendar astronomy, duplicate prevention, and API integration:

```powershell
& "backend/.venv/Scripts/python.exe" -m pytest backend/tests -v
```

**Test Coverage**:
- `test_festival_catalog_astronomical_dates`: Verifies annual lunisolar shifts for Diwali and Holi.
- `test_calculate_publish_datetime_timezone_awareness`: Verifies UTC conversion across timezones.
- `test_festival_classifier_diwali`: Verifies multi-signal greeting classification.
- `test_writing_style_analysis_formality`: Verifies formality scoring and language detection.
- `test_greeting_compositor_generates_valid_image`: Verifies Pillow graphics synthesis and resolution.
- `test_campaign_duplicate_prevention_and_idempotency`: Verifies database constraints and duplicate blocking.
- `test_health_check_endpoint` & `test_auth_registration_and_login`: Verifies FastAPI REST endpoints.

---

## 📂 Project Directory Structure

```
FestiveAI/
├── backend/
│   ├── app/
│   │   ├── config.py                 # Pydantic Settings & environment variables
│   │   ├── main.py                   # FastAPI initialization & scheduler worker
│   │   ├── core/
│   │   │   ├── security.py           # Bcrypt & JWT token management
│   │   │   └── encryption.py         # Fernet OAuth token encryption at rest
│   │   ├── db/
│   │   │   └── session.py            # SQLAlchemy 2.0 engine & session
│   │   ├── models/                   # Normalized database entities
│   │   │   ├── auth.py               # Organizations & Users
│   │   │   ├── account.py            # Social accounts & OAuth credentials
│   │   │   ├── historical.py         # Historical posts & media
│   │   │   ├── style_profile.py      # Persistent brand style profiles
│   │   │   ├── festival.py           # Definitions & regional observances
│   │   │   ├── campaign.py           # Campaigns, creatives & publishing attempts
│   │   │   └── automation.py         # Autonomous pipeline rules
│   │   ├── schemas/                  # Pydantic v2 schemas
│   │   ├── services/
│   │   │   ├── calendar_service.py   # Astronomical lunisolar dates (2025-2027)
│   │   │   ├── relevance_service.py  # Multi-signal Bayesian affinity scoring
│   │   │   ├── ingestion_service.py  # Post sync & sample dataset seeder
│   │   │   ├── analysis_service.py   # NLP classifier & visual/writing learner
│   │   │   ├── image_gen_service.py  # Deterministic Pillow graphics compositor
│   │   │   ├── caption_gen_service.py# Structured multilingual caption synthesizer
│   │   │   ├── publishing_service.py # Resilient publisher with duplicate locks
│   │   │   └── scheduler_service.py  # Persistent autonomous task orchestrator
│   │   ├── integrations/
│   │   │   ├── instagram.py          # Meta Instagram Graph API adapter
│   │   │   └── linkedin.py           # LinkedIn REST API adapter
│   │   └── api/v1/                   # REST API Routers
│   ├── tests/                        # Pytest suite
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/               # Navbar, Sidebar, StatCards
│   │   ├── pages/                    # Overview, ConnectedAccounts, StyleProfile,
│   │   │                             # FestivalCalendar, ContentStudio,
│   │   │                             # AutomationSettings, PublishingHistory
│   │   ├── services/api.ts           # Typed Axios client
│   │   └── types/index.ts            # TypeScript definitions
│   ├── package.json
│   ├── vite.config.ts
│   └── Dockerfile
├── docs/                             # Architecture, Security, Troubleshooting
├── .github/workflows/deploy-pages.yml# Automated GitHub Pages CI/CD
├── render.yaml                       # 1-Click Render.com Blueprint (Backend + Frontend)
├── vercel.json                       # Vercel deployment configuration
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## ☁️ Cloud Deployment & Hosting

### Option 1: Render.com (Recommended — Unified Full-Stack Single Service)

FestiveAI includes a multi-stage `Dockerfile` and native `render.yaml` that deploys the entire application (React SPA + FastAPI + Database + Background Scheduler) as a **single unified container** on Render's Free Tier with zero CORS issues.

1. Go to [render.com](https://render.com) and click **New +** > **Blueprint** (or click the **Deploy to Render** badge at the top of the README).
2. Connect your repository: `https://github.com/Adarshthakur-850/FestiveAI`.
3. Render will detect `render.yaml` and configure the **`festiveai`** unified service.
4. Click **Apply** to deploy!
   - Your frontend will load directly at root `/`.
   - Your API will be accessible at `/api/v1` and Swagger docs at `/docs`.

### Option 2: GitHub Pages (Free Automated UI Hosting)

The repository includes a ready-to-run GitHub Actions workflow (`.github/workflows/deploy-pages.yml`):

1. On your GitHub repo, go to **Settings** > **Pages**.
2. Under **Build and deployment** > **Source**, choose **GitHub Actions**.
3. Push to `main` (or run the workflow manually from the Actions tab).
4. Your frontend will be live at:
   `https://Adarshthakur-850.github.io/FestiveAI/`

*(Note: Connect `VITE_API_URL` secret in GitHub Settings > Secrets to point to your live backend service).*

### Option 3: Vercel (Frontend)

1. Go to [vercel.com](https://vercel.com) and click **Add New Project**.
2. Import `Adarshthakur-850/FestiveAI`.
3. Set **Root Directory** to `./frontend` or keep root (uses `vercel.json`).
4. Add environment variable `VITE_API_URL` pointing to your deployed backend.
5. Click **Deploy**.

---

## 🔒 Security & Privacy

- **Token Encryption**: Stored tokens are encrypted via AES-128-CBC with HMAC-SHA256 (Fernet).
- **Zero Logging of Secrets**: Access tokens are automatically masked in logs and exceptions.
- **Minimum Scopes**: Demands only feed publishing scopes without accessing personal profiles.
- **Tenant Isolation**: Strict organization-level filtering on all database queries.

---

## 📜 License
Distributed under the MIT License. Built for modern, culturally intelligent marketing automation.
