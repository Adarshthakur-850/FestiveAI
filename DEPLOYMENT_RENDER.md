# FestiveAI - Render Cloud Deployment Guide

This guide explains how to create a **brand-new, high-performance Render hosting service** for the FestiveAI full-stack platform.

---

## Method 1: Instant 1-Click Deploy (Fastest)

Click the official Render deployment button below:

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Adarshthakur-850/FestiveAI)

**Direct Link**: [https://render.com/deploy?repo=https://github.com/Adarshthakur-850/FestiveAI](https://render.com/deploy?repo=https://github.com/Adarshthakur-850/FestiveAI)

Render automatically detects [`render.yaml`](render.yaml) in your repository and configures all settings, environment variables, build scripts, and automatic deployments.

1. Click the button or link above (make sure you are logged in at [Render](https://dashboard.render.com)).
2. Render will show the blueprint configuration for `festiveai-app`.
3. Click **Apply**.
4. Render will automatically:
   - Create a new web service named `festiveai-app`.
   - Run `./render-build.sh` to install dependencies.
   - Start the FastAPI backend with `uvicorn main:app --host 0.0.0.0 --port $PORT`.
   - Serve the React frontend and documentation.
   - Enable **Auto-Deploy** for all future pushes to `main`.

---

## Method 2: Manual Web Service Creation (Standard)

If you prefer to configure the service manually via the Render UI:

1. Go to the [Render Dashboard](https://dashboard.render.com/).
2. Click **New +** → **Web Service**.
3. Select **Build and deploy from a Git repository** → Choose `Adarshthakur-850/FestiveAI`.
4. Fill in the following fields:

| Configuration Field | Value to Enter |
| :--- | :--- |
| **Name** | `festiveai-app` (or your preferred name) |
| **Region** | `Oregon (US West)` or `Frankfurt (EU)` |
| **Branch** | `main` |
| **Root Directory** | *(Leave blank)* |
| **Runtime** | `Python 3` |
| **Build Command** | `./render-build.sh` *(or `pip install -r requirements.txt`)* |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| **Instance Type** | `Free` |

5. Under **Advanced Settings**:
   - **Health Check Path**: `/health`
   - **Auto-Deploy**: `Yes`
   - **Environment Variables**:
     - `ENVIRONMENT` = `production`
     - `DEBUG` = `false`
     - `DEFAULT_AI_PROVIDER` = `mock`
     - `DATABASE_URL` = `sqlite:///./festiveai.db`
     - `SECRET_KEY` = *(Click Generate)*
     - `ENCRYPTION_KEY` = `gAAAAABmFz-mockEncryptionKeyFestiveAI32BytesNeededForFernet=`
     - `PYTHON_VERSION` = `3.12.8`

6. Click **Create Web Service**.

---

## Verification After Deployment

Once the build completes (typically 45–60 seconds):
- **Health Check**: `https://<your-new-service-name>.onrender.com/health`
- **Frontend Application**: `https://<your-new-service-name>.onrender.com/`
- **Interactive API Docs**: `https://<your-new-service-name>.onrender.com/docs`
- **Automation Status**: `https://<your-new-service-name>.onrender.com/api/v1/automation/status`
