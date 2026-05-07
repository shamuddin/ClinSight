#!/bin/bash
# ════════════════════════════════════════════════════════════
# Clinsight Droplet Setup Script — run ONCE on droplet host
# ════════════════════════════════════════════════════════════
set -euo pipefail

IP="$(curl -s http://169.254.169.254/metadata/v1/interfaces/public/0/ipv4/address 2>/dev/null || hostname -I | awk '{print $1}')"
LOG="/var/log/clinsight_setup.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== $(date) Setup on IP $IP ==="

# ─── 1. Persistent dirs ────────────────────────────────────
mkdir -p /shared-docker/hf_cache /shared-docker/vllm_logs /shared-docker/nginx
chmod -R 777 /shared-docker/hf_cache /shared-docker/vllm_logs /shared-docker/nginx

# ─── 2. Stop/remove old ────────────────────────────────────
docker stop rocm clinsight 2>/dev/null || true
docker rm -f rocm clinsight 2>/dev/null || true
echo "Old containers removed"

# ─── 3. Create rocm (GPU) ─────────────────────────────────
docker run -d \
  --name rocm \
  --restart unless-stopped \
  --network host \
  --privileged \
  --device /dev/kfd --device /dev/dri \
  --shm-size=16g \
  -e HF_HOME=/root/.cache/huggingface \
  -e HUGGINGFACE_HUB_CACHE=/root/.cache/huggingface/hub \
  -v /shared-docker/hf_cache:/root/.cache/huggingface:rw \
  rocm:latest \
  bash -c 'sleep infinity'

echo "rocm container: $(docker ps --format '{{.Names}}' | grep rocm)"

# ─── 4. Create clinsight (backend) ────────────────────────
docker run -d \
  --name clinsight \
  --restart unless-stopped \
  --network host \
  -e PYTHONPATH=/opt/clinsight \
  -e VLLM_VISION_URL=http://127.0.0.1:8000/v1 \
  -e VLLM_TEXT_URL=http://127.0.0.1:8001/v1 \
  ubuntu:22.04 \
  bash -c '
    apt-get update -qq && apt-get install -y -qq python3 python3-pip curl git > /dev/null 2>&1
    pip install -q fastapi uvicorn pydantic pillow httpx requests > /dev/null 2>&1
    while true; do
      cd /opt/clinsight 2>/dev/null && pkill -f uvicorn 2>/dev/null; sleep 2; python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level info > /tmp/backend.log 2>&1 &
      sleep 30
    done
    tail -f /tmp/backend.log
  '

echo "clinsight container: $(docker ps --format '{{.Names}}' | grep clinsight)"

# ─── 5. Systemd auto-start ─────────────────────────────────
cat > /etc/systemd/system/clinsight.service << 'SYSTEMD_EOF'
[Unit]
Description=ClinSight
After=docker.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c '
  docker start rocm 2>/dev/null || true
  docker start clinsight 2>/dev/null || true
  sleep 10
  docker exec clinsight bash -c "cd /opt/clinsight && pkill -f uvicorn 2>/dev/null; nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 > /tmp/backend.log 2>&1 &"
'
ExecStop=/bin/bash -c 'docker stop clinsight rocm 2>/dev/null || true'
[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

systemctl daemon-reload
systemctl enable clinsight.service
systemctl start clinsight.service

echo "=== $(date) Setup DONE ==="
echo "Containers:"
docker ps --format '{{.Names}} {{.Status}}' | grep -E 'rocm|clinsight'
echo "systemd: $(systemctl is-active clinsight)"
