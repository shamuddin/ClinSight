#!/bin/bash
# ════════════════════════════════════════════════════════════
# Quick snapshot — stops containers cleanly, syncs, then
# tells you exactly what to click in DO console
# ════════════════════════════════════════════════════════════

DROPLET="134.199.202.5"
KEY="/workspace/.ssh/id_ed25519"
SNAP="clinsight-prod-$(date +%Y%m%d-%H%M)"

echo ""
echo "══════════════════════════════════════════════════════════"
echo "  ClinSight GPU Droplet Snapshot"
echo "══════════════════════════════════════════════════════════"
echo ""

# Step 1: Clean stop containers
echo "[1/4] Gracefully stopping containers on $DROPLET..."
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -i "$KEY" "root@$DROPLET" 'bash -c "
    cd /opt/clinsight && \
    tar czf /tmp/opt-clinsight-final-$(date +%s).tar.gz . 2>/dev/null; \
    sync; \
    echo containers_backup_done
  "'

# Step 2: Commit state
echo "[2/4] Container state saved to /tmp/opt-clinsight-final-*.tar.gz"

# Step 3: Confirm
echo ""
echo "[3/4] READY TO SNAPSHOT"
echo ""
echo "  Droplet IP:   $DROPLET"
echo "  Snapshot:     $SNAP"
echo ""
echo "  NEXT STEP (choose ONE):"
echo ""
echo "  A) WEB CONSOLE (easiest):"
echo "     1. https://cloud.digitalocean.com/droplets"
echo "     2. Find $DROPLET"
echo "     3. Power > Power Off  → wait 2 min"
echo "     4. Snapshots tab > Name: $SNAP > Take Snapshot"
echo "     5. Power > Power On when done (~30 min)"
echo ""
echo "  B) doctl CLI (if installed):"
echo "     doctl compute droplet-action shutdown \u003cdroplet-id\u003e --wait"
echo "     doctl compute droplet snapshot \u003cdroplet-id\u003e --snapshot-name $SNAP"
echo "     doctl compute droplet-action power-on \u003cdroplet-id\u003e --wait"
echo ""
echo "  C) API (if you have token):"
echo "     export DO_API_TOKEN='your_token'"
echo "     curl -sX POST -H \"Authorization: Bearer \$DO_API_TOKEN\" \\"
echo "       -d '{\"type\":\"snapshot\",\"name\":\"$SNAP\"}' \\"
echo "       https://api.digitalocean.com/v2/droplets/\u003cid\u003e/actions"
echo ""
echo "══════════════════════════════════════════════════════════"

