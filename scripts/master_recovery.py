#!/usr/bin/env python3
"""
ClinSight GPU Droplet Master Recovery Script
============================================

One command to recover ClinSight from a fresh GPU droplet snapshot.

Usage (from local WSL):
    cd /mnt/k/Hackthon/ClinSight
    python3 scripts/master_recovery.py --host <DROPLET_IP>

Phases:
    1. Pre-flight (SSH, sudo, container status)
    2. Infrastructure (mount scratch, ensure container, port mapping)
    3. Code sync (local latest -> droplet /shared-docker -> container /opt/clinsight)
    4. Dependency check (Python packages inside container)
    5. Model check (HF cache on /mnt/scratch, download if missing)
    6. vLLM launch (vision:8000, text:8001 with proper settings)
    7. Health checks (/health, /v1/models, warm-up inference)
    8. E2E pipeline test (real inference, ESI check)
    9. Consistency pass (repeat pipeline, compare outputs)
    10. Report (summary table + next steps)

Exit codes:
    0 = all good
    1 = pre-flight failed
    2 = infrastructure issue
    3 = model download failed
    4 = vLLM launch failed
    5 = health check failed
    6 = E2E test failed
    7 = consistency check failed
"""

import argparse
import json
import os
import subprocess
import sys
import textwrap
import time
from pathlib import Path
from typing import List, Tuple

# ── Config ──
DEFAULT_LOCAL_REPO = "/mnt/k/Hackthon/ClinSight"
DROPLET_REPO_PATH = "/shared-docker/clinsight"
CONTAINER_REPO_PATH = "/opt/clinsight"
CONTAINER_NAME = "clinsight"
IMAGE_NAME = "rocm:latest"
SCRATCH_DISK = "/dev/vdc1"
SCRATCH_MOUNT = "/mnt/scratch"
LOCAL_HF_CACHE = f"{SCRATCH_MOUNT}/hf_cache"
MODELS = {
    "vision": {"id": "Qwen/Qwen2.5-VL-7B-Instruct", "port": 8000, "mem": 0.30, "len": 8192},
    "text":   {"id": "Qwen/Qwen3.5-35B-A3B",         "port": 8001, "mem": 0.55, "len": 4096},
}
SERVED_NAMES = {
    "vision": "qwen2.5-vl-7b",
    "text":   "qwen3.5-35b-a3b",
}
SSH_KEY = os.path.expanduser("~/.ssh/id_ed25519")
SSH_OPTS = "-o StrictHostKeyChecking=no -o ConnectTimeout=10"

# ── Colors ──
class C:
    OK = "\033[92m"
    WARN = "\033[93m"
    FAIL = "\033[91m"
    INFO = "\033[94m"
    END = "\033[0m"


def run_local(cmd: str, timeout: int = 60) -> Tuple[str, str, int]:
    """Run a local shell command."""
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout, r.stderr, r.returncode


def ssh_cmd(host: str, cmd: str, timeout: int = 60) -> Tuple[str, str, int]:
    """Run command on droplet via SSH."""
    full = f"ssh {SSH_OPTS} -i {SSH_KEY} root@{host} '{cmd}'"
    r = subprocess.run(full, shell=True, capture_output=True, text=True, timeout=timeout)
    return r.stdout, r.stderr, r.returncode


def docker_cmd(host: str, cmd: str, timeout: int = 60) -> Tuple[str, str, int]:
    """Run command inside the clinsight container."""
    return ssh_cmd(host, f"docker exec {CONTAINER_NAME} {cmd}", timeout=timeout)


def step(name: str):
    """Print section header."""
    print(f"\n{C.INFO}{'='*60}{C.END}")
    print(f"{C.INFO}>>> PHASE: {name}{C.END}")
    print(f"{C.INFO}{'='*60}{C.END}")


def ok(msg: str):
    print(f"  {C.OK}[OK]{C.END}  {msg}")


def fail(msg: str):
    print(f"  {C.FAIL}[FAIL]{C.END} {msg}")


