#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

trap 'kill 0 2>/dev/null' EXIT

echo "==> Starting backend (FastAPI) on http://127.0.0.1:8000"
(cd "$ROOT" && source .venv/bin/activate && python -m uvicorn app.main:app --reload --port 8000) &

echo "==> Starting frontend (Next.js) on http://localhost:3000"
(cd "$ROOT/web" && npm run dev) &

wait
