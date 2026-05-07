#!/bin/bash
# ════════════════════════════════════════════════════════════
# ONE-TIME FIX: Make droplet boot-ready from snapshot
# Run this ONCE on the droplet, then take a snapshot.
# ════════════════════════════════════════════════════════════

set -e

DROplet_IP="134.199.193.58"
KEY="/workspace/.ssh/id_ed25519"

echo "=== Step 1: Create persistent HF cache on host ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  mkdir -p /shared-docker/hf_cache
  chmod 777 /shared-docker/hf_cache
'

echo "=== Step 2: Copy models from containers to host cache ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  docker exec rocm bash -c "cp -a /root/.cache/huggingface/hub/. /shared-docker/hf_cache/" 2>&1 || true
  docker exec clinsight bash -c "cp -a /root/.cache/huggingface/hub/. /shared-docker/hf_cache/" 2>&1 || true
  du -sh /shared-docker/hf_cache/* 2>&1 | sort -rh | head -5
'

echo "=== Step 3: Recreate containers with cache mounts ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  docker stop rocm clinsight 2>/dev/null || true
  docker rm rocm clinsight 2>/dev/null || true
'

echo "=== Step 4: Create rocm container with cache mount ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  docker run -d --name rocm --restart unless-stopped \
    --network host \
    --privileged \
    --device /dev/kfd --device /dev/dri \
    -v /shared-docker/hf_cache:/root/.cache/huggingface \
    -v /shared-docker/clinsight:/opt/clinsight \
    rocm:latest \
    bash -c "sleep infinity"
  sleep 2
  docker ps --format "{{.Names}} {{.Status}}" | grep rocm
'

echo "=== Step 5: Install Python deps inside rocm container ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  docker exec rocm pip install -q fastapi uvicorn pydantic pillow httpx requests 2>&1 || true
  docker exec rocm python3 -c "import fastapi, uvicorn; print(\"deps_ok\")"
'

echo "=== Step 6: Create clinsight container with code ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  # Copy latest dist into the shared clinsight directory
  mkdir -p /shared-docker/clinsight/frontend/react-app/dist
  cp -r /opt/clinsight/frontend/react-app/dist/* /shared-docker/clinsight/frontend/react-app/dist/ 2>&1 || true

  docker run -d --name clinsight --restart unless-stopped \
    --network host \
    -v /shared-docker/clinsight:/opt/clinsight \
    -v /tmp:/tmp \
    clinsight:latest \
    bash -c "cd /opt/clinsight && python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error"
  sleep 3
  docker ps --format "{{.Names}} {{.Status}}" | grep -E "rocm|clinsight"
  # Health check
  curl -s http://127.0.0.1:3000/health 2>&1 || echo "BACKEND_NOT_READY"
'

echo "=== Step 7: Install systemd auto-start ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i "$KEY" root@$DROplet_IP '
  sudo tee /etc/systemd/system/clinsight.service <> EOF
[Unit]
Description=ClinSight Multi-Agent Stack
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c "
  echo Starting ClinSight stack;
  docker start rocm 2>/dev/null || true;
  docker start clinsight 2>/dev/null || true;
  sleep 5;
  docker exec clinsight bash -c \"cd /opt/clinsight \u0026\u0026 pkill -f uvicorn; python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 3000 --log-level error > /tmp/backend.log 2\u003e\u00261 \u0026\"
"
ExecStop=/bin/bash -c "docker stop clinsight rocm 2>/dev/null || true"

[Install]
WantedBy=multi-user.target
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable clinsight.service
  sudo systemctl start clinsight.service
  sudo systemctl status clinsight --no-pager | head -10
'

echo ""
echo "=== DONE ==="
echo "Next steps:"
echo "1. Verify: ssh -i $KEY root@$DROplet_IP 'docker ps'"
echo "2. Test:   curl http://$DROplet_IP:3000/health"
echo "3. Reboot droplet from DO console to test auto-start"
echo "4. Take snapshot from DO console"
echo "5. Destroy droplet → Recreate from snapshot → verify 2-min boot"