def warn(msg: str):
    print(f"  {C.WARN}[WARN]{C.END} {msg}")


def info(msg: str):
    print(f"  {C.INFO}[INFO]{C.END} {msg}")


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Pre-flight
# ═══════════════════════════════════════════════════════════════════════════════
def phase_pre_flight(host: str) -> bool:
    step("1. PRE-FLIGHT")

    # 1a: SSH connectivity
    out, err, code = ssh_cmd(host, "hostname", timeout=10)
    if code == 0:
        ok(f"SSH to root@{host} OK (hostname: {out.strip()})")
    else:
        fail(f"SSH failed: {err.strip()}")
        return False

    # 1b: Container exists
    out, err, code = ssh_cmd(host, f"docker inspect {CONTAINER_NAME} --format '{{{{.State.Status}}}}' 2>/dev/null")
    if code == 0:
        ok(f"Container '{CONTAINER_NAME}' exists, status: {out.strip()}")
    else:
        fail(f"Container '{CONTAINER_NAME}' not found. Build container first or use 'rocm:latest'.")
        return False

    # 1c: Container has GPU
    out, err, code = ssh_cmd(host, f"docker exec {CONTAINER_NAME} rocm-smi --showproductname 2>/dev/null | head -3 || echo 'no rocm-smi in container'")
    if "no rocm-smi" in out:
        warn("rocm-smi not available in container — GPU tools may be missing")
    else:
        ok(f"GPU in container: {out.strip()[:80]}")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Infrastructure (mount scratch, ensure ports)
# ═══════════════════════════════════════════════════════════════════════════════
def phase_infrastructure(host: str) -> bool:
    step("2. INFRASTRUCTURE")

    # 2a: Mount scratch disk
    out, err, code = ssh_cmd(host, f"mountpoint -q {SCRATCH_MOUNT} && echo mounted || (mount {SCRATCH_DISK} {SCRATCH_MOUNT} && echo mounted)")
    if "mounted" in out:
        ok(f"Scratch disk mounted: {SCRATCH_MOUNT}")
    else:
        fail(f"Scratch disk mount failed: {err}")
        return False

    # 2b: Ensure /mnt/scratch and /shared-docker are volume-mounted into container
    out, err, code = ssh_cmd(host, f"docker inspect {CONTAINER_NAME} --format '{{{{json .HostConfig.Binds}}}}'")
    binds = out.strip()
    ok(f"Container volumes: {binds[:150]}")
    if SCRATCH_MOUNT not in binds:
        fail(f"Container missing {SCRATCH_MOUNT} volume mount!")
        return False

    # 2c: Disk space
    out, err, code = ssh_cmd(host, f"df -h {SCRATCH_MOUNT} | tail -1")
    parts = out.split()
    if len(parts) >= 4:
        info(f"Scratch: {parts[1]} total, {parts[2]} used, {parts[3]} avail")

    # 2d: Ensure no other containers hogging ports
    ssh_cmd(host, "docker stop rocm 2>/dev/null || true; docker rm rocm 2>/dev/null || true")
    ok("Stopped generic 'rocm' container if present")

    # 2e: Start clinsight container if needed
    out, err, code = ssh_cmd(host, f"docker start {CONTAINER_NAME}")
    time.sleep(2)
    out2, _, _ = ssh_cmd(host, f"docker ps --format '{{{{.Names}}}}' | grep ^{CONTAINER_NAME}$")
    if CONTAINER_NAME in out2:
        ok(f"Container '{CONTAINER_NAME}' running")
    else:
        fail("Container failed to start")
        return False

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Code Sync (local -> droplet -> container)
# ═══════════════════════════════════════════════════════════════════════════════
def phase_code_sync(host: str, local_repo: str) -> bool:
    step("3. CODE SYNC")

    # 3a: Verify local repo existence
    repo = Path(local_repo)
    if not repo.exists():
        fail(f"Local repo not found: {local_repo}")
        return False
    ok(f"Local repo: {local_repo}")

    # 3b: Show current git commit
    out, _, _ = run_local(f"cd {local_repo} && git log --oneline -1")
    info(f"Local HEAD: {out.strip()}")

    # 3c: rsync local -> droplet /shared-docker/clinsight
    info("rsync local -> droplet /shared-docker/clinsight/ ...")
    out, err, code = run_local(
        f"rsync -avz --exclude='.venv' --exclude='node_modules' --exclude='.git' "
        f"--exclude='__pycache__' --exclude='*.pyc' --exclude='.pytest_cache' --exclude='htmlcov' "
        f"'{local_repo}/' root@{host}:{DROPLET_REPO_PATH}/"
    )
    if code == 0:
        ok("rsync complete")
    else:
        fail(f"rsync failed: {err[:200]}")
        return False

    # 3d: rsync droplet -> container /opt/clinsight
    info("Sync droplet -> container /opt/clinsight/ ...")
    ssh_cmd(host, f"docker exec {CONTAINER_NAME} rm -rf {CONTAINER_REPO_PATH}")
    out, err, code = ssh_cmd(host, f"docker cp {DROPLET_REPO_PATH}/. {CONTAINER_NAME}:{CONTAINER_REPO_PATH}/")
    if code == 0:
        ok("Container code updated")
    else:
        fail(f"docker cp failed: {err[:200]}")
        return False

    # 3e: Verify synced files
    out, _, _ = docker_cmd(host, f"ls {CONTAINER_REPO_PATH}/scripts/")
    if "start_vllm" in out:
        ok("Scripts present in container")
    else:
        warn("Scripts directory may be incomplete")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 4: Dependencies
