#!/bin/bash
# Start ClinSight stack on droplet (run on 134.199.193.58)
cd /opt/clinsight

# 1. Start backend directly (since container is stopped)
echo "=== Starting backend ==="
pkill -f uvicorn 2>/dev/null
sleep 1

export PYTHONPATH=/opt/clinsight:$PYTHONPATH
cd /opt/clinsight
nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level info > /tmp/backend.log 2>&1 &
echo "UVICORN_PID=$!"
sleep 3

# Health check
echo "=== Health check ==="
curl -s http://127.0.0.1:3000/health 2>&1 || echo "BACKEND_FAIL"

# 2. Check vLLM on ports 8000/8001
echo "=== vLLM check ==="
for port in 8000 8001; do
  curl -s -m 2 http://127.0.0.1:$port/v1/models 2>&1 | head -c 50 || echo "VLLM_${port}_FAIL"
done

echo "=== Done ==="
