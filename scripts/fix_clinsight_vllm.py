#!/usr/bin/env python3
"""Fix droplet: run BOTH vLLM servers inside 'clinsight' container with host networking."""
import subprocess, time, sys, json

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()

def run(cmd, timeout=60):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

def docker_exec(cmd, timeout=60):
    return run(f"docker exec clinsight bash -c '{cmd}'", timeout=timeout)

# 1. Kill vLLM in rocm container
log("Killing vLLM in rocm container...")
run("docker exec rocm bash -c 'pkill -f vllm.entrypoints || true'")
time.sleep(5)

# 2. Kill any stale vLLM in clinsight
log("Killing stale vLLM in clinsight...")
docker_exec("pkill -f vllm.entrypoints || true")
time.sleep(5)

# 3. Verify clinsight GPU access
r = docker_exec("rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -5")
log(f"GPU in clinsight:\n{r.stdout.strip()}")

# 4. Check models exist
HF_CACHE = "/mnt/scratch/hf_cache"
r = docker_exec(f"ls -d {HF_CACHE}/models--Qwen* 2>/dev/null")
log(f"Models:\n{r.stdout.strip()}")

VISION_DIR = f"{HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR = f"{HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"

# 5. Launch vision in clinsight (background)
log("Launching vision server in clinsight on :8000...")
docker_exec(f"""export HF_HOME={HF_CACHE}; export HUGGINGFACE_HUB_CACHE={HF_CACHE}; export PYTORCH_ALLOC_CONF=expandable_segments:True
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model {VISION_DIR} --served-model-name qwen2.5-vl-7b \
    --dtype float16 --tensor-parallel-size 1 --port 8000 --host 0.0.0.0 \
    --gpu-memory-utilization 0.20 --max-model-len 8192 --max-num-seqs 2 \
    --enforce-eager --trust-remote-code \
    > /tmp/vllm_vision.log 2>&1 &
echo vision_launched""")
time.sleep(2)

# Wait for vision
log("Waiting for vision ready...")
vision_ready = False
for i in range(60):
    time.sleep(5)
    r = run("curl -s http://127.0.0.1:8000/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[\"data\"][0][\"id\"])' 2>/dev/null || echo 'NOT_READY'")
    if r.stdout.strip() not in ("", "NOT_READY"):
        log(f"VISION READY: {r.stdout.strip()}")
        vision_ready = True
        break
    log(f"  wait {i+1}/60...")

if not vision_ready:
    log("VISION FAILED")
    r = docker_exec("cat /tmp/vllm_vision.log | tail -20")
    log(f"Vision log:\n{r.stdout}")
    sys.exit(1)

# 6. Launch text in clinsight (background)
log("Launching text server in clinsight on :8001...")
docker_exec(f"""export HF_HOME={HF_CACHE}; export HUGGINGFACE_HUB_CACHE={HF_CACHE}; export PYTORCH_ALLOC_CONF=expandable_segments:True
nohup python3 -m vllm.entrypoints.openai.api_server \
    --model {TEXT_DIR} --served-model-name qwen3.5-35b-a3b \
    --dtype float16 --tensor-parallel-size 1 --port 8001 --host 0.0.0.0 \
    --gpu-memory-utilization 0.70 --max-model-len 4096 --max-num-seqs 2 \
    --enforce-eager --trust-remote-code \
    > /tmp/vllm_text.log 2>&1 &
echo text_launched""")
time.sleep(2)

# Wait for text
log("Waiting for text ready...")
text_ready = False
for i in range(60):
    time.sleep(5)
    r = run("curl -s http://127.0.0.1:8001/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d[\"data\"][0][\"id\"])' 2>/dev/null || echo 'NOT_READY'")
    if r.stdout.strip() not in ("", "NOT_READY"):
        log(f"TEXT READY: {r.stdout.strip()}")
        text_ready = True
        break
    log(f"  wait {i+1}/60...")

if not text_ready:
    log("TEXT FAILED")
    r = docker_exec("cat /tmp/vllm_text.log | tail -20")
    log(f"Text log:\n{r.stdout}")
    sys.exit(1)

# 7. Patch backend config
log("Patching backend config in clinsight...")
patch = "\"\"\"from pydantic_settings import BaseSettings\nfrom pathlib import Path\n\nclass Settings(BaseSettings):\n    project_name: str = 'ClinSight'\n    version: str = '0.1.0'\n    debug: bool = False\n    api_host: str = '0.0.0.0'\n    api_port: int = 8000\n    vllm_vision_url: str = 'http://localhost:8000/v1'\n    vllm_text_url: str = 'http://localhost:8001/v1'\n    use_mock: bool = False\n    base_dir: Path = Path(__file__).resolve().parent.parent\n    data_dir: Path = base_dir / 'data'\n    cache_dir: Path = data_dir / 'contingency_cache'\n    image_dir: Path = data_dir / 'images'\n    class Config:\n        env_file = '.env'\n\nsettings = Settings()\n\"\"\""
with open('/opt/clinsight/backend/core/config.py', 'w') as f:
    f.write(patch)
print('patched')"

docker_exec(f"python3 -c {repr(patch)}")
log("Config patched")

# 8. Verify
r = docker_exec("python3 -c 'import sys; sys.path.insert(0, \"/opt/clinsight\"); from backend.core.config import settings; print(settings.use_mock, settings.vllm_vision_url, settings.vllm_text_url)'")
log(f"Config verify: {r.stdout.strip()}")

# 9. GPU state
r = run("rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -10")
log(f"GPU state:\n{r.stdout.strip()}")

log("=== BOTH SERVERS RUNNING IN clinsight ===")