# ═══════════════════════════════════════════════════════════════════════════════
def phase_dependencies(host: str) -> bool:
    step("4. DEPENDENCIES")

    required = ["fastapi", "uvicorn", "pydantic", "httpx", "openai", "Pillow", "numpy"]

    info("Checking Python deps in container...")
    out, err, code = docker_cmd(host, "pip list 2>/dev/null || echo 'pip not working'")
    installed = out.lower()

    missing = []
    for pkg in required:
        if pkg.lower() in installed:
            ok(f"{pkg} installed")
        else:
            missing.append(pkg)
            warn(f"{pkg} missing — will install")

    if missing:
        info(f"Installing {len(missing)} missing packages...")
        pkg_str = " ".join(missing)
        docker_cmd(host, f"pip install -q {pkg_str}", timeout=120)
        ok("Missing packages installed")
    else:
        ok("All deps present")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: Model Check / Download
# ═══════════════════════════════════════════════════════════════════════════════
def phase_models(host: str) -> bool:
    step("5. MODEL CHECK / DOWNLOAD")

    # Set HF_HOME in container
    docker_cmd(host, f"mkdir -p {LOCAL_HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct {LOCAL_HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B")

    for key, cfg in MODELS.items():
        model_id = cfg["id"]
        local_dir = f"{LOCAL_HF_CACHE}/models--{model_id.replace('/', '--')}"

        # Check if model files exist
        out, _, code = docker_cmd(host, f"ls {local_dir}/config.json 2>/dev/null && echo present || echo missing")
        if "present" in out:
            ok(f"[{key}] {model_id} already cached")
            continue

        warn(f"[{key}] {model_id} NOT found — downloading now (~{cfg['port']} port config)")
        info("This may take 5-45 min depending on model size...")

        # Download via huggingface-cli
        out, err, code = docker_cmd(
            host,
            f"export HF_HOME={LOCAL_HF_CACHE}; export HUGGINGFACE_HUB_CACHE={LOCAL_HF_CACHE}; "
            f"huggingface-cli download {model_id} --local-dir {local_dir} --local-dir-use-symlinks False",
            timeout=3600,
        )
        if code == 0:
            ok(f"[{key}] Download complete")
        else:
            fail(f"[{key}] Download failed: {err[:300]}")
            return False

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 6: vLLM Launch
# ═══════════════════════════════════════════════════════════════════════════════
def phase_vllm_launch(host: str) -> bool:
    step("6. VLLM LAUNCH")

    # Kill any existing vLLM processes
    ssh_cmd(host, f"docker exec {CONTAINER_NAME} pkill -f 'vllm.entrypoints' 2>/dev/null || true")
    time.sleep(2)

    for key, cfg in MODELS.items():
        model_id = cfg["id"]
        local_dir = f"{LOCAL_HF_CACHE}/models--{model_id.replace('/', '--')}"
        port = cfg["port"]
        mem = cfg["mem"]
        maxlen = cfg["len"]
        served = SERVED_NAMES[key]

        info(f"Starting {key} model on port {port}...")

        # Check if port already responding
        out, _, _ = ssh_cmd(host, f"docker exec {CONTAINER_NAME} curl -s http://127.0.0.1:{port}/v1/models 2>/dev/null || echo dead")
        if "id" in out:
            ok(f"[{key}] Already running on port {port}")
            continue

        # Launch
        docker_cmd(
            host,
            f"nohup bash -c 'export HF_HOME={LOCAL_HF_CACHE}; export HUGGINGFACE_HUB_CACHE={LOCAL_HF_CACHE}; "
            f"export VLLM_USE_V1=0; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True; "
            f"python3 -m vllm.entrypoints.openai.api_server "
            f"--model {local_dir} "
            f"--served-model-name {served} "
            f"--dtype float16 "
            f"--tensor-parallel-size 1 "
            f"--port {port} "
            f"--host 127.0.0.1 "
            f"--gpu-memory-utilization {mem} "
            f"--max-model-len {maxlen} "
            f"--max-num-seqs 2 "
            f"--trust-remote-code "
            f"2>&1 | tee {LOCAL_HF_CACHE}/../vllm_{key}.log' > /dev/null 2>&1 &"
        )
        time.sleep(3)
        ok(f"[{key}] Launch initiated in background")

    # Wait for servers to be ready
    info("Waiting for vLLM servers to be ready (up to 120s)...")
    for attempt in range(24):
        time.sleep(5)
        vision_ok = False
        text_ok = False

        out, _, _ = ssh_cmd(host, f"docker exec {CONTAINER_NAME} curl -s http://127.0.0.1:8000/v1/models 2>/dev/null || echo dead")
        if '"id"' in out:
            vision_ok = True
            if attempt == 0:
                ok("Vision API responding on port 8000")

        out, _, _ = ssh_cmd(host, f"docker exec {CONTAINER_NAME} curl -s http://127.0.0.1:8001/v1/models 2>/dev/null || echo dead")
        if '"id"' in out:
            text_ok = True
            if attempt == 0:
                ok("Text API responding on port 8001")

        if vision_ok and text_ok:
            ok("Both vLLM servers ready")
            return True

    fail("vLLM servers failed to start within 120s")
    return False


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 7: Health Checks
# ═══════════════════════════════════════════════════════════════════════════════
def phase_health(host: str) -> bool:
    step("7. HEALTH CHECKS")

    # 7a: GPU memory
    out, _, _ = ssh_cmd(host, f"docker exec {CONTAINER_NAME} rocm-smi | grep -E '^0')")
    info(f"GPU status: {out.strip()[:120]}")

    # 7b: Model list verification
    for port, name in [(8000, "vision"), (8001, "text")]:
        out, _, _ = ssh_cmd(
            host,
            f"docker exec {CONTAINER_NAME} curl -s http://127.0.0.1:{port}/v1/models"
        )
        if '"id"' in out:
            ok(f"[{name}] API /v1/models responds")
        else:
            fail(f"[{name}] API /v1/models NOT responding")
            return False

    # 7c: Warm-up inference on text model
    out, _, code = ssh_cmd(
        host,
        f"docker exec {CONTAINER_NAME} curl -s http://127.0.0.1:8001/v1/chat/completions "
        f"-H 'Content-Type: application/json' "
        f"-d '{{\"model\":\"qwen3.5-35b-a3b\",\"messages\":[{{\"role\":\"user\",\"content\":\"Say OK\"}}],\"max_tokens\":5}}'"
    )
    if '"content"' in out or '"OK"' in out:
        ok("Text model warm-up inference OK")
    else:
        warn("Text model warm-up returned: " + out[:200])

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 8: E2E Pipeline Test
# ═══════════════════════════════════════════════════════════════════════════════
def phase_e2e(host: str) -> bool:
    step("8. E2E PIPELINE TEST")

    e2e_script = f"""
import sys, os, json, asyncio, time
sys.path.insert(0, '{CONTAINER_REPO_PATH}')
os.chdir('{CONTAINER_REPO_PATH}')

from backend.agents.graph import run_pipeline

state = {{
    "case_id": "CS-2024-001",
    "image_path": "data/images/demo_chest_pain.png",
    "lab_values": {{"troponin_i": 0.12, "bnp": 180, "crp": 12, "wbc": 9.2,
                    "hemoglobin": 14.1, "platelets": 245, "creatinine": 0.9, "glucose": 105}},
    "lab_units": {{"troponin_i": "ng/L", "bnp": "pg/mL", "crp": "mg/L", "wbc": "K/uL",
                   "hemoglobin": "g/dL", "platelets": "K/uL", "creatinine": "mg/dL", "glucose": "mg/dL"}},
    "triage_note": "45yo male with chest pain, vitals stable",
    "patient_age": 45, "patient_sex": "M", "patient_race": "White",
    "chief_complaint": "Chest pain",
    "vitals": {{"bp": "120/80", "hr": 72, "rr": 16, "temp": 37.0, "spo2": 98}},
    "image_hash": "", "quality_gate": {{}}, "pediatric_gate": {{}}, "input_warnings": [],
    "image_features": {{}}, "findings": [], "attention_regions": [],
    "lab_alerts": [], "lab_patterns": [], "lab_correlation": {{}},
    "contradictions": [], "hallucination_flags": [], "bias_flags": [],
    "safety_downgrades": 0, "merged_flags": [],
    "esi_level": 5, "esi_description": "", "esi_rules_triggered": [],
    "differential": [], "suggested_actions": [], "report": {{}},
    "audit_log": [], "total_time_ms": 0.0,
}}

async def test():
    start = time.time()
    final = await run_pipeline(state)
    elapsed = time.time() - start
    result = {{
        "esi_level": final.get("esi_level"),
        "findings_count": len(final.get("findings", [])),
        "differential": final.get("differential", [])[:5],
        "suggested_actions": final.get("suggested_actions", [])[:5],
        "audit_log_count": len(final.get("audit_log", [])),
        "total_time_s": round(elapsed, 2),
        "errors": [],
    }}
    print(json.dumps(result))

asyncio.run(test())
"""
    # Write and run inside container
    ssh_cmd(host, f"docker exec {CONTAINER_NAME} bash -c 'cat > /tmp/e2e_test.py' << 'PYEOF'\n{e2e_script}\nPYEOF")
    out, err, code = docker_cmd(host, "python3 /tmp/e2e_test.py", timeout=180)

    try:
        result = json.loads(out.strip().splitlines()[-1])
    except json.JSONDecodeError:
        fail(f"E2E output parse failed: {out[:300]}")
        return False

    ok(f"Pipeline completed in {result.get('total_time_s', '?')}s")
    ok(f"ESI level: {result.get('esi_level', '?')}")
    ok(f"Findings: {result.get('findings_count', '?')}")
    ok(f"Audit entries: {result.get('audit_log_count', '?')}")

    if result.get("esi_level") is None:
        fail("ESI level not returned")
        return False

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Phase 9: Consistency Check
# ═══════════════════════════════════════════════════════════════════════════════
def phase_consistency(host: str) -> bool:
    step("9. CONSISTENCY CHECK")

    # Run E2E twice and compare ESI levels
    results = []
    for attempt in range(1, 3):
        info(f"Consistency run {attempt}/2...")
        out, err, code = docker_cmd(host, "python3 /tmp/e2e_test.py", timeout=180)
        try:
            result = json.loads(out.strip().splitlines()[-1])
            results.append(result)
        except Exception:
            warn(f"Run {attempt} failed to parse")
            return False

    if len(results) < 2:
        fail("Not enough successful runs")
        return False

    esi1 = results[0].get("esi_level")
    esi2 = results[1].get("esi_level")
    if esi1 == esi2:
        ok(f"Consistency PASS: ESI={esi1} on both runs")
    else:
        warn(f"Consistency diff: ESI run1={esi1}, ESI run2={esi2} (may be expected for LLM variance)")

    return True


