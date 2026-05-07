#!/bin/bash
set -euo pipefail

# ── Config ──
CONTAINER="rocm"
HF_CACHE="/mnt/scratch/hf_cache"
REPO_LOCAL="/shared-docker/clinsight"
REPO_CONTAINER="/opt/clinsight"
VISION_MODEL="Qwen/Qwen2.5-VL-7B-Instruct"
TEXT_MODEL="Qwen/Qwen3.5-35B-A3B"
VISION_PORT=8000
TEXT_PORT=8001

RED='\033[91m'; GRN='\033[92m'; YLW='\033[93m'; BLU='\033[94m'; RST='\033[0m'
info()  { echo -e "${BLU}[INFO]${RST}  $*"; }
ok()    { echo -e "${GRN}[OK]${RST}    $*"; }
warn()  { echo -e "${YLW}[WARN]${RST}  $*"; }
fail()  { echo -e "${RED}[FAIL]${RST}  $*"; exit 1; }
step() { echo ""; echo "============================================================"; echo -e "${BLU}>>> $*${RST}"; echo "============================================================"; }

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Mount scratch
# ═══════════════════════════════════════════════════════════════════════════════
step "1. SCRATCH DISK"
mkdir -p /mnt/scratch
df -h /mnt/scratch | grep -q /mnt/scratch || mount /dev/vdc1 /mnt/scratch || true
ok "Scratch: $(df -h /mnt/scratch | tail -1 | awk '{print $4}') available"

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Sync code
# ═══════════════════════════════════════════════════════════════════════════════
step "2. CODE SYNC"
# The local repo in /shared-docker/clinsight is old (May 5). Sync fresh.
if [ -d "${REPO_LOCAL}" ]; then
    info "Syncing ${REPO_LOCAL} -> container ${REPO_CONTAINER}..."
    docker exec "${CONTAINER}" rm -rf "${REPO_CONTAINER}" || true
    docker exec "${CONTAINER}" mkdir -p "${REPO_CONTAINER}"
    docker cp "${REPO_LOCAL}/." "${CONTAINER}:${REPO_CONTAINER}/" || warn "docker cp had issues"
    ok "Code synced"
else
    warn "No repo at ${REPO_LOCAL}"
fi

# Export HF token in container for gated models if needed
info "Setting HF token..."
HF_TOKEN="${HF_TOKEN:-}"
if [ -n "$HF_TOKEN" ]; then
    docker exec "${CONTAINER}" bash -c "mkdir -p /root/.cache/huggingface && echo '$HF_TOKEN' > /root/.cache/huggingface/token" || true
    ok "HF token set"
else
    warn "No HF_TOKEN env var — proceeding without token (models must be public)"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Dependencies
# ═══════════════════════════════════════════════════════════════════════════════
step "3. DEPENDENCIES"
MISSING=""
for pkg in fastapi uvicorn pydantic httpx openai Pillow numpy langgraph langchain; do
    docker exec "${CONTAINER}" bash -c "python3 -c 'import ${pkg}'" 2>/dev/null || MISSING="${MISSING} ${pkg}"
done
if [ -n "${MISSING}" ]; then
    info "Installing: ${MISSING}"
    docker exec "${CONTAINER}" pip install -q ${MISSING} || warn "Some packages failed"
    ok "Packages installed"
else
    ok "All deps present"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 4: Model Download
# ═══════════════════════════════════════════════════════════════════════════════
step "4. MODEL DOWNLOAD"

VISION_DIR="${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR="${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"

if [ -f "${VISION_DIR}/config.json" ]; then
    ok "Vision model already cached"
else
    info "Downloading vision model (7B, ~15GB)..."
    docker exec "${CONTAINER}" bash -c "
        export HF_HOME=${HF_CACHE}
        export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
        huggingface-cli download ${VISION_MODEL} --local-dir ${VISION_DIR} --local-dir-use-symlinks False
    " || warn "Vision download may have failed"
    ok "Vision download complete"
fi

if [ -f "${TEXT_DIR}/config.json" ]; then
    ok "Text model already cached"
else
    info "Downloading text model (35B-A3B, ~70GB)..."
    docker exec "${CONTAINER}" bash -c "
        export HF_HOME=${HF_CACHE}
        export HUGGINGFACE_HUB_CACHE=${HF_CACHE}
        huggingface-cli download ${TEXT_MODEL} --local-dir ${TEXT_DIR} --local-dir-use-symlinks False
    " || warn "Text download may have failed"
    ok "Text download complete"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: vLLM Launch
# ═══════════════════════════════════════════════════════════════════════════════
step "5. VLLM LAUNCH"

# Kill stale
info "Killing stale vLLM..."
docker exec "${CONTAINER}" bash -c "pkill -f vllm.entrypoints || true"
sleep 3

# Vision
info "Starting vision server on :${VISION_PORT}..."
docker exec -d "${CONTAINER}" bash -c "
    export HF_HOME=${HF_CACHE};
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE};
    export VLLM_USE_V1=0;
    export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True;
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${VISION_DIR} \
        --served-model-name qwen2.5-vl-7b \
        --dtype float16 \
        --tensor-parallel-size 1 \
        --port ${VISION_PORT} \
        --host 0.0.0.0 \
        --gpu-memory-utilization 0.30 \
        --max-model-len 8192 \
        --max-num-seqs 2 \
        --trust-remote-code > /tmp/vllm_vision.log 2>&1 &
