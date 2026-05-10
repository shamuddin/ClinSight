#!/bin/bash
export HF_HOME=/shared-docker/hf_cache
export HUGGINGFACE_HUB_CACHE=/shared-docker/hf_cache
export PYTORCH_ALLOC_CONF=expandable_segments:True

pkill -f "vllm serve Qwen/Qwen3.5-35B-A3B" || true
sleep 5

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

echo "Text vLLM started with 0.50 memory utilization"
