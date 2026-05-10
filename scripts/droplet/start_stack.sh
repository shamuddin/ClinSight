#!/bin/bash
set -e

export HF_HOME=/shared-docker/hf_cache
export HUGGINGFACE_HUB_CACHE=/shared-docker/hf_cache
export PYTORCH_ALLOC_CONF=expandable_segments:True

# Kill any existing processes
pkill -f "vllm serve" || true
pkill -f "backend.api.main:app" || true
sleep 2

# Start vision vLLM server
echo "Starting vision vLLM server on port 8000..."
nohup vllm serve Qwen/Qwen2.5-VL-7B-Instruct \
    --served-model-name qwen2.5-vl-7b \
    --dtype float16 \
    --tensor-parallel-size 1 \
    --port 8000 \
    --host 0.0.0.0 \
    --gpu-memory-utilization 0.20 \
    --max-model-len 8192 \
    --max-num-seqs 2 \
    --enforce-eager \
    --trust-remote-code \
    > /tmp/vllm_vision.log 2>&1 &

# Start text vLLM server
echo "Starting text vLLM server on port 30000..."
nohup vllm serve Qwen/Qwen3.5-35B-A3B \
    --served-model-name qwen3.5-35b-a3b \
    --dtype float16 \
    --tensor-parallel-size 1 \
    --port 30000 \
    --host 0.0.0.0 \
    --gpu-memory-utilization 0.70 \
    --max-model-len 4096 \
    --max-num-seqs 2 \
    --enforce-eager \
    --trust-remote-code \
    > /tmp/vllm_text.log 2>&1 &

# Wait for vLLM servers to be ready
echo "Waiting for vLLM servers to start..."
sleep 30

# Check if servers are up
curl -s http://localhost:8000/v1/models > /dev/null && echo "Vision vLLM ready" || echo "Vision vLLM not ready yet"
curl -s http://localhost:30000/v1/models > /dev/null && echo "Text vLLM ready" || echo "Text vLLM not ready yet"

# Start ClinSight backend
echo "Starting ClinSight backend on port 8888..."
cd /shared-docker
PYTHONPATH=/shared-docker nohup python3 -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8888 > /tmp/backend.log 2>&1 &

sleep 5
curl -s http://localhost:8888/health && echo "Backend ready" || echo "Backend not ready yet"

echo "Stack startup complete."
