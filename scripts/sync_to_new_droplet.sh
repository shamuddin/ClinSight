#!/bin/bash
set -e

# Copy latest Judge Verification files to new droplet
DROplet="134.199.193.58"
KEY="/workspace/.ssh/id_ed25519"

echo "=== Syncing latest code to new droplet $DROplet ==="

# Sync changed backend files (accuracy, transparency, ground truth, judge)
for f in backend/core/accuracy.py backend/data/ground_truth.py backend/data/medical_transparency.py backend/api/judge.py; do
    docker cp "/workspace/$f" clinsight:/opt/clinsight/$f 2>/dev/null || \
        scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
        -i "$KEY" "/workspace/$f" "root@$DROplet:/tmp/$f" && \
        ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
        -i "$KEY" "root@$DROplet" "docker cp /tmp/$f clinsight:/opt/clinsight/$f"
done

# Sync dist/ (frontend build)
docker cp /workspace/frontend/react-app/dist/ clinsight:/opt/clinsight/frontend/react-app/dist_ 2>/dev/null || \
    scp -r -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -i "$KEY" /workspace/frontend/react-app/dist/ "root@$DROplet:/tmp/dist" && \
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -i "$KEY" "root@$DROplet" "docker cp /tmp/dist clinsight:/opt/clinsight/frontend/react-app/dist"

# Restart
echo "=== Restarting backend ==="
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -i "$KEY" "root@$DROplet" "docker exec clinsight bash /tmp/restart_final.sh"

echo "=== Done ==="
