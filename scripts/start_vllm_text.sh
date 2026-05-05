#!/usr/bin/env bash
# =============================================================================
# Start vLLM Text Model Server (Qwen3.5-35B-A3B)
# =============================================================================
# Port: 8001 (default)
# Model: Qwen/Qwen3.5-35B-A3B (or compatible MoE text model)
# GPU: 1x AMD GPU, tensor-parallel = 1 (adjust if multi-GPU)
# =============================================================================
set -euo pipefail

MODEL_ID="${TEXT_MODEL:-Qwen/Qwen3.5-35B-A3B}"
PORT="${TEXT_PORT:-8001}"
GPU_MEMORY="${GPU_MEMORY_UTIL:-0.90}"
MAX_MODEL_LEN="${TEXT_MAX_LEN:-8192}"
TP_SIZE="${TEXT_TP_SIZE:-1}"
QUANTIZATION="${TEXT_QUANT:-none}"  # options: none, awq, gptq, fp8

echo "=== Starting vLLM Text Server ==="
echo "Model:  ${MODEL_ID}"
echo "Port:   ${PORT}"
echo "GPU:    ${GPU_MEMORY_UTIL} memory utilization"
echo "TP:     ${TP_SIZE}"
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
    --tensor-parallel-size "${TP_SIZE}" \
    --gpu-memory-utilization "${GPU_MEMORY}" \
    --max-model-len "${MAX_MODEL_LEN}" \
    --max-num-seqs 4 \
    --enable-chunked-prefill \
    --trust-remote-code \
    ${QFLAG} \
    "$@"
