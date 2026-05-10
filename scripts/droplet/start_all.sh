#!/bin/bash
set -e

export HF_HOME=/shared-docker/hf_cache
export HUGGINGFACE_HUB_CACHE=/shared-docker/hf_cache
export PYTORCH_ALLOC_CONF=expandable_segments:True

# Kill Jupyter (it will restart the container, but we'll handle that)
pkill -f "jupyter-lab" || true
sleep 2

# Kill any existing vLLM
pkill -f "vllm serve" || true
sleep 3

# Start vision vLLM
echo "Starting vision vLLM on port 8000..."
nohup vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
    --served-model-name qwen2.5-vl-7b \
    --dtype float16 \
    --tensor-parallel-size 1 \
    --port 8000 \
    --host 0.0.0.0 \
    --gpu-memory-utilization 0.20 \
    --max-model-len 8192 \
    --max-num-seqs 1 \
    --enforce-eager \
    --trust-remote-code \
    > /tmp/vllm_vision.log 2>&1 &

# Start text vLLM
echo "Starting text vLLM on port 30000..."
nohup vllm serve Qwen/Qwen3.5-35B-A3B \
    --served-model-name qwen3.5-35b-a3b \
    --dtype float16 \
    --tensor-parallel-size 1 \
    --port 30000 \
    --host 0.0.0.0 \
    --gpu-memory-utilization 0.50 \
    --max-model-len 4096 \
    --max-num-seqs 1 \
    --enforce-eager \
    --trust-remote-code \
    > /tmp/vllm_text.log 2>&1 &

# Wait for vLLM servers
echo "Waiting for vLLM servers..."
sleep 90

curl -s http://localhost:8000/v1/models > /dev/null && echo "Vision vLLM ready" || echo "Vision vLLM NOT ready"
curl -s http://localhost:30000/v1/models > /dev/null && echo "Text vLLM ready" || echo "Text vLLM NOT ready"

# Start ClinSight backend on port 8888
echo "Starting ClinSight backend on port 8888..."
cd /shared-docker
PYTHONPATH=/shared-docker nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8888 > /tmp/backend.log 2>&1 &

sleep 5
curl -s http://localhost:8888/health && echo "Backend ready" || echo "Backend NOT ready"

echo "All services started."
