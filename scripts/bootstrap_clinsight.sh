#!/bin/bash
# ════════════════════════════════════════════════════════════
# One-shot boot-strap for ClinSight on new droplet
# Run this ONCE on droplet: bash /tmp/bootstrap_clinsight.sh
# ════════════════════════════════════════════════════════════
set -euo pipefail

LOG="/var/log/clinsight_bootstrap.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== $(date) Bootstrap Start ==="

# ─── 1. Ensure containers are running ──────────────────────
echo "━━━ 1/5: Ensure containers ━━━"
docker start rocm 2>/dev/null || true
docker start clinsight 2>/dev/null || true
sleep 3
docker ps --format '{{.Names}}' | grep rocm >&1 || echo "WARNING: rocm not running"
docker ps --format '{{.Names}}' | grep clinsight >&1 || echo "WARNING: clinsight not running"

# ─── 2. Install deps in clinsight ────────────────────────────
echo "━━━ 2/5: Install Python dependencies ━━━"
docker exec clinsight bash -c '
  apt-get update -qq >/dev/null 2>&1
  pip install -q fastapi uvicorn pydantic pydantic-settings pillow httpx requests jinja2 >/dev/null 2>&1
  python3 -c "import fastapi, uvicorn, pydantic, pydantic_settings, jinja2; print(\"deps_all_ok\")"
'

# ─── 3. Ensure code is in container ────────────────────────
echo "━━━ 3/5: Sync code from host shared folder ━━━"
docker cp /shared-docker/clinsight/backend/. clinsight:/opt/clinsight/backend/ 2>&1 || true
docker cp /shared-docker/clinsight/frontend/. clinsight:/opt/clinsight/frontend/ 2>&1 || true
docker exec clinsight bash -c '
  touch /opt/clinsight/backend/__init__.py
  touch /opt/clinsight/backend/api/__init__.py
  touch /opt/clinsight/backend/data/__init__.py
  touch /opt/clinsight/backend/core/__init__.py
  touch /opt/clinsight/backend/agents/__init__.py
  touch /opt/clinsight/backend/inference/__init__.py
'
echo "Code synced"

# ─── 4. Start backend ──────────────────────────────────────
echo "━━━ 4/5: Start backend ━━━"
docker exec clinsight bash -c '
  export PYTHONPATH=/opt/clinsight
  cd /opt/clinsight
  pkill -f uvicorn 2>/dev/null || true
  sleep 1
  nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 > /tmp/backend.log 2>&1 &
  sleep 3
  curl -s http://127.0.0.1:3000/health 2>&1 || echo "BACKEND_NOT_YET"
  # Now run a quick demo to confirm
  sleep 2
  curl -s http://127.0.0.1:3000/judge/transparency 2>&1 | head -c 80 || echo "JUDGE_NOT_YET"
'

# ─── 5. Health check from host ──────────────────────────────
echo "━━━ 5/5: Host-side verification ━━━"
sleep 2
curl -s http://127.0.0.1:3000/health 2>&1 | head -c 80 || echo "HOST_BACKEND_FAIL"
echo ""
curl -s http://127.0.0.1:3000/judge/transparency 2>&1 | head -c 80 || echo "HOST_JUDGE_FAIL"

echo ""
echo "=== $(date) Bootstrap DONE ==="
echo "Frontend: http://$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address):3000/"
echo "API:      http://$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address):3000/judge/transparency"
echo "Log:      tail -f /var/log/clinsight_bootstrap.log"
