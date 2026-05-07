#!/usr/bin/env python3
"""Fix droplet state: start BOTH vLLM servers properly."""
import subprocess, time, sys, json

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def run(cmd, timeout=60):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

# 1. Check current state
log("=== Current State ===")
r = run("docker ps -a --format '{{.Names}} {{.Status}} {{.Ports}}'")
log(r.stdout.strip())

r = run("docker exec rocm ps aux | grep -i vllm | grep -v grep || echo 'no vllm'")
log(f"vLLM procs: {r.stdout.strip()[:200]}")

r = run("curl -s http://127.0.0.1:8000/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[\"data\"][0][\"id\"])' 2>/dev/null || echo 'NOT_READY'")
log(f"Port 8000: {r.stdout.strip()}")

r = run("curl -s http://127.0.0.1:8001/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[\"data\"][0][\"id\"])' 2>/dev/null || echo 'NOT_READY'")
log(f"Port 8001: {r.stdout.strip()}")

# 2. Check container clinsight
r = run("docker exec clinsight bash -c 'ls /opt/clinsight/backend/agents/*.py 2>/dev/null | wc -l'")
log(f"clinsight has {r.stdout.strip()} agent files in /opt/clinsight")

r = run("docker exec clinsight bash -c 'ls /shared/clinsight/backend/agents/*.py 2>/dev/null | wc -l'")
log(f"clinsight has {r.stdout.strip()} agent files in /shared/clinsight")

# 3. GPU state
r = run("rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -10")
log(f"GPU:\n{r.stdout.strip()}")

# 4. Check if both models exist
r = run("ls -d /mnt/scratch/hf_cache/models--Qwen--Qwen* 2>/dev/null")
log(f"Models:\n{r.stdout.strip()}")
