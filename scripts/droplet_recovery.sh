#!/usr/bin/env bash
# =============================================================================
# ClinSight Droplet Self-Recovery Script
# =============================================================================
# Place this on the droplet (e.g., /root/clinsight_recovery.sh).
# Run after booting from snapshot -- it verifies + heals everything in-place.
#
# Usage:
#   bash /root/clinsight_recovery.sh
#
# =============================================================================
set -euo pipefail

# ── Config ──
CONTAINER="clinsight"
SCRATCH_DISK="/dev/vdc1"
SCRATCH_MOUNT="/mnt/scratch"
HF_CACHE="${SCRATCH_MOUNT}/hf_cache"
REPO_LOCAL="/shared-docker/clinsight"
REPO_CONTAINER="/opt/clinsight"
VISION_MODEL="Qwen/Qwen2.5-VL-7B-Instruct"
TEXT_MODEL="Qwen/Qwen3.5-35B-A3B"
VISION_PORT=8000
TEXT_PORT=8001
WAIT_SECS=120

# ── Colors ──
RED='\033[91m'
GRN='\033[92m'
YLW='\033[93m'
BLU='\033[94m'
RST='\033[0m'

info()  { echo -e "${BLU}[INFO]${RST}  $*"; }
ok()    { echo -e "${GRN}[OK]${RST}    $*"; }
warn()  { echo -e "${YLW}[WARN]${RST}  $*"; }
fail()  { echo -e "${RED}[FAIL]${RST}  $*"; exit 1; }

