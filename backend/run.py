import uvicorn
import os
import sys

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("UVICORN_RELOAD", "false").lower() == "true"
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=reload)
