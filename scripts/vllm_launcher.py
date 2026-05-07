#!/usr/bin/env python3
"""Host-side launcher: starts vLLM inside the 'rocm' container and monitors."""
import subprocess, time, sys, json, os

CONTAINER = "rocm"
HF_CACHE = "/mnt/scratch/hf_cache"
VISION_DIR = f"{HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR = f"{HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"
VISION_PORT = 8000
TEXT_PORT = 8001
LOG = "/root/vllm_launcher.log"

def log(msg):
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def run_in_container(cmd: str):
    return subprocess.run(
        ["docker", "exec", "-d", CONTAINER, "bash", "-c", cmd],
        capture_output=True, text=True
    )

def check_port(port: int) -> bool:
    try:
        r = subprocess.run(
            ["curl", "-s", f"http://127.0.0.1:{port}/v1/models"],
            capture_output=True, text=True, timeout=5
        )
        return r.returncode == 0 and "id" in r.stdout
    except Exception:
        return False

log("=== Launcher started ===")

# Kill stale
log("Killing stale vLLM...")
subprocess.run(["docker", "exec", CONTAINER, "bash", "-c", "pkill -f vllm.entrypoints || true"], capture_output=True)
time.sleep(3)

# Launch vision
log("Launching vision server...")
vision_cmd = f"""
export HF_HOME={HF_CACHE}
export HUGGINGFACE_HUB_CACHE={HF_CACHE}
export VLLM_USE_V1=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model {VISION_DIR} \
    --served-model-name qwen2.5-vl-7b \
    --dtype float16 --tensor-parallel-size 1 --port {VISION_PORT} --host 0.0.0.0 \
    --gpu-memory-utilization 0.30 --max-model-len 8192 --max-num-seqs 2 --trust-remote-code \
    > /tmp/vllm_vision.log 2>&1 &
echo $!
"""
run_in_container(vision_cmd)
time.sleep(2)

# Launch text
log("Launching text server...")
text_cmd = f"""
export HF_HOME={HF_CACHE}
export HUGGINGFACE_HUB_CACHE={HF_CACHE}
export VLLM_USE_V1=0
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model {TEXT_DIR} \
    --served-model-name qwen3.5-35b-a3b \
    --dtype float16 --tensor-parallel-size 1 --port {TEXT_PORT} --host 0.0.0.0 \
    --gpu-memory-utilization 0.55 --max-model-len 4096 --max-num-seqs 2 --trust-remote-code \
    > /tmp/vllm_text.log 2>&1 &
echo $!
"""
run_in_container(text_cmd)

# Wait loop
log("Waiting for servers (up to 300s)...")
vision_ok = False
text_ok = False
for i in range(60):
    time.sleep(5)
    if not vision_ok and check_port(VISION_PORT):
        vision_ok = True
        log("VISION READY")
    if not text_ok and check_port(TEXT_PORT):
        text_ok = True
        log("TEXT READY")
    if vision_ok and text_ok:
        break
    log(f"  wait {i+1}/60: V={vision_ok} T={text_ok}")

if not vision_ok:
    log("VISION FAILED")
if not text_ok:
    log("TEXT FAILED")

# Health check
log("Running health checks...")
try:
    r = subprocess.run(["curl", "-s", f"http://127.0.0.1:{VISION_PORT}/v1/models"], capture_output=True, text=True, timeout=5)
    d = json.loads(r.stdout)
    log(f"VISION MODEL: {d['data'][0]['id']}")
except Exception as e:
    log(f"VISION health failed: {e}")

try:
    r = subprocess.run(["curl", "-s", f"http://127.0.0.1:{TEXT_PORT}/v1/models"], capture_output=True, text=True, timeout=5)
    d = json.loads(r.stdout)
    log(f"TEXT MODEL: {d['data'][0]['id']}")
except Exception as e:
    log(f"TEXT health failed: {e}")

# GPU
log("GPU state:")
try:
    r = subprocess.run(["rocm-smi", "--showmeminfo", "vram", "--showuse"], capture_output=True, text=True, timeout=10)
    log(r.stdout[:500])
except Exception as e:
    log(f"rocm-smi failed: {e}")

log("=== Launcher done ===")
