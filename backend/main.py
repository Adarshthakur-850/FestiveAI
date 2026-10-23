import sys
import os

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app

# Export for Vercel Serverless
app = app
