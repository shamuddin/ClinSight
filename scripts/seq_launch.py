#!/usr/bin/env python3
"""Sequential vLLM launcher: start vision, wait, then text."""
import subprocess, time, json, sys

CONTAINER = "rocm"
HF_CACHE = "/mnt/scratch/hf_cache"
VISION_DIR = f"{HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR = f"{HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"
VISION_PORT = 8000
TEXT_PORT = 8001

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def is_running(port):
    try:
        r = subprocess.run(["curl", "-s", f"http://127.0.0.1:{port}/v1/models"], capture_output=True, text=True, timeout=5)
        return r.returncode == 0 and "id" in r.stdout
    except Exception:
        return False

def kill_vllm():
    log("Killing any existing vLLM...")
    subprocess.run(["docker", "exec", CONTAINER, "bash", "-c", "pkill -f vllm.entrypoints || true"], capture_output=True)
    time.sleep(5)

def launch_vision():
    log("Launching vision server...")
    cmd = f"""export HF_HOME={HF_CACHE}
export HUGGINGFACE_HUB_CACHE={HF_CACHE}
export PYTORCH_ALLOC_CONF=expandable_segments:True
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model {VISION_DIR} \
    --served-model-name qwen2.5-vl-7b \
    --dtype float16 --tensor-parallel-size 1 \
    --port {VISION_PORT} --host 0.0.0.0 \
    --gpu-memory-utilization 0.95 --max-model-len 8192 --max-num-seqs 2 \
    --enforce-eager --trust-remote-code \
    > /tmp/vllm_vision.log 2>&1 &
echo vision_launched"""
    subprocess.run(["docker", "exec", "-d", CONTAINER, "bash", "-c", cmd], capture_output=True)

def launch_text():
    log("Launching text server...")
    cmd = f"""export HF_HOME={HF_CACHE}
export HUGGINGFACE_HUB_CACHE={HF_CACHE}
export PYTORCH_ALLOC_CONF=expandable_segments:True
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model {TEXT_DIR} \
    --served-model-name qwen3.5-35b-a3b \
    --dtype float16 --tensor-parallel-size 1 \
    --port {TEXT_PORT} --host 0.0.0.0 \
    --gpu-memory-utilization 0.95 --max-model-len 4096 --max-num-seqs 2 \
    --enforce-eager --trust-remote-code \
    > /tmp/vllm_text.log 2>&1 &
echo text_launched"""
    subprocess.run(["docker", "exec", "-d", CONTAINER, "bash", "-c", cmd], capture_output=True)

def wait_for(port, name, max_wait=300):
    log(f"Waiting for {name} on :{port} (max {max_wait}s)...")
    for i in range(max_wait // 5):
        time.sleep(5)
        if is_running(port):
            log(f"{name} READY!")
            return True
        log(f"  wait {i+1}/{max_wait//5}...")
    log(f"{name} FAILED after {max_wait}s")
    return False

# Main
log("=== Sequential vLLM Launcher ===")
kill_vllm()

launch_vision()
if not wait_for(VISION_PORT, "VISION", max_wait=300):
    log("VISION failed — aborting")
    sys.exit(1)

launch_text()
if not wait_for(TEXT_PORT, "TEXT", max_wait=300):
    log("TEXT failed — aborting")
    sys.exit(1)

log("=== Both servers running ===")
log("GPU state:")
subprocess.run(["rocm-smi", "--showmeminfo", "vram", "--showuse"])
log("Done.")
