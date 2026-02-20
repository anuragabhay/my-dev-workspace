#!/usr/bin/env bash
# Start API (uvicorn) and frontend dev server in parallel.
# Usage: ./run_dev.sh
# Requires: venv activated, npm deps installed in frontend/

set -e
cd "$(dirname "$0")"

# Ensure we're in project root
if [ ! -d "src" ] || [ ! -d "frontend" ]; then
  echo "Error: run from youtube-shorts-generator root"
  exit 1
fi

# Start API in background
echo "Starting API on http://localhost:8000"
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

# Start frontend
echo "Starting frontend on http://localhost:5173"
cd frontend && npm run dev &
FRONT_PID=$!

cleanup() {
  kill $API_PID 2>/dev/null || true
  kill $FRONT_PID 2>/dev/null || true
}
trap cleanup EXIT

wait
