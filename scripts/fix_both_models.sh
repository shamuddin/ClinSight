#!/bin/bash
set -e
log() { echo "[$(date '+%H:%M:%S')] $1"; }

CONTAINER="clinsight"
HF_CACHE="/mnt/scratch/hf_cache"
VISION_DIR="${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR="${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"

log "=== Kill stale vLLM ==="
docker exec rocm bash -c 'pkill -f vllm.entrypoints || true' 2>/dev/null || true
sleep 5
docker exec clinsight bash -c 'pkill -f vllm.entrypoints || true' 2>/dev/null || true
sleep 5

log "=== Launch vision on :8000 ==="
docker exec -d ${CONTAINER} bash -c "
    export HF_HOME=${HF_CACHE}; export HUGGINGFACE_HUB_CACHE=${HF_CACHE}; export PYTORCH_ALLOC_CONF=expandable_segments:True
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${VISION_DIR} --served-model-name qwen2.5-vl-7b \
        --dtype float16 --tensor-parallel-size 1 --port 8000 --host 0.0.0.0 \
        --gpu-memory-utilization 0.20 --max-model-len 8192 --max-num-seqs 2 \
        --enforce-eager --trust-remote-code \
        > /tmp/vllm_vision.log 2>&1 &
    echo vision_launched
"

log "Waiting 120s for vision..."
sleep 120

V_READY=$(curl -s http://127.0.0.1:8000/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["data"][0]["id"])' 2>/dev/null || echo NOT_READY)
log "Vision: ${V_READY}"

if [ "${V_READY}" = "NOT_READY" ]; then
    log "VISION FAILED"
    docker exec clinsight bash -c 'tail -20 /tmp/vllm_vision.log'
    exit 1
fi

log "=== Launch text on :8001 ==="
docker exec -d ${CONTAINER} bash -c "
    export HF_HOME=${HF_CACHE}; export HUGGINGFACE_HUB_CACHE=${HF_CACHE}; export PYTORCH_ALLOC_CONF=expandable_segments:True
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${TEXT_DIR} --served-model-name qwen3.5-35b-a3b \
        --dtype float16 --tensor-parallel-size 1 --port 8001 --host 0.0.0.0 \
        --gpu-memory-utilization 0.70 --max-model-len 4096 --max-num-seqs 2 \
        --enforce-eager --trust-remote-code \
        > /tmp/vllm_text.log 2>&1 &
    echo text_launched
"

log "Waiting 180s for text..."
sleep 180

T_READY=$(curl -s http://127.0.0.1:8001/v1/models 2>/dev/null | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["data"][0]["id"])' 2>/dev/null || echo NOT_READY)
log "Text: ${T_READY}"

if [ "${T_READY}" = "NOT_READY" ]; then
    log "TEXT FAILED"
    docker exec clinsight bash -c 'tail -20 /tmp/vllm_text.log'
    exit 1
fi

log "=== Patch config ==="
docker exec clinsight bash -c 'cat > /opt/clinsight/backend/core/config.py << EOF
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    project_name: str = "ClinSight"
    version: str = "0.1.0"
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    vllm_vision_url: str = "http://localhost:8000/v1"
    vllm_text_url: str = "http://localhost:8001/v1"
    use_mock: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / "data"
    cache_dir: Path = data_dir / "contingency_cache"
    image_dir: Path = data_dir / "images"
    class Config:
        env_file = ".env"

settings = Settings()
EOF'

log "Verify config:"
docker exec clinsight bash -c 'python3 -c "import sys; sys.path.insert(0, \"/opt/clinsight\"); from backend.core.config import settings; print(\"mock=\", settings.use_mock)"'

log "=== GPU ==="
rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -5

log "=== SERVERS RUNNING ==="
