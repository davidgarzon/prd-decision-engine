#!/usr/bin/env bash
set -euo pipefail

# ── Configuration ────────────────────────────────────────────────────────────
BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "==> Health check"
curl -s "${BASE_URL}/health" | python3 -m json.tool
echo

echo "==> Fetching review output schema"
curl -s "${BASE_URL}/schema" | python3 -m json.tool
echo

echo "==> Submitting PRD for review (mock mode)"
curl -s -X POST "${BASE_URL}/review" \
  -H "Content-Type: application/json" \
  -d @"${SCRIPT_DIR}/review_request.json" \
  | python3 -m json.tool
echo

echo "Done."
