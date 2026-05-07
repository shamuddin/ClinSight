#!/usr/bin/env python3
"""Fast launcher: starts both vLLM servers via docker exec -d and exits immediately."""
import subprocess, time, sys

CONTAINER = "rocm"
HF_CACHE = "/mnt/scratch/hf_cache"
VISION_DIR = f"{HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR = f"{HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"

def run(cmd: str):
    subprocess.run(["docker", "exec", "-d", CONTAINER, "bash", "-c", cmd], capture_output=True)

# Kill stale
print("[1/4] Killing stale vLLM...")
subprocess.run(["docker", "exec", CONTAINER, "bash", "-c", "pkill -f vllm.entrypoints || true"], capture_output=True)
time.sleep(3)

# Vision
print("[2/4] Launching vision (20% GPU)...")
run(f"""export HF_HOME={HF_CACHE}; export HUGGINGFACE_HUB_CACHE={HF_CACHE}; export PYTORCH_ALLOC_CONF=expandable_segments:True
python3 -m vllm.entrypoints.openai.api_server --model {VISION_DIR} --served-model-name qwen2.5-vl-7b --dtype float16 --tensor-parallel-size 1 --port 8000 --host 0.0.0.0 --gpu-memory-utilization 0.20 --max-model-len 8192 --max-num-seqs 2 --enforce-eager --trust-remote-code > /tmp/vllm_vision.log 2>&1 &
echo vision_started""")
time.sleep(2)

# Text
print("[3/4] Launching text (70% GPU)...")
run(f"""export HF_HOME={HF_CACHE}; export HUGGINGFACE_HUB_CACHE={HF_CACHE}; export PYTORCH_ALLOC_CONF=expandable_segments:True
python3 -m vllm.entrypoints.openai.api_server --model {TEXT_DIR} --served-model-name qwen3.5-35b-a3b --dtype float16 --tensor-parallel-size 1 --port 8001 --host 0.0.0.0 --gpu-memory-utilization 0.70 --max-model-len 4096 --max-num-seqs 2 --enforce-eager --trust-remote-code > /tmp/vllm_text.log 2>&1 &
echo text_started""")

print("[4/4] Done. Servers are starting in background.")
print("Poll with: curl http://127.0.0.1:8000/v1/models")
