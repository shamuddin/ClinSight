#!/bin/bash
set -euo pipefail
CONTAINER="rocm"
HF_CACHE="/mnt/scratch/hf_cache"
VISION_DIR="${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR="${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"
VISION_PORT=8000
TEXT_PORT=8001

echo "[INFO] Stopping any existing vLLM inside container..."
docker exec "${CONTAINER}" bash -c "pkill -f 'vllm.entrypoints' || true"
sleep 3

echo "[INFO] Launching vision server..."
docker exec -d "${CONTAINER}" bash -c "
    export HF_HOME=${HF_CACHE}
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
    export VLLM_USE_V1=0
    export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
    python3 -m vllm.entrypoints.openai.api_server \
        --model ${VISION_DIR} \
        --served-model-name qwen2.5-vl-7b \
        --dtype float16 \
        --tensor-parallel-size 1 \
        --port ${VISION_PORT} \
        --host 0.0.0.0 \
        --gpu-memory-utilization 0.30 \
        --max-model-len 8192 \
        --max-num-seqs 2 \
        --trust-remote-code \
        > /tmp/vllm_vision.log 2>&1
" &
echo "[INFO] Vision launched"

echo "[INFO] Launching text server..."
docker exec -d "${CONTAINER}" bash -c "
    export HF_HOME=${HF_CACHE}
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
    export VLLM_USE_V1=0
    export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
    python3 -m vllm.entrypoints.openai.api_server \
        --model ${TEXT_DIR} \
        --served-model-name qwen3.5-35b-a3b \
        --dtype float16 \
        --tensor-parallel-size 1 \
        --port ${TEXT_PORT} \
        --host 0.0.0.0 \
        --gpu-memory-utilization 0.55 \
        --max-model-len 4096 \
        --max-num-seqs 2 \
        --trust-remote-code \
        > /tmp/vllm_text.log 2>&1
" &
echo "[INFO] Text launched"

echo "[INFO] Waiting 120s for warmup..."
sleep 120

echo "[INFO] Checking servers..."
curl -s http://127.0.0.1:${VISION_PORT}/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('VISION:', d['data'][0]['id'])" 2>/dev/null || echo "VISION NOT READY"
curl -s http://127.0.0.1:${TEXT_PORT}/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('TEXT:', d['data'][0]['id'])" 2>/dev/null || echo "TEXT NOT READY"

echo "[INFO] rocm-smi..."
rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -8 || true
