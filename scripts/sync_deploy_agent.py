#!/usr/bin/env python3
"""ClinSight Sync & Deploy Agent
Builds React dist, syncs to droplet/container, verifies health.
Usage: python scripts/sync_deploy_agent.py [DROPLET_IP]
"""
import subprocess, sys, time, requests, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
FRONTEND = BASE / "frontend" / "react-app"
DROPLET = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DROPLET_IP", "129.212.176.125")
HEALTH_URL = f"http://{DROPLET}:3000/health"
DEMO_URL = f"http://{DROPLET}:3000/demo/cases"

def run(cmd, cwd=None):
    print(f"  ► {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ FAILED: {result.stderr[:200]}")
        return False
    print(f"  ✓ OK")
    return True

print("═" * 60)
print("CLINSIGHT SYNC & DEPLOY AGENT")
print("═" * 60)

# Step 1: Build
print("\n[1/4] Building React frontend...")
if not run("npm run build", cwd=str(FRONTEND)):
    sys.exit(1)

# Step 2: Verify dist exists
DIST = FRONTEND / "dist"
if not DIST.exists():
    print("  ✗ dist/ not found after build")
    sys.exit(1)
index = DIST / "index.html"
if index.exists():
    print(f"  ✓ dist/index.html exists ({index.stat().st_size} bytes)")

# Step 3: Sync to droplet
print(f"\n[2/4] Syncing dist/ to droplet {DROPLET}...")
# Try ssh pipe first (most reliable)
cmd = f"""cd {FRONTEND} && tar czf - dist/ | ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 root@{DROPLET} 'cd /opt/clinsight && tar xzf - && echo SYNC_OK'"""
if not run(cmd):
    # Fallback: try rsync if available
    print("  ⚠ SSH pipe failed, trying rsync...")
    cmd2 = f"rsync -avz --delete -e 'ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519' {DIST}/ root@{DROPLET}:/opt/clinsight/frontend/react-app/dist/"
    if not run(cmd2):
        print("  ✗ All sync methods failed")
        sys.exit(1)

# Step 4: Restart backend
print(f"\n[3/4] Restarting backend on {DROPLET}...")
restart_cmd = f"ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_ed25519 root@{DROPLET} 'cd /opt/clinsight && docker restart clinsight-backend || docker-compose restart backend'"
run(restart_cmd)
time.sleep(3)

# Step 5: Verify
print(f"\n[4/4] Verifying deployment...")
try:
    r = requests.get(HEALTH_URL, timeout=10)
    data = r.json()
    print(f"  ✓ /health: {data}")
    if data.get("mode") == "live_inference":
        print("  ✓ Backend is in LIVE inference mode")
    else:
        print(f"  ⚠ Backend mode: {data.get('mode', 'unknown')}")
except Exception as e:
    print(f"  ✗ Health check failed: {e}")
    sys.exit(1)

try:
    r = requests.get(DEMO_URL, timeout=10)
    cases = r.json()
    print(f"  ✓ /demo/cases: {len(cases)} cases loaded")
except Exception as e:
    print(f"  ⚠ Demo cases check failed: {e}")

print("\n" + "═" * 60)
print("DEPLOY COMPLETE")
print("═" * 60)
