#!/bin/bash
export HF_HOME=/shared-docker/hf_cache
export HUGGINGFACE_HUB_CACHE=/shared-docker/hf_cache
export PYTORCH_ALLOC_CONF=expandable_segments:True

pkill -f "vllm serve" || true
sleep 5

# Start text vLLM with lower memory
echo "Starting text vLLM on port 30000..."
nohup vllm serve Qwen/Qwen3.5-35B-A3B \
    --served-model-name qwen3.5-35b-a3b \
    --dtype float16 \
    --tensor-parallel-size 1 \
    --port 30000 \
    --host 0.0.0.0 \
    --gpu-memory-utilization 0.45 \
    --max-model-len 4096 \
    --max-num-seqs 1 \
    --enforce-eager \
    --trust-remote-code \
    > /tmp/vllm_text.log 2>&1 &

sleep 60

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

sleep 60

curl -s http://localhost:30000/v1/models > /dev/null && echo "Text vLLM ready" || echo "Text vLLM not ready"
curl -s http://localhost:8000/v1/models > /dev/null && echo "Vision vLLM ready" || echo "Vision vLLM not ready"
