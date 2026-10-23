import pytest
import os
import sys

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.db.session import get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test_festiveai.db"

@pytest.fixture(scope="session")
def test_db_engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("./test_festiveai.db"):
        try:
            os.remove("./test_festiveai.db")
        except Exception:
            pass

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    Session = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
