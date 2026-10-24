import asyncio
import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import settings
from app.db.session import engine, SessionLocal
from app.db.migrate import auto_migrate_db
from app.models import Base
from app.api.v1 import api_router
from app.services.calendar_service import CalendarService
from app.services.scheduler_service import SchedulerService

import threading
import time

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("FestiveAI")

def background_scheduler_worker():
    """Background daemon thread running the autonomous cycle periodically."""
    logger.info("FestiveAI autonomous background scheduler worker started.")
    time.sleep(5)
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
        time.sleep(settings.AUTONOMOUS_WORKER_INTERVAL_SECONDS)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure media directories exist
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    os.makedirs(settings.STATIC_UPLOADS, exist_ok=True)
    os.makedirs(settings.GENERATED_ASSETS, exist_ok=True)

    # Startup: Create tables and seed initial festival definitions
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    auto_migrate_db(engine)
    
    db = SessionLocal()
    try:
        logger.info("Seeding festival definitions & multi-year astronomical observances...")
        CalendarService.seed_festival_definitions(db)
        logger.info("Bootstrapping default demo workspace, user, and active account...")
        from app.api.deps import bootstrap_system_demo_data
        bootstrap_system_demo_data(db)
    finally:
        db.close()

    # Start scheduler background worker only in persistent server environments (not serverless or testing)
    is_test = "pytest" in sys.modules or os.environ.get("TESTING") == "1"
    is_serverless = os.environ.get("VERCEL") == "1" or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") is not None
    if not is_serverless and not is_test:
        worker_thread = threading.Thread(target=background_scheduler_worker, daemon=True, name="FestiveAI-Scheduler")
        worker_thread.start()

    yield

    logger.info("FestiveAI backend shutdown complete.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-Powered Social Media Profile Analysis, Personalized Festival Greeting Generation, and Autonomous Publishing Platform",
    lifespan=lifespan
)

# CORS Middleware
origins = [o for o in settings.BACKEND_CORS_ORIGINS if o != "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https?://.*",
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

# Resolve frontend dist directory for unified full-stack serving
frontend_dist_dirs = [
    os.path.join(os.getcwd(), "frontend", "dist"),
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "dist"),
    os.path.join(os.getcwd(), "dist"),
]

frontend_dist_path = None
for d in frontend_dist_dirs:
    if os.path.exists(d) and os.path.exists(os.path.join(d, "index.html")):
        frontend_dist_path = os.path.abspath(d)
        break

if frontend_dist_path:
    logger.info(f"Serving built React frontend from: {frontend_dist_path}")
    assets_dir = os.path.join(frontend_dist_path, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="frontend_assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("static") or full_path.startswith("redoc") or full_path in ("health", "docs", "openapi.json"):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        
        file_path = os.path.join(frontend_dist_path, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist_path, "index.html"))
else:
    @app.get("/", tags=["Root"])
    def root():
        return {
            "message": f"Welcome to {settings.PROJECT_NAME} API",
            "documentation": "/docs",
            "version": settings.VERSION
        }
