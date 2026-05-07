# ════════════════════════════════════════════════════════════════════════
# GPU Droplet Snapshot Persistence Guide
# WHY Everything Resets + HOW To Fix It Permanently
# ════════════════════════════════════════════════════════════════════════

## The 3 Problems

### Problem 1: Containers Don't Auto-Start
When DigitalOcean boots from snapshot, Docker containers that were running are now STOPPED.
You must start them manually every time.

### Problem 2: Models Downloaded to Container Layer (Ephemeral)
vLLM model cache (`~/.cache/huggingface/`) is inside the container's writable overlay filesystem.
When containers are recreated (even from same image), that layer is reset.
→ Models vanish → re-download every time.

### Problem 3: Docker Volumes Not Persisted Across Snapshot
If models are in a named Docker volume, snapshots of /shared-docker or /mnt/scratch
may not persist if those directories are not on the system disk.

## The Solutions

### Solution A: systemd Auto-Start Service (Fix Problem 1) ✅
Create a systemd service that starts containers on boot:

```bash
# On the droplet, create
sudo tee /etc/systemd/system/clinsight.service << 'EOF'
[Unit]
Description=ClinSight Multi-Agent Stack
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/bash -c '
  echo "Starting ClinSight containers...";
  docker start rocm || true;
  sleep 2;
  docker start clinsight || true;
  sleep 5;
  docker exec clinsight bash /opt/clinsight/scripts/restart_final.sh || true;
  docker exec rocm bash -c "bash /opt/clinsight/scripts/start_vllm_vision.sh > /tmp/vllm_vision.log 2>\u00261 &" || true;
  sleep 10;
  docker exec rocm bash -c "bash /opt/clinsight/scripts/start_vllm_text.sh > /tmp/vllm_text.log 2>\u00261 &" || true;
'
ExecStop=/usr/bin/bash -c '
  docker stop clinsight || true;
  docker stop rocm || true;
'

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable clinsight.service
sudo systemctl start clinsight.service
```

**Then create snapshot** → On recreate, containers auto-start.

### Solution B: Mount Cache to Persistent Host Directory (Fix Problem 2) ✅
Map container's HuggingFace cache to host directory (persisted in snapshot):

```bash
# On droplet host
sudo mkdir -p /shared-docker/hf_cache
sudo chmod 777 /shared-docker/hf_cache

# Stop containers
docker stop rocm clinsight

# Recreate rocm with cache mount
docker run -d --name rocm --restart unless-stopped \
  --network host \
  --device /dev/kfd --device /dev/dri \
  -v /shared-docker/hf_cache:/root/.cache/huggingface \
  -v /shared-docker:/shared-docker \
  rocm:latest sleep infinity

# Verify
docker exec rocm ls /root/.cache/huggingface/hub/ | head -5
```

**Then download models once** → Cache persists in `/shared-docker/hf_cache` → Snapshot preserves it.

### Solution C: Single Container (Simpler) ✅
Instead of 2 containers, use 1 container with everything:

```bash
# Dockerfile approach — build an image with models baked in
cat > /shared-docker/Dockerfile.clinsight-full <> 'EOF'
FROM vllm/vllm-openai-rocm:v0.17.1

# Install backend deps
RUN pip install fastapi uvicorn httpx pillow pydantic

# Copy code
COPY . /opt/clinsight
WORKDIR /opt/clinsight

# Download models once (baked into image)
RUN python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('Qwen/Qwen2.5-VL-7B-Instruct', local_dir='/root/.cache/huggingface/hub/Qwen2.5-VL-7B')
snapshot_download('Qwen/Qwen3.5-35B-A3B', local_dir='/root/.cache/huggingface/hub/Qwen3.5-35B')
" 2>/dev/null || true

EXPOSE 3000 8000 8001
CMD bash /opt/clinsight/scripts/start_all.sh
EOF

# Build
docker build -f /shared-docker/Dockerfile.clinsight-full -t clinsight:prod /shared-docker/clinsight
```

Then snapshot only needs `docker run clinsight:prod` and everything works.

## What You Have Now vs What You Need

| | Current State | Optimal State |
|---|---|---|
| Containers after boot | STOPPED | Auto-started via systemd |
| Model cache | Inside container (lost) | Host volume `/shared-docker/hf_cache` (persisted) |
| Code updates | Manual docker cp or rebuild | Git clone + volume mount |
| Snapshot size | Small (no models) | Large (models in host volume) |
| Time to ready | 1+ hour (re-download) | 2 minutes (auto-start) |

## Recommended One-Time Fix (Do Before Next Snapshot)

1. On current droplet:
```bash
ssh -i /workspace/.ssh/id_ed25519 root@134.199.193.58

# Mount cache to host
docker exec rocm bash -c 'cp -r /root/.cache/huggingface/hub/* /shared-docker/hf_cache/ 2>/dev/null || true'
mkdir -p /shared-docker/hf_cache
docker exec rocm bash -c 'ls /root/.cache/huggingface/hub/' | head -5

# If models there, copy them
docker exec rocm bash -c 'cp -a /root/.cache/huggingface/hub/. /shared-docker/hf_cache/' 

# Recreate rocm with cache mount
docker stop rocm
docker rm rocm
docker run -d --name rocm --restart unless-stopped \
  --network host --privileged \
  --device /dev/kfd --device /dev/dri \
  -v /shared-docker/hf_cache:/root/.cache/huggingface \
  -v /shared-docker/clinsight:/opt/clinsight \
  rocm:latest sleep infinity

# Install deps
docker exec rocm pip install -q fastapi uvicorn pydantic pillow httpx 2>/dev/null

# Start systemd auto-start
sudo tee /etc/systemd/system/clinsight.service << 'EOF'
[Unit]
Description=ClinSight
After=docker.service
[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/bash -c 'docker start rocm clinsight 2>/dev/null || true; sleep 5; docker exec clinsight bash /tmp/restart_final.sh 2>/dev/null || true'
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable clinsight

# Test reboot
sync
# Now take snapshot via DO console
```

2. Take snapshot
3. Destroy droplet
4. Recreate from snapshot → models, cache, auto-start all preserved

## Summary

| Fix | What It Solves | Effort |
|---|---|---|
| `--restart unless-stopped` | Container auto-start | 1 line |
| `-v /shared-docker/hf_cache:/root/.cache/huggingface` | Model persistence | 1 flag |
| systemd service | Full stack auto-start on boot | 1 file |
| Single baked image | Everything in one place | Docker build |

The snapshot should make your droplet **boot-ready in 2 minutes**, not require full setup.
