import pytest
import os
import sys

# Ensure backend root is on sys.path and set test environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["TESTING"] = "1"
os.environ["DATABASE_URL"] = "sqlite:///./test_festiveai.db"

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.db.session import engine as app_engine, SessionLocal, get_db
from app.services.calendar_service import CalendarService
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def init_test_database():
    """Ensure all database tables exist and seed definitions for tests."""
    Base.metadata.create_all(bind=app_engine)
    db = SessionLocal()
    try:
        CalendarService.seed_festival_definitions(db)
    finally:
        db.close()
    yield
    Base.metadata.drop_all(bind=app_engine)
    if os.path.exists("./test_festiveai.db"):
        try:
            os.remove("./test_festiveai.db")
        except Exception:
            pass

@pytest.fixture(scope="function")
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
