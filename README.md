# FestiveAI 🪔✨
### Autonomous Social Media Profile Learning, Deterministic Cultural Creative Synthesis, and Guaranteed Zero-Duplicate Festival Publishing Platform

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Adarshthakur-850/FestiveAI)

[![Live App](https://img.shields.io/badge/Live_Production-Render-success.svg?style=for-the-badge&logo=render)](https://festiveai-2b3x.onrender.com/)
[![API Docs](https://img.shields.io/badge/Swagger_Docs-API_v1-blue.svg?style=for-the-badge&logo=fastapi)](https://festiveai-2b3x.onrender.com/docs)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

## 🌐 Live Production Deployment

| Service | Public Production URL |
| :--- | :--- |
| **Unified Web Dashboard** | **[https://festiveai-2b3x.onrender.com/](https://festiveai-2b3x.onrender.com/)** |
| **Interactive API Documentation (Swagger)** | **[https://festiveai-2b3x.onrender.com/docs](https://festiveai-2b3x.onrender.com/docs)** |
| **Alternative OpenAPI Docs (ReDoc)** | **[https://festiveai-2b3x.onrender.com/redoc](https://festiveai-2b3x.onrender.com/redoc)** |
| **Backend Health Check** | **[https://festiveai-2b3x.onrender.com/health](https://festiveai-2b3x.onrender.com/health)** |
| **API Base Endpoint** | **[https://festiveai-2b3x.onrender.com/api/v1](https://festiveai-2b3x.onrender.com/api/v1)** |

> [!NOTE]
> The live deployment runs as a unified single-container full-stack application on Render. The FastAPI engine serves the REST API, the deterministic graphics synthesizer, the persistent background scheduler, and the compiled responsive React 19 Single Page Application (SPA).

---

## 📖 Executive Summary (In Brief)

**FestiveAI** is an autonomous marketing automation platform built to permanently solve the problem of routine festival greeting creation for businesses, founders, creators, and marketing teams.

Every year, companies spend hundreds of manual hours tracking festival dates, briefing designers, proofreading cultural copy, and scheduling greeting posts across Instagram and LinkedIn. FestiveAI automates this entire lifecycle end-to-end:

1. **Ingests and Analyzes Historical Posts**: Deeply learns your account's visual identity (5-color palette, logo placement, typography) and writing style (formality index, emoji frequency, multilingual tone).
2. **Infers Host Persona & Content Pillars**: Identifies whether the brand persona is a *Tech Founder*, *Corporate B2B Leader*, *Creative Agency*, or *Lifestyle Brand*, and categorizes historical posts into content pillars (*Thought Leadership*, *Behind-the-Scenes*, *Product Showcase*, *Educational*, etc.).
3. **Tracks Astronomical & Lunisolar Calendars**: Uses Hindu lunisolar ephemeris and Islamic Hijri astronomical cycles to compute moving festival dates (Diwali, Eid, Holi, Ganesh Chaturthi, etc.) and Gregorian dates with multi-signal brand relevance scoring.
4. **Composes Deterministic Artwork & Copy**: Eliminates generative AI spelling hallucinations and awkward artifacts by using a deterministic Pillow (PIL) graphic compositor with gold accents, sacred geometry, and logo overlays, paired with structured multilingual captions (English, Hindi, Hinglish).
5. **Autonomously Publishes with Zero Duplicate Locks**: Implements strict database unique constraints `UNIQUE(social_account_id, festival_id, year)` and idempotent state machines, guaranteeing that no account ever publishes duplicate festival posts. Operates in either **Autonomous Hands-Off Mode** or **Human-in-the-Loop Approval Mode**.
6. **Multi-Device Responsive Interface**: Designed from the ground up to render seamlessly across mobile phones, tablets, laptops, and ultra-wide desktop monitors.

---

## 🏗️ System Architecture

FestiveAI operates on a clean, decoupled full-stack architecture designed for enterprise reliability, high performance, and rapid deployment:

```
┌────────────────────────────────────────────────────────────────────────────┐
│                             CLIENT LAYER                                   │
│  React 19 SPA • TypeScript • Tailwind CSS • Lucide Icons • Responsive UI   │
│       (Mobile Hamburger Drawer + Tablet Reflow + Desktop Dashboard)        │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │ REST API / JSON (Axios)
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND ENGINE                           │
│  ┌───────────────────────┬──────────────────────┬───────────────────────┐  │
│  │   Auth & Security     │  Calendar Engine     │  Style & Persona      │  │
│  │   • JWT & Bcrypt      │  • Lunisolar Dates   │  • Color Extraction   │  │
│  │   • Fernet Encryption │  • Relevance Scorer  │  • Pillar Breakdown   │  │
│  └───────────────────────┴──────────────────────┴───────────────────────┘  │
│  ┌───────────────────────┬──────────────────────┬───────────────────────┐  │
│  │   Creative Studio     │  Publishing Engine   │  Autonomous Worker    │  │
│  │   • Pillow Compositor │  • Instagram Graph   │  • APScheduler Cron   │  │
│  │   • Multilingual Copy │  • LinkedIn UGC REST │  • Lead Window Scan   │  │
│  └───────────────────────┴──────────────────────┴───────────────────────┘  │
└─────────────────────────────────────┬──────────────────────────────────────┘
                                      │ SQLAlchemy 2.0 ORM
                                      ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                             DATABASE LAYER                                 │
│        SQLite (Zero-Config Default) / PostgreSQL (Cloud Production)         │
│     Unique Idempotency Constraints: UNIQUE(account_id, festival_id, year)   │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Detailed Feature Walkthrough

### 1. AI-Powered Profile Learning & Host Persona Extraction
- **Historical Post Ingestion**: Connects to Instagram or LinkedIn (or instant Sandbox Mock accounts) and ingests historical posts, captions, hashtags, and media assets.
- **Host Persona Archetype Inference**: Automatically identifies the host persona type (*Tech Founder & Innovator*, *Corporate B2B Leader*, *Creative Designer & Studio*, *Wellness & Mindfulness Guide*, *D2C Brand*, or *Educator*) and captures the host's signature opening hooks (e.g. `"Here's what building at scale taught us..."`).
- **Content Pillar Distribution**: Breaks down past posts into *Thought Leadership*, *Product Features*, *Behind-the-Scenes*, *Educational Tips*, and *Festivals*, generating interactive progress bars and distribution metrics.
- **Visual Palette Extraction**: Identifies the account's dominant 5-color palette, secondary accents, contrast ratios, and preferred logo placement (*Top Right*, *Top Left*, *Bottom Right*, *Bottom Center*).
- **Writing Style Extraction**: Quantifies formality score ($0.0$ to $1.0$), emoji frequency (*none*, *minimal*, *moderate*, *expressive*), multilingual preference (*English*, *Hindi*, *Hinglish*), and enforces mandatory brand sign-offs while blocking prohibited promotional terms (*sale*, *discount*, *limited time*).

### 2. Intelligent Astronomical & Lunisolar Festival Calendar & Host Events
- **Dynamic Lunisolar Calculations**: Calculates astronomical festivals whose dates change annually based on moon phases and lunar calendars (e.g. Diwali, Holi, Eid-ul-Fitr, Eid-ul-Adha, Ganesh Chaturthi, Maha Shivratri, Raksha Bandhan, Durga Puja, Chhath Puja) across 2025, 2026, and 2027.
- **Fixed Solar & Gregorian Observances**: Tracks New Year's Day, Republic Day, Independence Day, Gandhi Jayanti, Christmas, and international days.
- **⚡ Quick Random Test Event Generator**: Instant one-click test event button to verify system publishing, creative synthesis, and platform connectivity in real-time.
- **➕ Host Custom & Milestone Event Creator**: Allows hosts to create custom brand milestones, company anniversaries, and cultural events with optional instant auto-publishing to Instagram or LinkedIn.
- **Multi-Signal Bayesian Relevance Scoring**: Computes an account-specific relevance score based on:
  - Account industry niche & target audience.
  - Historical posting frequency during that festival.
  - Regional and cultural alignment.
- **Customizable Tracking**: Allows users to toggle specific festivals between `TRACKED` and `MUTED`.

### 3. Deterministic Pillow Graphic Compositor (No Hallucinations)
- **Eliminates AI Spelling Errors**: Standard generative image models frequently misspell Devanagari text, English greetings, and brand names. FestiveAI uses a deterministic Python Pillow compositor that draws crisp typography, authentic cultural motifs, gradient backdrops, and brand logos at pixel precision.
- **Standardized Aspect Ratios**: Generates $1080 \times 1080$ square posts for Instagram feeds and $1200 \times 628$ landscape posts for LinkedIn updates.
- **Logo Watermarking**: Automatically overlays the brand's uploaded high-res transparent PNG/SVG logo into the configured corner with proper margins.
- **Instant Preview & Customization**: Live preview in the Content Studio with one-click regeneration and manual adjustments.

### 4. Multilingual Copywriting & Caption Synthesis
- **Culturally Authentic Greetings**: Produces warm, respectful messages incorporating festival themes (prosperity for Diwali, joy and unity for Eid, vibrant colors for Holi, gratitude for Thanksgiving).
- **Host Persona Conditioning**: Seamlessly weaves the host's tone (e.g., blending tech innovation with Diwali light motifs).
- **Multilingual Support**: Supports English, pure Hindi (हिंदी), and Hinglish (conversational Romanized Hindi).
- **Smart Hashtag Curation**: Dynamically suggests top-ranking festival and industry hashtags.
- **Anti-Spam Safety**: Strictly filters out commercial jargon to maintain dignity and authenticity.

### 5. Autonomous Publishing Engine & Zero-Duplicate Safety
- **Dual Operating Modes**:
  - **Autonomous Mode (Hands-Off)**: The system periodically checks the upcoming festival horizon (e.g., 7 days ahead), generates the creative, runs verification checks, and publishes automatically at the designated local time (e.g., 09:00:00 IST).
  - **Approval Mode (Human-in-the-Loop)**: The system generates creatives in advance and stages them as `generated`. They will only be published after an administrator clicks **Approve Campaign** in Content Studio.
- **Zero-Duplicate Database Lock**: Backed by database-enforced unique constraints:
  ```sql
  CONSTRAINT uq_account_festival_year UNIQUE (social_account_id, festival_id, year)
  ```
- **Idempotent State Machine**: State transitions follow a strict lifecycle:
  $$\text{Draft} \longrightarrow \text{Generated} \longrightarrow \text{Approved} \longrightarrow \text{Scheduled} \longrightarrow \text{Published}$$
- **Exponential Backoff**: Automatic retry policies with configurable retry counts (1 to 5) and error logging.

### 6. Full-Device Responsiveness (Mobile, Tablet, Laptop, Desktop)
- **Mobile Navigation Drawer**: Sliding drawer with backdrop overlay for screens $< 768\text{px}$, accessible via a clean hamburger toggle.
- **Compact Navbar Actions**: Account picker and "Trigger Pipeline" adaptively collapse on narrow screens.
- **Fluid Layouts**: KPI metric grids adapt (`grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`), modals auto-scroll vertically (`max-h-[90vh]`), and tables support touch-friendly horizontal scrolling (`overflow-x-auto min-w-[640px]`).

---

## 📱 User Interface & Page Overview

FestiveAI includes 7 dedicated, production-grade pages:

| Page | Description | Key Capabilities |
| :--- | :--- | :--- |
| **Command Overview** | Real-time command dashboard | Next festival countdown banner, 4 KPI metric cards, upcoming festival pipeline, active account cards, one-click studio access. |
| **Connected Accounts** | OAuth & account manager | Connect Instagram / LinkedIn or instant Sandbox mock accounts, post type breakdown inspector, sync status, re-analysis trigger. |
| **Brand & Style Profile** | Visual & writing style tuner | Host persona selector, visual archetype cards, 5-color hex picker, logo uploader, formality slider, emoji frequency, sign-off rules. |
| **Festival Calendar** | Lunisolar & solar tracker | Astronomical dates, search & category filters, countdown timers, relevance scores, one-click studio launch, mute/track toggles. |
| **Content Studio** | Creative generation canvas | Live $1080 \times 1080$ preview, persona post archetype switcher, caption editor, curated hashtags, immediate publishing trigger. |
| **Automation Rules** | Autonomous pipeline controls | Toggle Autonomous vs. Approval mode, lead window slider (1–21 days), target publishing time, timezone picker, retry limits. |
| **Publishing History** | Immutable audit trail | Searchable and filterable history table, campaign identifiers, target timestamps, delivery statuses, verified platform post IDs. |

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.13) — High performance, asynchronous, automated OpenAPI/Swagger generation |
| **Database & ORM** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) with [Alembic](https://alembic.sqlalchemy.org/) — Unified SQLite / PostgreSQL support |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) — Strict typing and schema serialization |
| **Security & Auth** | [PyJWT](https://pyjwt.readthedocs.io/), [Passlib / Bcrypt](https://passlib.readthedocs.io/), [Cryptography (Fernet AES-128)](https://cryptography.io/) |
| **Background Scheduler** | [APScheduler](https://apscheduler.readthedocs.io/) — Timezone-aware cron & interval background job orchestration |
| **Graphics Compositor** | [Pillow (PIL)](https://python-pillow.org/) — Deterministic high-resolution image rendering and compositing |
| **Frontend Framework** | [React 19](https://react.dev/) with [TypeScript](https://www.typescriptlang.org/) and [Vite 6](https://vitejs.dev/) |
| **Styling & Icons** | [Tailwind CSS 3.4](https://tailwindcss.com/) & [Lucide React](https://lucide.dev/) |
| **HTTP Client** | [Axios](https://axios-http.com/) with typed interceptors and global error handling |
| **Containerization** | Multi-stage production [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) |
| **Cloud Hosting** | [Render.com](https://render.com/) — Unified single-service full-stack deployment |

---

## 🔌 REST API Documentation

The complete interactive Swagger documentation is available live at **[https://festiveai-2b3x.onrender.com/docs](https://festiveai-2b3x.onrender.com/docs)**.

### Key API Endpoints

```http
# System & Health
GET    /health                               # Backend health check and version info
GET    /api/v1/analytics/overview             # Aggregate KPI metrics and account stats

# Authentication
POST   /api/v1/auth/register                 # Register new organization & admin
POST   /api/v1/auth/login                    # JWT authentication
GET    /api/v1/auth/me                       # Current user profile

# Connected Accounts
GET    /api/v1/accounts                      # List connected accounts
POST   /api/v1/accounts/mock-connect         # Instant Sandbox account with historical data
POST   /api/v1/accounts/{id}/analyze         # Trigger AI historical profile analysis
GET    /api/v1/accounts/{id}/historical-posts# Retrieve ingested historical posts
DELETE /api/v1/accounts/{id}                 # Disconnect account

# Style Profile & Host Persona
GET    /api/v1/style-profile/{account_id}    # Retrieve learned visual & persona profile
PUT    /api/v1/style-profile/{account_id}    # Calibrate colors, persona, tone, rules
POST   /api/v1/style-profile/{account_id}/logo # Upload brand watermark logo (PNG/SVG)

# Festival Calendar & Custom Host Events
GET    /api/v1/calendar/festivals            # All cataloged astronomical festivals
GET    /api/v1/calendar/upcoming             # Upcoming festivals with account relevance
POST   /api/v1/calendar/custom-event         # Host custom event creation with optional auto-publish
POST   /api/v1/calendar/random-test-event    # Instant random test event generation & live social publishing
PUT    /api/v1/calendar/preference/{acc_id}/{fest_id} # Toggle mute/track preference

# Campaigns & Content Studio
GET    /api/v1/campaigns                     # List all campaigns
POST   /api/v1/campaigns/generate            # Synthesize deterministic creative & copy
PUT    /api/v1/campaigns/{id}                # Update caption & hashtags
POST   /api/v1/campaigns/{id}/approve        # Approve campaign for publishing
POST   /api/v1/campaigns/{id}/publish        # Immediately publish post to social platform

# Automation Rules
GET    /api/v1/automation/{account_id}       # Retrieve autonomous rules & lead windows
PUT    /api/v1/automation/{account_id}       # Update operating mode, time, timezone
POST   /api/v1/automation/trigger-cycle      # Manually run the autonomous cycle
```

---

## 💻 Local Development Setup

### Prerequisites
- **Python 3.11+** (or [uv](https://astral.sh/uv))
- **Node.js 18+** & **npm**

### 1. Clone the Repository
```bash
git clone https://github.com/Adarshthakur-850/FestiveAI.git
cd FestiveAI
```

### 2. Environment Configuration
Copy the sample environment file:
```bash
cp .env.example .env
```
*(The defaults are pre-configured to run out of the box with SQLite and Sandbox mode!)*

### 3. Backend Setup
```bash
# Set up Python virtual environment and dependencies
python -m venv backend/.venv
# On Windows:
.\backend\.venv\Scripts\activate
# On Linux/macOS:
source backend/.venv/bin/activate

pip install -r backend/requirements.txt

# Run the database seeder and initialize festivals
python -c "
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

# Start FastAPI backend
python backend/run.py
```
*Backend will start at `http://localhost:8000` with Swagger docs at `http://localhost:8000/docs`.*

### 4. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```
*Frontend will be running at `http://localhost:5173`.*

---

## 🐳 Running with Docker

Run the entire full-stack application with Docker Compose:

```bash
docker-compose up --build -d
```

- **Frontend App**: `http://localhost`
- **Backend API Docs**: `http://localhost:8000/docs`
- **PostgreSQL**: `localhost:5432`

---

## 🧪 Automated Testing

FestiveAI includes a comprehensive unit and integration test suite:

```bash
# Run pytest with detailed verbose output
pytest backend/tests -v
```

**Key Test Coverage (13 Tests, 100% Passing)**:
- `test_festival_catalog_astronomical_dates`: Verifies annual lunisolar shifts for Diwali and Holi across 2025–2027.
- `test_calculate_publish_datetime_timezone_awareness`: Tests UTC conversion across global timezones.
- `test_festival_classifier_diwali`: Validates multi-signal NLP and hashtag classification for past greetings.
- `test_writing_style_analysis_formality`: Tests formality calculation, emoji metrics, and language detection.
- `test_greeting_compositor_generates_valid_image`: Ensures Pillow outputs valid, uncorrupted, high-res images.
- `test_campaign_duplicate_prevention_and_idempotency`: Verifies database constraints and prevents duplicate posts.
- `test_health_check_endpoint` & `test_auth_registration_and_login`: Tests core API endpoints.
- `test_custom_event_and_auto_publishing`: Validates custom host event creation, creative synthesis, and platform publishing.
- `test_random_test_event_auto_publishing`: Verifies random test event generation and instantaneous Instagram/LinkedIn delivery.
- `test_host_persona_and_post_pillar_classification`: Confirms host persona classification and content pillar distribution.

---

## 🔒 Security & Data Integrity

- **Fernet Token Encryption**: All stored OAuth tokens and platform refresh tokens are encrypted at rest using AES-128-CBC with HMAC-SHA256.
- **Zero Logging of Secrets**: Sensitive tokens and credentials are automatically stripped from log outputs.
- **Multi-Tenant Isolation**: Strict organization-level filtering prevents cross-tenant data access.
- **Enterprise Safety**: Dual duplicate protection via database constraints and in-memory locks.

---

## 📄 License
This project is licensed under the [MIT License](LICENSE).

---

<p align="center">
  <b>FestiveAI</b> — Engineered for cultural authenticity, brand consistency, and autonomous peace of mind. 🪔✨<br>
  Explore the live app: <a href="https://festiveai-2b3x.onrender.com/">https://festiveai-2b3x.onrender.com/</a>
</p>