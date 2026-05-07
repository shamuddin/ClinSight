#!/bin/bash
cd /opt/clinsight
pkill -f uvicorn 2>/dev/null
sleep 2
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error > /tmp/backend.log 2>&1 &
BACK_PID=$!
sleep 3
HEALTH=$(curl -s http://127.0.0.1:3000/health || echo fail)
UV_COUNT=$(ps aux | grep uvicorn | grep -v grep | wc -l)
echo "PID=$BACK_PID HEALTH=$HEALTH UVICORNS=$UV_COUNT"
