#!/usr/bin/env python3
"""Launch single vision server (handles both image + text) and patch backend config."""
import subprocess, time, sys, json

CONTAINER = "rocm"
HF_CACHE = "/mnt/scratch/hf_cache"
VISION_DIR = f"{HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
REPO = "/opt/clinsight"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

# Kill stale
log("Killing stale vLLM...")
subprocess.run(["docker", "exec", CONTAINER, "bash", "-c", "pkill -f vllm.entrypoints || true"], capture_output=True)
time.sleep(5)

# Launch vision server only
log("Launching vision server (95% GPU)...")
cmd = f"""export HF_HOME={HF_CACHE}
export HUGGINGFACE_HUB_CACHE={HF_CACHE}
export PYTORCH_ALLOC_CONF=expandable_segments:True
python3 -m vllm.entrypoints.openai.api_server \
    --model {VISION_DIR} \
    --served-model-name qwen2.5-vl-7b \
    --dtype float16 --tensor-parallel-size 1 \
    --port 8000 --host 0.0.0.0 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 8192 --max-num-seqs 2 \
    --enforce-eager --trust-remote-code \
    > /tmp/vllm_vision.log 2>&1 &
echo launched"""
subprocess.run(["docker", "exec", "-d", CONTAINER, "bash", "-c", cmd], capture_output=True)

# Wait for server
log("Waiting for vision server...")
for i in range(60):
    time.sleep(5)
    try:
        r = subprocess.run(
            ["curl", "-s", "http://127.0.0.1:8000/v1/models"],
            capture_output=True, text=True, timeout=5
        )
        if r.returncode == 0 and "id" in r.stdout:
            d = json.loads(r.stdout)
            log(f"VISION READY: {d['data'][0]['id']}")
            break
    except Exception:
        pass
    log(f"  wait {i+1}/60...")
else:
    log("VISION FAILED")
    sys.exit(1)

# Patch backend config to use same server for both
log("Patching backend config...")
patch_cmd = f"""cd {REPO}
# Patch config to use vision server for both clients
sed -i 's|http://127.0.0.1:8000/v1|http://127.0.0.1:8000/v1|g' backend/core/config.py || true
sed -i 's|http://127.0.0.1:8001/v1|http://127.0.0.1:8000/v1|g' backend/core/config.py || true
echo patched"""
subprocess.run(["docker", "exec", CONTAINER, "bash", "-c", patch_cmd], capture_output=True)

# Health check: send a text completion
log("Health check: text inference...")
health = subprocess.run(
    ["curl", "-s", "http://127.0.0.1:8000/v1/chat/completions", "-H", "Content-Type: application/json", "-d", json.dumps({"model": "qwen2.5-vl-7b", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 5})],
    capture_output=True, text=True, timeout=30
)
if health.returncode == 0:
    try:
        d = json.loads(health.stdout)
        content = d["choices"][0]["message"]["content"]
        log(f"Health OK: response='{content}'")
    except Exception as e:
        log(f"Health parse issue: {e}")
else:
    log(f"Health check failed: {health.stderr}")

log("=== Single-server setup complete ===")
log("GPU state:")
subprocess.run(["rocm-smi", "--showmeminfo", "vram", "--showuse"])
