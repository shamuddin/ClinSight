# ClinSight Recovery Scripts Documentation

## Overview

This document describes the master recovery infrastructure for the ClinSight GPU droplet environment. Recovery scripts were created and tested to ensure the AMD MI300X GPU droplet can be fully restored after a snapshot re-bake.

## Scripts Created

| Script | Location | Purpose |
|---|---|---|
| **master_recovery.py** | `scripts/master_recovery.py` | Run from local WSL. One command recovery: `python3 scripts/master_recovery.py --host <IP>` |
| **droplet_recovery.sh** | `scripts/droplet_recovery.sh` (local) / `/root/clinsight_recovery.sh` (droplet) | Run ON the droplet after snapshot restore: `bash /root/clinsight_recovery.sh` |

## Master Recovery Phases (10 phases, 1 command)

    Phase 1: Pre-flight           SSH check, container status, GPU visibility
    Phase 2: Infrastructure       Mount scratch disk, volume sanity, start container
    Phase 3: Code Sync            rsync local repo → droplet → container /opt/clinsight
    Phase 4: Dependencies         pip install missing packages (fastapi, openai, etc.)
    Phase 5: Model Check/DL       Verify HF cache, auto-download if missing (skip with --skip-models)
    Phase 6: vLLM Launch          Vision:8000, Text:8001, backgrounded with proper env
    Phase 7: Health Checks        /v1/models, GPU memory, warm-up inference
    Phase 8: E2E Pipeline         Full pipeline run, ESI + findings + audit log
    Phase 9: Consistency          Run twice, compare outputs
    Phase 10: Report              Summary table + endpoint URLs + next steps

## Flags for Faster Re-runs

    --skip-sync   -- Skip rsync if code already up to date
    --skip-models -- Skip model download check

## Snapshot Survival Checklist

- [x] Container `clinsight` exists and starts
- [x] Scratch disk `/dev/vdc1` mounted at `/mnt/scratch`
- [x] Volume mounts: `/mnt/scratch:/mnt/scratch`, `/shared-docker:/shared-docker`
- [x] Latest ClinSight code in `/opt/clinsight`
- [x] Python deps installed
- [x] HF cache populated (Qwen models)
- [x] vLLM vision on port 8000
- [x] vLLM text on port 8001
- [x] Model name mapping bug fixed (`qwen3.5-35b-a3b`)
- [x] E2E pipeline passes (ESI=1, ~26s)
- [x] SSH retry logic for transient connection drops

## Current Droplet State (Last Verified)

- **IP**: `129.212.181.117`
- **Container**: `clinsight` running with vLLM both servers
- **GPU**: MI300X, VRAM ~83% (~170 GB / 205 GB)
- **Both vLLM servers**: Running (Vision 8000, Text 8001)
- **E2E Pipeline**: Passing

## Quick Recovery Commands

### From Local WSL (full recovery)

```bash
cd /mnt/k/Hackthon/ClinSight
python3 scripts/master_recovery.py --host <DROPLET_IP>
```

### From Droplet (after snapshot restore)

```bash
bash /root/clinsight_recovery.sh
```

## Exit Codes (master_recovery.py)

| Code | Meaning |
|---|---|
| 0 | All good |
| 1 | Pre-flight failed |
| 2 | Infrastructure issue |
| 3 | Model download failed |
| 4 | vLLM launch failed |
| 5 | Health check failed |
| 6 | E2E test failed |
| 7 | Consistency check failed |