step() {
    echo ""
    echo "============================================================"
    echo -e "${BLU}>>> $*${RST}"
    echo "============================================================"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 1: Pre-flight
# ═══════════════════════════════════════════════════════════════════════════════
step "1. PRE-FLIGHT"
[ -f "${SSH_KEY:-/root/.ssh/id_ed25519}" ] || warn "No SSH key found -- external access may fail"
docker info >/dev/null 2>&1 || fail "Docker not running"
ok "Docker OK"

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 2: Infrastructure
# ═══════════════════════════════════════════════════════════════════════════════
step "2. INFRASTRUCTURE"

# Mount scratch disk
if mountpoint -q "${SCRATCH_MOUNT}"; then
    ok "Scratch disk already mounted"
else
    info "Mounting scratch disk..."
    mkdir -p "${SCRATCH_MOUNT}"
    mount "${SCRATCH_DISK}" "${SCRATCH_MOUNT}" || fail "Scratch mount failed"
    ok "Scratch mounted at ${SCRATCH_MOUNT}"
fi

# Ensure container has volumes mounted
if ! docker inspect "${CONTAINER}" >/dev/null 2>&1; then
    fail "Container '${CONTAINER}' not found -- recreate from image 'rocm:latest'"
fi

# Start container if down
if [ "$(docker inspect "${CONTAINER}" --format='{{.State.Status}}')" != "running" ]; then
    info "Starting container..."
    docker start "${CONTAINER}" || fail "Container start failed"
    sleep 2
fi
ok "Container '${CONTAINER}' running"

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 3: Code Sync (from /shared-docker -> container)
# ═══════════════════════════════════════════════════════════════════════════════
step "3. CODE SYNC"

if [ ! -d "${REPO_LOCAL}" ]; then
    warn "No local repo at ${REPO_LOCAL} -- code sync skipped (assumes container already has code)"
else
    info "Syncing ${REPO_LOCAL} -> container ${REPO_CONTAINER}..."
    docker exec "${CONTAINER}" rm -rf "${REPO_CONTAINER}"
    docker cp "${REPO_LOCAL}/." "${CONTAINER}:${REPO_CONTAINER}/" || warn "docker cp had issues"
    ok "Code synced"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 4: Dependencies
# ═══════════════════════════════════════════════════════════════════════════════
step "4. DEPENDENCIES"

info "Checking Python packages..."
MISSING=""
for pkg in fastapi uvicorn pydantic httpx openai Pillow numpy; do
    docker exec "${CONTAINER}" bash -c "python3 -c 'import ${pkg}'" 2>/dev/null || MISSING="${MISSING} ${pkg}"
done

if [ -n "${MISSING}" ]; then
    info "Installing missing: ${MISSING}"
    docker exec "${CONTAINER}" pip install -q ${MISSING} || warn "Some packages failed"
    ok "Packages installed"
else
    ok "All deps present"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 5: Model Verification
# ═══════════════════════════════════════════════════════════════════════════════
step "5. MODEL VERIFICATION"

check_model() {
    local model_id="$1"
    local name="$2"
    local dir="${HF_CACHE}/models--$(echo ${model_id} | tr '/' '--')"
    if docker exec "${CONTAINER}" test -f "${dir}/config.json" 2>/dev/null; then
        ok "[${name}] Cached at ${dir}"
        return 0
    else
        warn "[${name}] NOT cached"
        return 1
    fi
}

check_model "${VISION_MODEL}" "vision" || {
    info "Downloading ${VISION_MODEL}... (this may take 5-10 min)"
    docker exec "${CONTAINER}" bash -c "
        export HF_HOME=${HF_CACHE};
        huggingface-cli download ${VISION_MODEL} --local-dir ${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct --local-dir-use-symlinks False
    " || fail "Vision model download failed"
    ok "Vision model downloaded"
}

check_model "${TEXT_MODEL}" "text" || {
    info "Downloading ${TEXT_MODEL}... (this may take 30-60 min)"
    docker exec "${CONTAINER}" bash -c "
        export HF_HOME=${HF_CACHE};
        huggingface-cli download ${TEXT_MODEL} --local-dir ${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B --local-dir-use-symlinks False
    " || fail "Text model download failed"
    ok "Text model downloaded"
}

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 6: vLLM Launch
# ═══════════════════════════════════════════════════════════════════════════════
step "6. VLLM LAUNCH"

launch_server() {
    local model_dir="$1"
    local served_name="$2"
    local port="$3"
    local mem="$4"
    local maxlen="$5"
    local log="${HF_CACHE}/../vllm_$(basename ${model_dir}).log"

    # Check if already alive
    if docker exec "${CONTAINER}" bash -c "curl -s http://127.0.0.1:${port}/v1/models 2>/dev/null | grep -q id"; then
        ok "Port ${port} already active"
        return 0
    fi

    info "Starting vLLM on port ${port}..."
    docker exec -d "${CONTAINER}" bash -c "
        export HF_HOME=${HF_CACHE};
        export HUGGINGFACE_HUB_CACHE=${HF_CACHE};
        export VLLM_USE_V1=0;
        export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True;
        nohup python3 -m vllm.entrypoints.openai.api_server \
            --model ${model_dir} \
            --served-model-name ${served_name} \
            --dtype float16 \
            --tensor-parallel-size 1 \
            --port ${port} \
            --host 127.0.0.1 \
            --gpu-memory-utilization ${mem} \
            --max-model-len ${maxlen} \
            --max-num-seqs 2 \
            --trust-remote-code \> ${log} 2\u003e\u00261 \u0026
    "
    return 0
}

# Kill any stale vLLM processes
info "Stopping stale vLLM processes..."
docker exec "${CONTAINER}" pkill -f "vllm.entrypoints" 2>/dev/null || true
sleep 2

launch_server "${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct" "qwen2.5-vl-7b" ${VISION_PORT} 0.30 8192
launch_server "${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"         "qwen3.5-35b-a3b" ${TEXT_PORT}   0.55 4096

info "Waiting up to ${WAIT_SECS}s for servers..."
for i in $(seq 1 $((${WAIT_SECS}/5))); do
    sleep 5
    VISION_OK=false
    TEXT_OK=false

    docker exec "${CONTAINER}" bash -c "curl -s http://127.0.0.1:${VISION_PORT}/v1/models 2>/dev/null | grep -q id" && VISION_OK=true
    docker exec "${CONTAINER}" bash -c "curl -s http://127.0.0.1:${TEXT_PORT}/v1/models   2>/dev/null | grep -q id" && TEXT_OK=true

    ${VISION_OK} && ${TEXT_OK} && { ok "Both vLLM servers ready"; break; }
done

${VISION_OK} || fail "Vision server on port ${VISION_PORT} did not start"
${TEXT_OK}   || fail "Text server on port ${TEXT_PORT} did not start"

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 7: Health Checks
# ═══════════════════════════════════════════════════════════════════════════════
step "7. HEALTH CHECKS"

docker exec "${CONTAINER}" bash -c "curl -s http://127.0.0.1:${VISION_PORT}/v1/models | python3 -c 'import sys,json; d=json.load(sys.stdin); print(\"vision\", d[\"data\"][0][\"id\"])'" && ok "Vision API OK"
docker exec "${CONTAINER}" bash -c "curl -s http://127.0.0.1:${TEXT_PORT}/v1/models   | python3 -c 'import sys,json; d=json.load(sys.stdin); print(\"text  \", d[\"data\"][0][\"id\"])'" && ok "Text API OK"

docker exec "${CONTAINER}" rocm-smi | grep -E "^0" | while read line; do ok "GPU: ${line}"; done

# ═══════════════════════════════════════════════════════════════════════════════
# Phase 8: E2E Quick Test
# ═══════════════════════════════════════════════════════════════════════════════
step "8. E2E QUICK TEST"

info "Running 1 E2E pipeline test..."
docker exec "${CONTAINER}" bash -c "
cd ${REPO_CONTAINER}
cat > /tmp/e2e.py << 'PYEOF'
import sys, asyncio, json
sys.path.insert(0, '${REPO_CONTAINER}')
from backend.agents.graph import run_pipeline

state = {
    'case_id': 'CS-2024-001', 'image_path': 'data/images/demo_chest_pain.png',
    'lab_values': {'troponin_i':0.12,'bnp':180,'crp':12,'wbc':9.2,'hemoglobin':14.1,'platelets':245,'creatinine':0.9,'glucose':105},
    'lab_units': {'troponin_i':'ng/L','bnp':'pg/mL','crp':'mg/L','wbc':'K/uL','hemoglobin':'g/dL','platelets':'K/uL','creatinine':'mg/dL','glucose':'mg/dL'},
    'triage_note':'45yo male with chest pain, vitals stable',
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
    print(json.dumps({'esi':final.get('esi_level'),'findings':len(final.get('findings',[])),'diff':final.get('differential',[])[:3], 'audit':len(final.get('audit_log',[]))}))
asyncio.run(test())
PYEOF
python3 /tmp/e2e.py
" && ok "E2E test passed"

# ═══════════════════════════════════════════════════════════════════════════════
# Report
# ═══════════════════════════════════════════════════════════════════════════════
step "RECOVERY COMPLETE"

IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${GRN}ClinSight droplet is ready!${RST}"
echo ""
echo "  Vision API: http://${IP}:${VISION_PORT}/v1 (qwen2.5-vl-7b)"
echo "  Text API:   http://${IP}:${TEXT_PORT}/v1   (qwen3.5-35b-a3b)"
echo ""
echo "  Container:  docker exec -it ${CONTAINER} bash"
echo "  Logs:       docker exec ${CONTAINER} tail -f ${HF_CACHE}/../vllm_*.log"
echo ""
echo "  From local WSL, run benchmarks:"
echo "    cd /mnt/k/Hackthon/ClinSight"
echo "    python3 scripts/run_benchmark.py --host ${IP}"
echo ""
