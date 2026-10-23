# ==============================================================================
# FestiveAI Production Multi-Stage Dockerfile (Full-Stack Unified Container)
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Build Frontend SPA (React + TypeScript + Vite + TailwindCSS)
# ------------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
# Use relative API path for unified single-origin deployment
ENV VITE_API_URL=/api/v1
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 2: Production Python Backend & Static Server
# ------------------------------------------------------------------------------
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/backend

# Install OS libraries for Pillow image rendering, fonts, and networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install Python backend dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --upgrade pip && pip install -r backend/requirements.txt

# Copy backend code
COPY backend ./backend

# Copy compiled frontend from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Ensure media storage directories exist
RUN mkdir -p media/uploads media/generated

EXPOSE 8000

# Start Uvicorn bound to Render dynamic $PORT or 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
