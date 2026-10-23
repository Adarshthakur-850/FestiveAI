import asyncio
import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.db.session import engine, SessionLocal
from app.db.migrate import auto_migrate_db
from app.models import Base
from app.api.v1 import api_router
from app.services.calendar_service import CalendarService
from app.services.scheduler_service import SchedulerService

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FestiveAI")

async def background_scheduler_worker():
    """Background task running the autonomous cycle periodically."""
    logger.info("FestiveAI autonomous background scheduler worker started.")
    while True:
        try:
            db = SessionLocal()
            try:
                summary = SchedulerService.run_automation_cycle(db)
                if summary["campaigns_generated"] > 0 or summary["campaigns_published"] > 0:
                    logger.info(f"Autonomous cycle results: {summary}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error in scheduler background worker: {e}")
        await asyncio.sleep(settings.AUTONOMOUS_WORKER_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and seed initial festival definitions
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    auto_migrate_db(engine)
    
    db = SessionLocal()
    try:
        logger.info("Seeding festival definitions & multi-year astronomical observances...")
        CalendarService.seed_festival_definitions(db)
    finally:
        db.close()

    # Start scheduler background worker
    scheduler_task = asyncio.create_task(background_scheduler_worker())

    yield

    # Shutdown
    scheduler_task.cancel()
    logger.info("FestiveAI backend shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Social Media Profile Analysis, Personalized Festival Greeting Generation, and Autonomous Publishing Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve generated creatives and uploaded brand logos
app.mount("/static", StaticFiles(directory=settings.MEDIA_ROOT), name="static")

# Mount API routers
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }

@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "documentation": "/docs",
        "version": settings.VERSION
    }
