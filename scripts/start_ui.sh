#!/bin/bash
# Start ClinSight backend + frontend inside clinsight container
export USE_MOCK=false
export VLLM_VISION_URL=http://127.0.0.1:8000/v1
export VLLM_TEXT_URL=http://127.0.0.1:8001/v1
export HF_HOME=/mnt/scratch/hf_cache

# Kill old servers
pkill -f "python3.*uvicorn" 2>/dev/null || true
pkill -f "python3.*http.server" 2>/dev/null || true
sleep 2

# Start backend API
cd /opt/clinsight
python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 > /tmp/backend.log 2>&1 &
echo "Backend PID: $!"
sleep 5

# Start frontend static server
cd /opt/clinsight/frontend/react-app/dist
python3 -m http.server 3001 > /tmp/frontend.log 2&& echo "Frontend PID: $!" &
sleep 3

echo "Servers started:"
ss -tlnp | grep -E ':3000|:3001' || echo 'check ports'
echo "--- Backend log tail ---"
tail -5 /tmp/backend.log || true
echo "--- Frontend log tail ---"
tail -5 /tmp/frontend.log || true
