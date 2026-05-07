#!/bin/bash
set -euo pipefail
LOG="/root/run_all.log"
exec > "$LOG" 2>&1

CONTAINER="rocm"
HF_CACHE="/mnt/scratch/hf_cache"
REPO_CONTAINER="/opt/clinsight"
VISION_PORT=8000
TEXT_PORT=8001
VISION_DIR="${HF_CACHE}/models--Qwen--Qwen2.5-VL-7B-Instruct"
TEXT_DIR="${HF_CACHE}/models--Qwen--Qwen3.5-35B-A3B"

echo "=== $(date) ==="
echo "Step 1: Ensure scratch mounted"
mkdir -p /mnt/scratch
df -h /mnt/scratch | grep -q /mnt/scratch || mount /dev/vdc1 /mnt/scratch || true

echo "Step 2: Sync code into container"
docker exec "${CONTAINER}" rm -rf "${REPO_CONTAINER}" || true
docker exec "${CONTAINER}" mkdir -p "${REPO_CONTAINER}"
docker cp "/shared-docker/clinsight/." "${CONTAINER}:${REPO_CONTAINER}/" || true

echo "Step 3: Install deps"
docker exec "${CONTAINER}" bash -c "pip install -q fastapi uvicorn pydantic httpx openai Pillow numpy langgraph langchain 2>/dev/null || true"

echo "Step 4: Kill stale vLLM"
docker exec "${CONTAINER}" bash -c "pkill -f vllm.entrypoints || true"
sleep 3

echo "Step 5: Launch Vision vLLM"
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
"
echo "Vision launched"

echo "Step 6: Launch Text vLLM"
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
"
echo "Text launched"

echo "Step 7: Wait for warmup (180s)..."
sleep 180

echo "Step 8: Check servers"
for port in ${VISION_PORT} ${TEXT_PORT}; do
    for i in {1..30}; do
        if curl -s http://127.0.0.1:${port}/v1/models | grep -q id; then
            echo "Port ${port} ready"
            break 2
        fi
        sleep 2
    done
    echo "Port ${port} NOT ready after 60s"
done

echo "Step 9: Model list"
curl -s http://127.0.0.1:${VISION_PORT}/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('VISION:', d['data'][0]['id'])" || true
curl -s http://127.0.0.1:${TEXT_PORT}/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('TEXT:', d['data'][0]['id'])" || true

echo "Step 10: rocm-smi"
rocm-smi --showmeminfo vram --showuse 2>/dev/null | head -10 || true

echo "Step 11: E2E test"
docker exec "${CONTAINER}" bash -c "
cd ${REPO_CONTAINER}
cat > /tmp/e2e.py << 'PYEOF'
import sys, asyncio, json
sys.path.insert(0, '${REPO_CONTAINER}')
from backend.agents.graph import run_pipeline
state = {
    'case_id': 'CS-2024-001',
    'image_path': 'frontend/react-app/public/demo-images/CS-2024-001.png',
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
    print(json.dumps({'esi':final.get('esi_level'),'findings':len(final.get('findings',[])),'audit':len(final.get('audit_log',[]))}))
asyncio.run(test())
PYEOF
python3 /tmp/e2e.py
" || echo "E2E FAILED"

echo "=== DONE $(date) ==="
