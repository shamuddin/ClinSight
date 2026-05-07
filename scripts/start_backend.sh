#!/bin/bash
# Start ClinSight backend (no backgrounding in terminal call - this script handles it)
cd /opt/clinsight
pkill -f 'uvicorn backend.api.main:app' 2>/dev/null || true
sleep 1
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error > /tmp/backend.log 2>&1 &
echo "BACKGROUND_PID=$!"
sleep 3
curl -s http://127.0.0.1:3000/health || echo HEALTH_CHECK_FAIL
ps aux | grep uvicorn | grep -v grep | wc -l
echo "DONE"
