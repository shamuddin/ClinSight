#!/bin/bash
set -e
CONTAINER="rocm"
HF_CACHE="/mnt/scratch/hf_cache"
VISION_DIR="${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR="${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"

echo "[$(date)] Killing stale vLLM..."
docker exec "${CONTAINER}" bash -c "pkill -f vllm.entrypoints || true"
sleep 5

echo "[$(date)] Vision at 20% GPU (38GB of 192GB)..."
docker exec -d "${CONTAINER}" bash -c "
    export HF_HOME=${HF_CACHE}
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
    export PYTORCH_ALLOC_CONF=expandable_segments:True
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${VISION_DIR} \
        --served-model-name qwen2.5-vl-7b \
        --dtype float16 --tensor-parallel-size 1 \
        --port 8000 --host 0.0.0.0 \
        --gpu-memory-utilization 0.20 \
        --max-model-len 8192 --max-num-seqs 2 \
        --enforce-eager --trust-remote-code \
        > /tmp/vllm_vision.log 2>&1 &
echo 'vision launched'
"

echo "[$(date)] Waiting 120s for vision warmup..."
sleep 120

echo "[$(date)] Text at 70% GPU (134GB of 192GB)..."
docker exec -d "${CONTAINER}" bash -c "
    export HF_HOME=${HF_CACHE}
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
    export PYTORCH_ALLOC_CONF=expandable_segments:True
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${TEXT_DIR} \
        --served-model-name qwen3.5-35b-a3b \
        --dtype float16 --tensor-parallel-size 1 \
        --port 8001 --host 0.0.0.0 \
        --gpu-memory-utilization 0.70 \
        --max-model-len 4096 --max-num-seqs 2 \
        --enforce-eager --trust-remote-code \
        > /tmp/vllm_text.log 2>&1 &
echo 'text launched'
"

echo "[$(date)] Waiting 180s for text warmup..."
sleep 180

echo "[$(date)] Checking servers..."
curl -s http://127.0.0.1:8000/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('VISION:', d['data'][0]['id'])" 2>/dev/null || echo "VISION NOT READY"
curl -s http://127.0.0.1:8001/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('TEXT:', d['data'][0]['id'])" 2>/dev/null || echo "TEXT NOT READY"

echo "[$(date)] rocm-smi:"
rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -10 || true
echo "[$(date)] Done"
