# ==============================================================================
# FestiveAI Production Unified Dockerfile (Full-Stack Single-Container)
# ==============================================================================
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

# Copy pre-compiled production React frontend distribution
COPY frontend/dist ./frontend/dist

# Ensure media storage directories exist
RUN mkdir -p media/uploads media/generated

EXPOSE 8000

# Start Uvicorn bound to dynamic Render $PORT or 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
