#!/bin/bash
pkill -f uvicorn 2>/dev/null
sleep 2
cd /opt/clinsight
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error > /tmp/backend.log 2>&1 &
PID=$!
sleep 3
HEALTH=$(curl -s http://127.0.0.1:3000/health || echo FAIL)
JUDGE=$(curl -s http://127.0.0.1:3000/judge/accuracy/CS-2024-001 | python3 -c "import sys,json; d=json.load(sys.stdin); print(list(d.keys()))" 2>/dev/null || echo JUDGE_FAIL)
echo "HEALTH=$HEALTH JUDGE=$JUDGE"
