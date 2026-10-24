#!/usr/bin/env bash
# Exit immediately on error
set -o errexit

echo "=== FestiveAI Render Deployment Build ==="
echo "--- Installing Python Backend Dependencies ---"
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "--- Verifying Pre-Compiled Frontend Dist ---"
if [ ! -d "frontend/dist" ]; then
    echo "frontend/dist not found, building frontend with npm..."
    cd frontend
    npm install
    npm run build
    cd ..
else
    echo "Found pre-compiled frontend in frontend/dist."
fi

echo "=== FestiveAI Build Completed Successfully! ==="