echo 'vision launched'
"
sleep 2

# Text
info "Starting text server on :${TEXT_PORT}..."
docker exec -d "${CONTAINER}" bash -c "
    export HF_HOME=${HF_CACHE};
    export HUGGINGFACE_HUB_CACHE=${HF_CACHE};
    export VLLM_USE_V1=0;
    export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True;
    nohup python3 -m vllm.entrypoints.openai.api_server \
        --model ${TEXT_DIR} \
        --served-model-name qwen3.5-35b-a3b \
        --dtype float16 \
        --tensor-parallel-size 1 \
        --port ${TEXT_PORT} \
        --host 0.0.0.0 \
        --gpu-memory-utilization 0.55 \
        --max-model-len 4096 \
        --max-num-seqs 2 \
        --trust-remote-code > /tmp/vllm_text.log 2>&1 &
echo 'text launched'
"

# Wait
info "Waiting for servers..."
VISION_OK=false
TEXT_OK=false
for i in $(seq 1 60); do
    sleep 5
    if curl -s http://127.0.0.1:${VISION_PORT}/v1/models 2>/dev/null | grep -q id; then VISION_OK=true; fi
    if curl -s http://127.0.0.1:${TEXT_PORT}/v1/models   2>/dev/null | grep -q id; then TEXT_OK=true; fi
    ${VISION_OK} && ${TEXT_OK} && { ok "Both servers ready"; break; }
    echo "  wait $i/60: V=$((${VISION_OK} && echo 1 || echo 0)) T=$((${TEXT_OK} && echo 1 || echo 0))"
done

${VISION_OK} || fail "Vision server failed"
${TEXT_OK}   || fail "Text server failed"

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 6: Health Check
# ═══════════════════════════════════════════════════════════════════════════════
step "6. HEALTH CHECK"

curl -s http://127.0.0.1:${VISION_PORT}/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('VISION:', d['data'][0]['id'])" && ok "Vision API OK"
curl -s http://127.0.0.1:${TEXT_PORT}/v1/models   | python3 -c "import sys,json; d=json.load(sys.stdin); print('TEXT:  ', d['data'][0]['id'])" && ok "Text API OK"

rocm-smi --showproductname --showmeminfo vram --showuse 2>/dev/null | head -8 || true

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 7: Quick E2E
# ═══════════════════════════════════════════════════════════════════════════════
step "7. E2E TEST"
docker exec "${CONTAINER}" bash -c "
cd ${REPO_CONTAINER}
cat > /tmp/e2e.py << 'PYEOF'
import sys, asyncio, json
sys.path.insert(0, '${REPO_CONTAINER}')
from backend.agents.graph import run_pipeline
state = {
    'case_id': 'CS-2024-001',
    'image_path': 'data/images/demo_chest_pain.png',
    'lab_values': {'troponin_i':0.12,'bnp':180,'crp':12,'wbc':9.2,'hemoglobin':14.1,'platelets':245,'creatinine':0.9,'glucose':105},
    'lab_units': {'troponin_i':'ng/L','bnp':'pg/mL','crp':'mg/L','wbc':'K/uL','hemoglobin':'g/dL','platelets':'K/uL','creatinine':'mg/dL','glucose':'mg/dL'},
    'triage_note':'45yo male with chest pain',
    'patient_age':45,'patient_sex':'M','patient_race':'White','chief_complaint':'Chest pain',
    'vitals':{'bp':'120/80','hr':72,'rr':16,'temp':37.0,'spo2':98},
    'image_hash':'','quality_gate':{},'pediatric_gate':{},'input_warnings':[],
    'image_features':{},'findings':[],'attention_regions':[],'lab_alerts':[],'lab_patterns':[],
    'lab_correlation':{},'contradictions':[],'hallucination_flags':[],'bias_flags':[],
    'safety_downgrades':0,'merged_flags':[],'esi_level':5,'esi_description':'','esi_rules_triggered':[],
    'differential':[],'suggested_actions':[],'report':{},'audit_log':[],'total_time_ms':0.0,
}
async def test():
    final = await run_pipeline(state)
    print(json.dumps({'esi':final.get('esi_level'),'findings':len(final.get('findings',[])),'audit':len(final.get('audit_log',[]))}))
asyncio.run(test())
PYEOF
python3 /tmp/e2e.py
" && ok "E2E passed"

step "RECOVERY COMPLETE"
IP=$(hostname -I | awk '{print $1}')
echo "  Vision: http://${IP}:${VISION_PORT}/v1"
echo "  Text:   http://${IP}:${TEXT_PORT}/v1"
echo "  rocm-smi: rocm-smi --showmeminfo vram --showuse"
