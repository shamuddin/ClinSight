#!/bin/bash
# ════════════════════════════════════════════════════════════
# COMPLETE DROPLET SETUP — Boot-Ready + Persistence
# Run this ONCE, snapshot, then every recreate = instant boot
# ════════════════════════════════════════════════════════════
set -euo pipefail

LOG="/var/log/clinsight_setup.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== $(date) ClinSight Full Setup Started ==="

# ─── CONFIG ────────────────────────────────────────────────
DROplet_IP="134.199.193.58"
KEY="/workspace/.ssh/id_ed25519"
SSH="ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i $KEY root@$DROplet_IP"

# ─── STEP 1: PREPARE HOST PERSISTENT DIRS ──────────────────
echo ""
echo "━━━ STEP 1/8: Create persistent directories on host ━━━"
$SSH '
  mkdir -p /shared-docker/hf_cache /shared-docker/clinsight /shared-docker/vllm_logs /shared-docker/nginx
  chmod -R 777 /shared-docker/hf_cache /shared-docker/clinsight /shared-docker/vllm_logs /shared-docker/nginx
  chown -R root:root /shared-docker
  echo "Host dirs created: /shared-docker/{hf_cache,clinsight,vllm_logs,nginx}"
'

# ─── STEP 2: COPY LATEST CODE TO HOST ─────────────────────
echo ""
echo "━━━ STEP 2/8: Sync latest code from local to host ━━━"

# Sync via pipe (no scp timeouts)
( cd /workspace && tar czf - \
    backend/core/accuracy.py \
    backend/data/ground_truth.py \
    backend/data/medical_transparency.py \
    backend/api/judge.py \
    backend/api/main.py \
    frontend/react-app/dist/ \
    scripts/start_vllm_vision.sh \
    scripts/start_vllm_text.sh \
    scripts/vllm_launcher.py \
    scripts/restart_final.sh \
    requirements.txt \
    2>/dev/null ) | $SSH 'cat > /tmp/latest_code.tar.gz && echo code_received'

