from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.accounts import router as accounts_router
from app.api.v1.ingestion import router as ingestion_router
from app.api.v1.profiles import router as profiles_router
from app.api.v1.calendar import router as calendar_router
from app.api.v1.campaigns import router as campaigns_router
from app.api.v1.studio import router as studio_router
from app.api.v1.automation import router as automation_router
from app.api.v1.analytics import router as analytics_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(accounts_router)
api_router.include_router(ingestion_router)
api_router.include_router(profiles_router)
api_router.include_router(calendar_router)
api_router.include_router(campaigns_router)
api_router.include_router(studio_router)
api_router.include_router(automation_router)
api_router.include_router(analytics_router)
