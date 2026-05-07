#!/bin/bash
# ════════════════════════════════════════════════════════════
# ONE-TIME FIX: Make droplet boot-ready from snapshot
# Run this ONCE per droplet, snapshot, then every recreate = instant
# ════════════════════════════════════════════════════════════
set -e

DROplet="134.199.193.58"
KEY="/workspace/.ssh/id_ed25519"
SSH="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $KEY root@$DROplet"

echo "=== STEP 1/7: Stop all running containers ==="
$SSH 'docker stop $(docker ps -q) 2>/dev/null || true; sleep 2; docker ps --format "{{.Names}}" | head -5'

echo ""
echo "=== STEP 2/7: Create persistent directories on host ==="
$SSH '
  mkdir -p /shared-docker/hf_cache /shared-docker/clinsight /shared-docker/vllm_logs
  chmod -R 777 /shared-docker/hf_cache /shared-docker/clinsight /shared-docker/vllm_logs
  chown -R root:root /shared-docker
'

echo ""
echo "=== STEP 3/7: Copy model cache from containers to host ==="
$SSH '
  # Try to copy any cached models from rocm container
  docker cp rocm:/root/.cache/huggingface/hub/. /shared-docker/hf_cache/ 2>&1 || true
  # Try from clinsight too
  docker cp clinsight:/root/.cache/huggingface/hub/. /shared-docker/hf_cache/ 2>&1 || true
  # Show what we got
  echo "Host cache size:"
  du -sh /shared-docker/hf_cache/* 2>&1 | sort -rh | head -5
  echo "Total:"
  du -sh /shared-docker/hf_cache 2>&1
'

echo ""
echo "=== STEP 4/7: Copy latest clinsight code to host ==="
# First, fix container clinsight to have latest code
cat /opt/clinsight/scripts/start_stack.sh | $SSH 'cat && docker cp /opt/clinsight/scripts/start_stack.sh clinsight:/tmp/'

# Now copy code from container to host (so we can mount it)
$SSH '
  docker cp clinsight:/opt/clinsight/. /shared-docker/clinsight/ 2>&1 || true
  ls -la /shared-docker/clinsight/backend/api/main.py 2>&1 | head -1
'

echo ""
echo "=== STEP 5/7: Recreate containers with auto-restart + persistent mounts ==="

# Remove old
$SSH 'docker rm -f rocm clinsight 2>/dev/null || true'

# Recreate rocm with GPU + cache mount + auto-restart
$SSH '
  docker run -d \
    --name rocm \
    --restart unless-stopped \
    --network host \
    --privileged \
    --device /dev/kfd --device /dev/dri \
    -v /shared-docker/hf_cache:/root/.cache/huggingface \
    -v /shared-docker/vllm_logs:/tmp \
    -e HF_HOME=/root/.cache/huggingface \
    rocm:latest \
    bash -c "sleep infinity"
  sleep 2
  docker ps --format "{{.Names}} {{.Status}}" | grep rocm
'

# Create clinsight container with code mount + backend auto-start
$SSH '
  docker run -d \
    --name clinsight \
    --restart unless-stopped \
    --network host \
    -v /shared-docker/clinsight:/opt/clinsight \
    -v /tmp:/tmp \
    -e PYTHONPATH=/opt/clinsight \
    ubuntu:22.04 \
    bash -c "apt-get update -qq && apt-get install -y -qq python3 python3-pip curl unzip git >/dev/null 2>&1 && pip install -q fastapi uvicorn pydantic pillow httpx requests >/dev/null 2>&1 && cd /opt/clinsight && python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error"
  sleep 3
  docker ps --format "{{.Names}} {{.Status}}" | grep clinsight
'

echo ""
echo "=== STEP 6/7: Create systemd service for full auto-start on boot ==="
$SSH '
  cat > /etc/systemd/system/clinsight.service <> EOF
[Unit]
Description=ClinSight Multi-Agent Stack
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c "
  echo \"$(date) ClinSight auto-start...\" >> /var/log/clinsight.log
  docker start rocm >> /var/log/clinsight.log 2>&1 || true
  sleep 5
  docker start clinsight >> /var/log/clinsight.log 2>&1 || true
  sleep 10
  curl -s http://127.0.0.1:3000/health >> /var/log/clinsight.log 2>&1 || echo HEALTH_FAIL
  echo \"$(date) ClinSight ready\" >> /var/log/clinsight.log
"
ExecStop=/bin/bash -c "docker stop clinsight rocm 2>/dev/null || true"
TimeoutStartSec=120

[Install]
WantedBy=multi-user.target
EOF

  systemctl daemon-reload
  systemctl enable clinsight.service
  systemctl start clinsight.service || true
  sleep 2
  echo "--- systemd status ---"
  systemctl status clinsight --no-pager --lines=3 2>&1 | head -10
'

echo ""
echo "=== STEP 7/7: Health check ==="
$SSH '
  sleep 3
  echo "=== Containers ==="
  docker ps --format "{{.Names}} {{.Status}}"
  echo ""
  echo "=== Backend ==="
  curl -s http://127.0.0.1:3000/health 2>&1 || echo BACKEND_NOT_READY
  echo ""
  echo "=== vLLM text (8000) ==="
  curl -s -m 2 http://127.0.0.1:8000/v1/models 2>&1 | head -c 50 || echo NOT_RUNNING
  echo ""
  echo "=== vLLM vision (8001) ==="
  curl -s -m 2 http://127.0.0.1:8001/v1/models 2>&1 | head -c 50 || echo NOT_RUNNING
'

echo ""
echo "=========================================="
echo "DONE. Now take snapshot via DO console:"
echo "  https://cloud.digitalocean.com/droplets"
echo "  Power Off → Snapshots → 'clinsight-prod-fixed'"
echo ""
echo "AFTER THIS SNAPSHOT, every recreate:"
echo "  1. Boot droplet from snapshot"
echo "  2. Wait 30 seconds"
echo "  3. Everything auto-starts (systemd + docker restart)"
echo "  4. Models persist in /shared-docker/hf_cache (host mount)"
echo "=========================================="
