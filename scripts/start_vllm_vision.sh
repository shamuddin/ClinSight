#!/usr/bin/env bash
# =============================================================================
# Start vLLM Vision Model Server (Qwen2.5-VL-7B-Instruct)
# =============================================================================
# Port: 8000 (default)
# Model: Qwen2.5-VL-7B-Instruct (or compatible vision-LM)
# GPU: 1x AMD GPU, tensor-parallel = 1
# =============================================================================
set -euo pipefail

MODEL_ID="${VISION_MODEL:-Qwen/Qwen2.5-VL-7B-Instruct}"
PORT="${VISION_PORT:-8000}"
GPU_MEMORY="${GPU_MEMORY_UTIL:-0.90}"
MAX_MODEL_LEN="${VISION_MAX_LEN:-4096}"
QUANTIZATION="${VISION_QUANT:-none}"  # options: none, awq, gptq

echo "=== Starting vLLM Vision Server ==="
echo "Model:  ${MODEL_ID}"
echo "Port:   ${PORT}"
echo "GPU:    ${GPU_MEMORY_UTIL} memory utilization"
echo ""

# Optional quantization flag
QFLAG=""
if [[ "$QUANTIZATION" != "none" ]]; then
    QFLAG="--quantization ${QUANTIZATION}"
fi

python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL_ID}" \
    --port "${PORT}" \
    --dtype bfloat16 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization "${GPU_MEMORY}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --max-num-seqs 4 \
    --enable-chunked-prefill \
    --trust-remote-code \
    ${QFLAG} \
    "$@"