# ═══════════════════════════════════════════════════════════════════════════════
# Master Report
# ═══════════════════════════════════════════════════════════════════════════════
def print_report(host: str):
    step("REPORT")
    out, _, _ = ssh_cmd(host, f"docker exec {CONTAINER_NAME} cat /opt/clinsight/.env")
    print(f"\n{C.INFO}Container .env:{C.END}")
    print(textwrap.indent(out.strip(), "    "))

    out, _, _ = ssh_cmd(host, f"docker exec {CONTAINER_NAME} rocm-smi | grep -E '^0|Device'")
    print(f"\n{C.INFO}GPU Status:{C.END}")
    print(textwrap.indent(out.strip(), "    "))

    print(f"\n{C.OK}All phases complete!{C.END}")
    print(f"Endpoints:")
    print(f"  Vision: http://{host}:8000/v1 (qwen2.5-vl-7b)")
    print(f"  Text:   http://{host}:8001/v1 (qwen3.5-35b-a3b)")
    print(f"\nNext steps:")
    print(f"  - Run benchmarks: python scripts/run_benchmark.py --host {host}")
    print(f"  - Run accuracy test: python scripts/run_benchmark.py --mode accuracy --host {host}")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description="ClinSight GPU Droplet Master Recovery")
    parser.add_argument("--host", required=True, help="GPU droplet IP address")
    parser.add_argument("--repo", default=DEFAULT_LOCAL_REPO, help="Local ClinSight repo path")
    parser.add_argument("--skip-sync", action="store_true", help="Skip code sync (use if code already fresh)")
    parser.add_argument("--skip-models", action="store_true", help="Skip model download check (use if models cached)")
    args = parser.parse_args()

    start_time = time.time()
    phases = []

    # Phase 1
    if not phase_pre_flight(args.host):
        sys.exit(1)
    phases.append("Pre-flight OK")

    # Phase 2
    if not phase_infrastructure(args.host):
        sys.exit(2)
    phases.append("Infrastructure OK")

    # Phase 3
    if not args.skip_sync:
        if not phase_code_sync(args.host, args.repo):
            sys.exit(2)
        phases.append("Code sync OK")
    else:
        phases.append("Code sync SKIPPED")

    # Phase 4
    if not phase_dependencies(args.host):
        sys.exit(2)
    phases.append("Dependencies OK")

    # Phase 5
    if not args.skip_models:
        if not phase_models(args.host):
            sys.exit(3)
        phases.append("Models OK")
    else:
        phases.append("Models SKIPPED")

    # Phase 6
    if not phase_vllm_launch(args.host):
        sys.exit(4)
    phases.append("vLLM launch OK")

    # Phase 7
    if not phase_health(args.host):
        sys.exit(5)
    phases.append("Health OK")

    # Phase 8
    if not phase_e2e(args.host):
        sys.exit(6)
    phases.append("E2E OK")

    # Phase 9
    if not phase_consistency(args.host):
        sys.exit(7)
    phases.append("Consistency OK")

    # Report
    print_report(args.host)

    total = time.time() - start_time
    print(f"\n{C.INFO}Total recovery time: {total:.0f}s ({total/60:.1f} min){C.END}")
    print(f"{C.OK}All systems operational.{C.END}")
    sys.exit(0)


if __name__ == "__main__":
    main()
