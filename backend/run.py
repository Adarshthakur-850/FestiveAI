import uvicorn
import os
import sys
import socket
import urllib.request
import json

# Ensure backend root is in PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def check_existing_festiveai(port: int) -> bool:
    try:
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/v1/health")
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            return data.get("service") == "FestiveAI"
    except Exception:
        return False

def free_port(port: int):
    """Safely terminates any orphaned process holding the target port on Windows."""
    try:
        import subprocess
        output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
        for line in output.strip().split("\n"):
            parts = [p for p in line.strip().split(" ") if p]
            if len(parts) >= 5 and "LISTENING" in line:
                pid = parts[-1]
                if int(pid) != os.getpid():
                    print(f"Terminating stale process {pid} on port {port}...", flush=True)
                    subprocess.call(f"taskkill /F /PID {pid}", shell=True)
    except Exception as e:
        print(f"Note on port check: {e}", flush=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    reload = os.environ.get("UVICORN_RELOAD", "false").lower() == "true"
    force_restart = os.environ.get("FORCE_RESTART", "false").lower() == "true"

    if is_port_in_use(port):
        if check_existing_festiveai(port) and not force_restart:
            print(f"=== FestiveAI Backend is ALREADY actively running on http://localhost:{port} ===", flush=True)
            print(f"- Health Endpoint: http://localhost:{port}/api/v1/health", flush=True)
            print(f"- API Documentation: http://localhost:{port}/docs", flush=True)
            print(f"- Frontend UI: http://localhost:5173", flush=True)
            print(f"To force a fresh restart, run with: $env:FORCE_RESTART='true'; python backend/run.py", flush=True)
            sys.exit(0)
        else:
            print(f"Port {port} is occupied. Freeing port for fresh startup...", flush=True)
            free_port(port)

    print(f"Starting FestiveAI backend on 0.0.0.0:{port} (reload={reload})...", flush=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=reload, log_level="info")
