#!/bin/bash
cd /opt/clinsight
pkill -f uvicorn 2>/dev/null
sleep 1
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error > /tmp/backend.log 2>&1 &
PID=$!
sleep 2
HEALTH=$(curl -s http://127.0.0.1:3000/health || echo FAIL)
JUDGE=$(curl -s http://127.0.0.1:3000/judge/accuracy/CS-2024-001 | head -c 100 || echo JUDGE_FAIL)
echo "PID=$PID HEALTH=$HEALTH JUDGE=$JUDGE"
