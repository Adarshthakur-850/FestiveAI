import sys
import os

# Insert backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "backend")
sys.path.insert(0, os.path.abspath(backend_dir))

from app.main import app

app = app
