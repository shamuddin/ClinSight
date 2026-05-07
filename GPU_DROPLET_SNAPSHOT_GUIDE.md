# ════════════════════════════════════════════════════════════════
# GPU Droplet Snapshot Guide — ClinSight Production
# ════════════════════════════════════════════════════════════════
# Date: 2026-05-07
# Droplet IP: 134.199.202.5
# Droplet Name: clinsight-gpu
# Current State: clinsight container running, rocm container stopped
#
# This guide preserves your GPU droplet for instant recreation.
# ════════════════════════════════════════════════════════════════

## 1. CURRENT STATE (Last verified)

| Component | Status | Details |
|---|---|---|
| droplet IP | 134.199.202.5 | Ubuntu 22.04, ROCm 5.7 |
| clinsight container | **RUNNING** | Has latest code + frontend dist |
| rocm container | **STOPPED** | Has vision model, not symlinked |
| vLLM text (port 8000) | **RUNNING** | Qwen3.5-35B-A3B via clinsight container |
| vLLM vision (port 8001) | **UNKNOWN** | Via clinsight container |
| Backend API (port 3000) | **RUNNING** | FastAPI with judge/transparency endpoints |

## 2. SAVE THIS FILE

Before snapshotting, save this file and SSH key permanently:
```bash
cp /workspace/.ssh/id_ed25519 /workspace/.ssh/id_ed25519.clinsight-backup
cp /workspace/scripts/snapshot_gpu_droplet.sh /workspace/scripts/snapshot_gpu_droplet.sh.backup
```

## 3. CLEAN STOP (before snapshot)

Run ON THE DROPLET (not locally) to freeze state:
```bash
ssh -i /workspace/.ssh/id_ed25519 root@134.199.202.5

# Inside droplet:
docker exec clinsight bash -c 'tar czf /tmp/backend-data-$(date +%s).tar.gz /opt/clinsight/backend/data/ 2>/dev/null; echo saved'
docker exec clinsight bash -c 'tar czf /tmp/frontend-dist-$(date +%s).tar.gz /opt/clinsight/frontend/react-app/dist/ 2>/dev/null; echo saved'
sync
shutdown -h now
```

## 4. TAKE SNAPSHOT

### Method A — DigitalOcean Web Console (easiest, ~5 minutes)

1. Go to: https://cloud.digitalocean.com/droplets
2. Find: **clinsight-gpu** (134.199.202.5)
3. Click **Power → Power Off**
4. Wait ~2 minutes for droplet to stop
5. Click **Snapshots** tab
6. Name: `clinsight-gpu-snapshot-YYYYMMDD`
7. Click **Take Snapshot**
8. Wait ~30 minutes (snapshot takes ~20-40 min for 80GB)
9. Click **Power → Power On** to restart

### Method B — doctl CLI (faster if you have it)

```bash
# Install doctl if not already
brew install doctl      # macOS
snap install doctl        # Ubuntu

# Authenticate
doctl auth init           # paste your DO API token

# Take snapshot
doctl compute droplet-action shutdown clinsight-gpu --wait
doctl compute droplet snapshot clinsight-gpu --snapshot-name clinsight-gpu-snapshot-$(date +%Y%m%d)
doctl compute droplet-action power-on clinsight-gpu --wait
```

### Method C — API (for automation)

```bash
# Get droplet ID
DROPLET_ID=$(curl -s -X GET \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  "https://api.digitalocean.com/v2/droplets?page=1&per_page=200" \
  | jq '.droplets[] | select(.name=="clinsight-gpu") | .id')

# Create snapshot
curl -s -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DO_API_TOKEN" \
  -d '{"type":"snapshot","name":"clinsight-gpu-snapshot-'$(date +%Y%m%d)'"}' \
  "https://api.digitalocean.com/v2/droplets/$DROPLET_ID/actions"
```

## 5. RESTART AFTER SNAPSHOT

```bash
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -i /workspace/.ssh/id_ed25519 root@134.199.202.5 \
  "bash /tmp/restart_final.sh"
```

## 6. RECREATE FROM SNAPSHOT (when needed)

### Option 1 — Same region (fastest)
1. Go to https://cloud.digitalocean.com/images/snapshots
2. Find: `clinsight-gpu-snapshot-YYYYMMDD`
3. Click **More → Create Droplet**
4. Choose same region (e.g., NYC1)
5. Select same GPU flavor (e.g., g-8vcpu-64gb-192g-amd-mi300x)
6. Add SSH key
7. Launch
8. Wait 2-3 minutes for boot
9. SSH in as root (same IP or new IP — check console)

### Option 2 — Different region (copy snapshot first)
```bash
doctl compute image-action transfer \
  <snapshot-id> \
  --region nyc1 \
  --region sfo3
```
Then create droplet from copied snapshot.

## 7. POST-RECREATION STEPS

After recreating droplet from snapshot, it should boot with everything working.
If services don't auto-start, run:
```bash
docker exec clinsight bash /tmp/restart_final.sh
```

## 8. COST

| Item | Cost |
|---|---|
| Snapshot storage | ~$0.02/GB/month ≈ $1.60/month (80GB) |
| Droplet running | ~$3.00/hour for 8 CPU + MI300X |
| Droplet stopped | $0/hour (snapshot storage only) |

## 9. IMPORTANT NOTES

- **Snapshot includes**: entire disk including Docker containers, models, code
- **Excludes**: RAM state (containers must be restarted after power-on)
- **SSH key**: snapshot preserves root password + SSH keys
- **IP may change**: clone gets new IP unless using reserved/floating IP
- **Best practice**: Snapshot weekly before major changes

## 10. TROUBLESHOOTING

### "Droplet won't start after snapshot"
- Check console via DO web panel (force reboot)
- Check kernel parameters (rocm drivers may need kernel flags)

### "Services don't start after boot"
- SSH in, check `docker ps`
- Run `bash /tmp/restart_final.sh`

### "Models are missing after recreation"
- vLLM models should survive (on disk in container)
- HF cache may need re-download if on ephemeral storage

## 11. EMERGENCY: SSH key lost?

Use DO console access:
1. Web panel → Droplet → Access → Launch Recovery Console
2. Login as root (use original root password)
3. Re-add SSH key to `/root/.ssh/authorized_keys`

## 12. FILE LOCATIONS (for manual recovery)

| Data | Path on Droplet | Path on Local |
|---|---|---|
| SSH key | `/workspace/.ssh/id_ed25519` (local) | `/workspace/.ssh/id_ed25519` |
| ClinSight code | `/opt/clinsight/` (container) | `/workspace/` (git repo) |
| vLLM models | `/root/.cache/huggingface/` | N/A (auto-download) |
| Frontend dist | `/opt/clinsight/frontend/react-app/dist/` | `/workspace/frontend/react-app/dist/` |
| Restart script | `/tmp/restart_final.sh` | `/workspace/scripts/restart_final.sh` |
| Ground truth | `/opt/clinsight/backend/data/ground_truth.py` | `/workspace/backend/data/ground_truth.py` |
| Transparency | `/opt/clinsight/backend/data/medical_transparency.py` | `/workspace/backend/data/medical_transparency.py` |

# ════════════════════════════════════════════════════════════════
EOF
