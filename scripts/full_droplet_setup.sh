#!/bin/bash
set -e
log() { echo "[$(date '+%H:%M:%S')] $1"; }

# === CONFIG ===
CONTAINER="clinsight"
HF_CACHE="/mnt/scratch/hf_cache"
VISION_DIR="${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR="${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"
REPO_LOCAL="/shared-docker/clinsight"
REPO_CONTAINER="/opt/clinsight"

log "=== STEP 1: Sync latest code from WSL to droplet ==="
cd ${REPO_LOCAL}
git fetch origin 2>/dev/null || true
git reset --hard HEAD 2>/dev/null || true
# Pull latest if we have remote
if git remote | grep -q origin; then
    git pull origin $(git rev-parse --abbrev-ref HEAD) 2>/dev/null || true
fi
log "Repo at: $(git rev-parse --short HEAD) - $(git log -1 --format=%s)"

log "=== STEP 2: Sync code into clinsight container ==="
# Use docker cp for speed
docker cp ${REPO_LOCAL}/backend ${CONTAINER}:${REPO_CONTAINER}/
docker cp ${REPO_LOCAL}/scripts ${CONTAINER}:${REPO_CONTAINER}/
docker cp ${REPO_LOCAL}/tests ${CONTAINER}:${REPO_CONTAINER}/
docker cp ${REPO_LOCAL}/frontend ${CONTAINER}:${REPO_CONTAINER}/
docker cp ${REPO_LOCAL}/hf_space ${CONTAINER}:${REPO_CONTAINER}/
docker cp ${REPO_LOCAL}/benchmarks ${CONTAINER}:${REPO_CONTAINER}/ 2>/dev/null || true
docker cp ${REPO_LOCAL}/requirements.txt ${CONTAINER}:${REPO_CONTAINER}/ 2>/dev/null || true
docker exec ${CONTAINER} bash -c "chown -R 1000:1000 ${REPO_CONTAINER} 2>/dev/null || true"
log "Code synced into container"

log "=== STEP 3: Kill stale vLLM ==="
# Kill in both containers to be safe
docker exec rocm bash -c 'pkill -f vllm.entrypoints || true' 2>/dev/null || true
docker exec ${CONTAINER} bash -c 'pkill -f vllm.entrypoints || true' 2>/dev/null || true
sleep 10
log "Stale vLLM killed"

log "=== STEP 4: Launch vision on :8000 (20% GPU) ==="
docker exec -d ${CONTAINER} bash -c "
    export HF_HOME=${HF_CACHE}
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
    export PYTORCH_ALLOC_CONF=expandable_segments:True
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${VISION_DIR} --served-model-name qwen2.5-vl-7b \
        --dtype float16 --tensor-parallel-size 1 \
        --port 8000 --host 0.0.0.0 \
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
    docker exec ${CONTAINER} bash -c 'tail -30 /tmp/vllm_vision.log'
    exit 1
fi

log "=== STEP 5: Launch text on :8001 (70% GPU) ==="
docker exec -d ${CONTAINER} bash -c "
    export HF_HOME=${HF_CACHE}
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
    export PYTORCH_ALLOC_CONF=expandable_segments:True
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${TEXT_DIR} --served-model-name qwen3.5-35b-a3b \
        --dtype float16 --tensor-parallel-size 1 \
        --port 8001 --host 0.0.0.0 \
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
    docker exec ${CONTAINER} bash -c 'tail -30 /tmp/vllm_text.log'
    exit 1
fi

log "=== STEP 6: Patch config ==="
docker exec ${CONTAINER} bash -c "cat > ${REPO_CONTAINER}/backend/core/config.py << 'PYEOF'
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    project_name: str = 'ClinSight'
    version: str = '0.1.0'
    debug: bool = False
    api_host: str = '0.0.0.0'
    api_port: int = 8002
    vllm_vision_url: str = 'http://localhost:8000/v1'
    vllm_text_url: str = 'http://localhost:8001/v1'
    use_mock: bool = False
    base_dir: Path = Path(__file__).resolve().parent.parent
    data_dir: Path = base_dir / 'data'
    cache_dir: Path = data_dir / 'contingency_cache'
    image_dir: Path = data_dir / 'images'
    class Config:
        env_file = '.env'

settings = Settings()
PYEOF
echo config_patched"

log "Verify:"
docker exec ${CONTAINER} bash -c "python3 -c 'import sys; sys.path.insert(0, \"${REPO_CONTAINER}\"); from backend.core.config import settings; print(\"mock=\", settings.use_mock, \"vision=\", settings.vllm_vision_url, \"text=\", settings.vllm_text_url)'"

log "=== STEP 7: GPU state ==="
rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -8

log "=== ALL DONE ==="
log "Vision: http://127.0.0.1:8000 -> ${V_READY}"
log "Text:   http://127.0.0.1:8001 -> ${T_READY}"
log "Backend config: use_mock=False, separate endpoints"
