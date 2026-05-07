#!/bin/bash
# ════════════════════════════════════════════════════════════════
# GPU Dropulet Snapshot Script
# Run this from your LOCAL machine (not the droplet)
# ════════════════════════════════════════════════════════════════

DROPLET_IP="134.199.202.5"
DROPLET_NAME="clinsight-gpu"
PRIVATE_KEY="/workspace/.ssh/id_ed25519"
SNAPSHOT_NAME="clinsight-gpu-snapshot-$(date +%Y%m%d-%H%M%S)"

echo "=== ClinSight GPU Droplet Snapshot ==="
echo "Target: $DROPLET_IP"
echo "Snapshot name: $SNAPSHOT_NAME"
echo ""

# 1. Gracefully stop containers on the droplet
echo "[1/5] Stopping containers on droplet..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -i "$PRIVATE_KEY" "root@$DROPLET_IP" \
  "docker stop clinsight 2>/dev/null; docker stop rocm 2>/dev/null; echo 'containers_stopped'"

# 2. Sync filesystem
echo "[2/5] Syncing filesystem..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -i "$PRIVATE_KEY" "root@$DROPLET_IP" "sync; echo 'sync_done'"

# 3. Power off the droplet (required for consistent snapshot)
echo "[3/5] Powering off droplet..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -i "$PRIVATE_KEY" "root@$DROPLET_IP" "shutdown -h now" 2>/dev/null || true

# Wait for droplet to go offline
echo "[4/5] Waiting for droplet to stop (~30s)..."
sleep 30

# 4. Create snapshot via DigitalOcean API (needs DO token)
echo "[5/5] Creating snapshot..."
echo ""
echo "==================================================="
echo "ACTION REQUIRED: Run ONE of these on your local machine:"
echo ""
echo "METHOD A — doctl (recommended):"
echo "  doctl auth init  # if first time"
echo "  doctl compute droplet snapshot $DROPLET_NAME --snapshot-name $SNAPSHOT_NAME"
echo ""
echo "METHOD B — Web console (easiest):"
echo "  1. Go to: https://cloud.digitalocean.com/droplets"
echo "  2. Find: $DROPLET_NAME ($DROPLET_IP)"
echo "  3. Click 'Snapshots' tab"
echo "  4. Enter name: $SNAPSHOT_NAME"
echo "  5. Click 'Take Snapshot'"
echo ""
echo "==================================================="
echo "Estimated time: 20-40 minutes for 80GB droplet"
echo "Cost: ~$0.02/GB/month = ~$1.60/month stored"
echo ""
echo "After snapshot, restart droplet to test it boots:"
echo "  doctl compute droplet-action power-on $DROPLET_NAME"

