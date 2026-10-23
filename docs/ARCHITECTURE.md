# FestiveAI: Technical Architecture & System Design

## 1. System Overview
FestiveAI is an end-to-end autonomous social media marketing platform. It connects with authorized Instagram and LinkedIn accounts, ingests and classifies historical posts, learns recurring visual styling and writing habits, tracks a verified multi-cultural festival calendar, synthesizes original personalized greeting graphics with exact brand typography and logo overlays, and publishes them autonomously on schedule with duplicate prevention and failure recovery.

```
+-----------------------------------------------------------------------------------+
|                                 FESTIVEAI PLATFORM                                |
+-----------------------------------------------------------------------------------+
|  [React 19 + TypeScript + Vite Dashboard]  <--->  [FastAPI REST API v1]           |
|                                                          |                        |
|  +--------------------+  +-------------------------+     |                        |
|  | Ingestion Service  |  | AI Profile Analysis     | <---+                        |
|  | (API & JSON Sync)  |  | (Vision & NLP Learner)  |                              |
|  +--------------------+  +-------------------------+                              |
|             |                         |                                           |
|             v                         v                                           |
|  +-------------------------------------------------+                              |
|  | Persistent Brand Style Profile (SQLAlchemy 2.0) |                              |
|  +-------------------------------------------------+                              |
|                         |                                                         |
|                         v                                                         |
|  +--------------------+  +-------------------------+  +------------------------+  |
|  | Lunisolar Calendar |  | Relevance Engine        |  | Creative Compositor    |  |
|  | (Ephemeris Dates)  |  | (Bayesian Affinity)     |  | (Pillow Deterministic) |  |
|  +--------------------+  +-------------------------+  +------------------------+  |
|             |                         |                           |               |
|             +-------------------------+---------------------------+               |
|                                       v                                           |
|  +-----------------------------------------------------------------------------+  |
|  | Autonomous Orchestration & Duplicate Gatekeeper (Idempotency Locks)         |  |
|  +-----------------------------------------------------------------------------+  |
|                         |                               |                         |
|                         v                               v                         |
|             [Instagram Graph API]              [LinkedIn UGC API]                 |
+-----------------------------------------------------------------------------------+
```

## 2. Core Subsystems

### 2.1 Ingestion & Analysis Engine
- **Multi-Signal Classification**: Combines greeting cue detection, festival keyword matchers, hashtag taxonomy, and date proximity.
- **Visual Style Learning**: Extracts dominant & secondary 5-color palettes using k-means/RGB analysis, identifies logo placement conventions, and saves aspect ratios (1:1 for Instagram, 1.91:1 for LinkedIn).
- **Writing Style Extraction**: Analyzes sentence length, formality index, emoji frequency, multilingual preferences (EN, HI, Hinglish), and mandatory brand sign-offs.

### 2.2 Lunisolar Festival Calendar
- Calculates dynamic dates for Hindu lunisolar festivals (Diwali, Holi, Durga Puja, Raksha Bandhan, Ganesh Chaturthi, Onam, Pongal), Islamic lunar Hijri festivals (Eid al-Fitr, Eid al-Adha), and Gregorian fixed events (Christmas, New Year, Independence Day).
- Accurately converts target publication times into UTC timestamps using local timezones (e.g. `Asia/Kolkata`).

### 2.3 Deterministic Graphics Compositor
- Solves AI image generation spelling hallucinations by rendering exact festival greetings, drop shadows, and brand watermarks via Pillow deterministic graphics composition onto rich cultural gradient backgrounds.
- Enforces brand logo preservation with alpha-channel compositing.

### 2.4 Autonomous Publishing & Duplicate Prevention
- Guaranteed Idempotency: Unique constraint on `(social_account_id, festival_id, year)` prevents duplicate campaigns.
- Dual Operating Modes:
  - **Autonomous Mode**: Content is automatically synthesized and published without human intervention.
  - **Approval Mode**: Content is prepared in advance and awaits review in Content Studio.
- Exponential backoff retry handler for transient API network faults.