# Extract to host persistent dir
$SSH '
  cd /shared-docker/clinsight && rm -rf ./* 2>/dev/null
  mkdir -p /shared-docker/clinsight
  tar xzf /tmp/latest_code.tar.gz -C /shared-docker/clinsight && echo code_extracted
  ls /shared-docker/clinsight/backend/api/ 2>&1 | head -5
'

# ─── STEP 3: COPY MODELS FROM CONTAIERS TO HOST ────────────
echo ""
echo "━━━ STEP 3/8: Copy model cache to host (persist across snapshots) ━━━"

$SSH '
  # Copy from existing containers if any
  docker exec rocm bash -c "cp -a /root/.cache/huggingface/hub/. /shared-docker/hf_cache/ 2>/dev/null || true" 2>&1 || true
  docker exec clinsight bash -c "cp -a /root/.cache/huggingface/hub/. /shared-docker/hf_cache/ 2>/dev/null || true" 2>&1 || true
  
  # Check what we have
  echo "Cache contents:"
  ls -la /shared-docker/hf_cache/ 2>/dev/null | head -10 || echo "(empty - will download)"
  du -sh /shared-docker/hf_cache 2>/dev/null || true
'

# ─── STEP 4: STOP/REMOVE OLD CONTAINERS ────────────────────
echo ""
echo "━━━ STEP 4/8: Stop and clean old containers ━━━"

$SSH '
  docker stop $(docker ps -q) 2>/dev/null || true
  sleep 2
  docker rm -f rocm clinsight 2>/dev/null || true
  sleep 1
  echo "Old containers removed."
'

# ─── STEP 5: CREATE ROCM + VLLM CONTAINER ──────────────────
echo ""
echo "━━━ STEP 5/8: Create rocm container (vLLM + GPU) ━━━"

$SSH '
  docker run -d \
    --name rocm \
    --restart unless-stopped \
    --network host \
    --privileged \
    --device /dev/kfd --device /dev/dri \
    --shm-size=16g \
    -v /shared-docker/hf_cache:/root/.cache/huggingface:rw \
    -v /shared-docker/clinsight:/opt/clinsight:rw \
    -v /shared-docker/vllm_logs:/tmp:rw \
    -e HF_HOME=/root/.cache/huggingface \
    -e HUGGINGFACE_HUB_CACHE=/root/.cache/huggingface/hub \
    rocm:latest \
    bash -c "sleep infinity"
  
  sleep 3
  echo "rocm container: $(docker ps --format "{{.Names}}" | grep rocm || echo NOT_RUNNING)"
'

# ─── STEP 6: CREATE CLINSIGHT BACKEND CONTAINER ────────────
echo ""
echo "━━━ STEP 6/8: Create clinsight container (backend) ━━━"

$SSH '
  # Create a Python image that auto-starts backend
  docker run -d \
    --name clinsight \
    --restart unless-stopped \
    --network host \
    -v /shared-docker/clinsight:/opt/clinsight:rw \
    -v /tmp:/tmp:rw \
    -e PYTHONPATH=/opt/clinsight \
    -e VLLM_VISION_URL=http://127.0.0.1:8000/v1 \
    -e VLLM_TEXT_URL=http://127.0.0.1:8001/v1 \
    ubuntu:22.04 \
    bash -c "
      apt-get update -qq && apt-get install -y -qq python3 python3-pip curl unzip git >/dev/null 2>&1 &&
      pip install -q fastapi uvicorn pydantic pillow httpx requests >/dev/null 2>&1 &&
      cd /opt/clinsight && 
      pkill -f uvicorn 2>/dev/null &&
      nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level info > /tmp/backend.log 2>&1 &
      sleep 2 &&
      tail -f /tmp/backend.log
    "
  
  sleep 5
  echo "clinsight container: $(docker ps --format "{{.Names}}" | grep clinsight || echo NOT_RUNNING)"
'

# ─── STEP 7: START VLLM SERVERS ────────────────────────────
echo ""
echo "━━━ STEP 7/8: Start vLLM servers (models will download to host cache) ━━━"

$SSH '
  # Start vision model (Qwen2.5-VL-7B) on port 8000
  docker exec rocm bash -c "
    export HF_HOME=/root/.cache/huggingface
    export HUGGINGFACE_HUB_CACHE=/root/.cache/huggingface/hub
    nohup bash /opt/clinsight/scripts/start_vllm_vision.sh > /shared-docker/vllm_logs/vllm_vision.log 2>&1 &
    echo vllm_vision_started_pid=\$!
  " || echo "vision_script_failed"
  
  sleep 2
  
  # Start text model (Qwen3.5-35B) on port 8001
  docker exec rocm bash -c "
    export HF_HOME=/root/.cache/huggingface
    export HUGGINGFACE_HUB_CACHE=/root/.cache/huggingface/hub
    nohup bash /opt/clinsight/scripts/start_vllm_text.sh > /shared-docker/vllm_logs/vllm_text.log 2>&1 &
echo vllm_text_started_pid=\$!
  " || echo "text_script_failed"
  
  sleep 2
  
  echo ""
  echo "vLLM processes:"
  docker exec rocm ps aux | grep -E "vllm|python" | grep -v grep | head -3 || echo "(still loading)"
'

# ─── STEP 8: SYSTEMD AUTO-START + HEALTH CHECK ─────────────
echo ""
echo "━━━ STEP 8/8: Install systemd auto-start + verify ━━━"

$SSH '
  cat > /etc/systemd/system/clinsight.service << "SYSTEMD_EOF"
[Unit]
Description=ClinSight Multi-Agent Stack
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c "
echo \"$(date) Starting ClinSight...\" >> /var/log/clinsight.log
# Ensure directories exist
mkdir -p /shared-docker/hf_cache /shared-docker/clinsight /shared-docker/vllm_logs
chown -R root:root /shared-docker

# Start rocm
docker start rocm >> /var/log/clinsight.log 2>&1 || true
sleep 5

# Start clinsight backend
docker start clinsight >> /var/log/clinsight.log 2>&1 || true
sleep 5
docker exec clinsight bash -c \"cd /opt/clinsight && pkill -f uvicorn 2>/dev/null; nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 > /tmp/backend.log 2>\u00261 &\" >> /var/log/clinsight.log 2>&1 || true
sleep 10

# Start vLLM inside rocm
docker exec rocm bash -c \"export HF_HOME=/root/.cache/huggingface; nohup bash /opt/clinsight/scripts/start_vllm_vision.sh > /shared-docker/vllm_logs/vllm_vision.log 2>\u00261 &\" >> /var/log/clinsight.log 2>&1 || true
sleep 5
docker exec rocm bash -c \"export HF_HOME=/root/.cache/huggingface; nohup bash /opt/clinsight/scripts/start_vllm_text.sh > /shared-docker/vllm_logs/vllm_text.log 2>\u00261 &\" >> /var/log/clinsight.log 2>&1 || true
sleep 15

# Health check
curl -s http://127.0.0.1:3000/health >> /var/log/clinsight.log 2>&1 || echo HEALTH_FAIL
echo \"$(date) ClinSight ready\" >> /var/log/clinsight.log
"
ExecStop=/bin/bash -c "docker stop clinsight rocm 2>/dev/null || true"
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
SYSTEMD_EOF

  systemctl daemon-reload
  systemctl enable clinsight.service
  systemctl start clinsight.service || true
  echo ""
  echo "systemd: $(systemctl is-active clinsight.service || echo unknown)"
'

# ─── FINAL HEALTH CHECK ────────────────────────────────────
echo ""
echo "━━━ FINAL STATUS ━━━"
$SSH '
  sleep 3
  echo "=== Containers ==="
  docker ps --format "{{.Names}} {{.Status}}" | grep -E "rocm|clinsight"
  echo ""
  echo "=== Backend ==="
  curl -s http://127.0.0.1:3000/health 2>&1 || echo BACKEND_NOT_READY
  echo ""
  echo "=== vLLM Vision (8000) ==="
  curl -s -m 2 http://127.0.0.1:8000/v1/models 2>&1 | python3 -m json.tool 2>&1 | head -5 || echo "VISION_NOT_READY (models may be downloading)"
  echo ""
  echo "=== vLLM Text (8001) ==="
  curl -s -m 2 http://127.0.0.1:8001/v1/models 2>&1 | python3 -m json.tool 2>&1 | head -5 || echo "TEXT_NOT_READY (models may be downloading)"
  echo ""
  echo "=== Host Cache Size ==="
  du -sh /shared-docker/hf_cache 2>&1 || true
'

echo ""
echo "=========================================="
echo "SETUP COMPLETE. $(date)"
echo ""
echo "NEXT STEPS:"
echo "1. Wait for vLLM model download (~10-20 min first time)"
echo "   Watch: tail -f /var/log/clinsight.log"
echo "2. Once models ready, take snapshot via DO console"
echo "3. Destroy → recreate = auto-start in 30 seconds"
echo ""
echo "URLs:"
echo "  Frontend: http://134.199.193.58:3000/"
echo "  Health:   http://134.199.193.58:3000/health"
echo "  API:      http://134.199.193.58:3000/judge/transparency"
echo "=========================================="
