#!/bin/bash
set -e
CONTAINER="rocm"
HF_CACHE="/mnt/scratch/hf_cache"
REPO="/shared-docker/clinsight"
VISION_PORT=8000
TEXT_PORT=8001
VISION_MODEL="Qwen/Qwen2.5-VL-7B-Instruct"
TEXT_MODEL="Qwen/Qwen3.5-35B-A3B"

echo "=== Phase 1: Mount scratch ==="
mkdir -p /mnt/scratch
df -h /mnt/scratch | grep -q /mnt/scratch || mount /dev/vdc1 /mnt/scratch || true

echo "=== Phase 2: Ensure container running ==="
if [ "$(docker inspect "${CONTAINER}" --format='{{.State.Status}}' 2>/dev/null)" != "running" ]; then
    docker start "${CONTAINER}" || docker run -d --name "${CONTAINER}" --device /dev/kfd --device /dev/dri -v /mnt/scratch:/mnt/scratch -v /shared-docker:/shared-docker -p 8000:8000 -p 8001:8001 rocm tail -f /dev/null
fi

echo "=== Phase 3: Sync code ==="
docker cp "${REPO}/." "${CONTAINER}:/opt/clinsight/"

echo "=== Phase 4: Install deps in container ==="
docker exec "${CONTAINER}" bash -c "pip install -q fastapi uvicorn pydantic httpx openai Pillow numpy langgraph langchain 2>/dev/null || true"

echo "=== Phase 5: Download models ==="
docker exec "${CONTAINER}" bash -c "export HF_HOME=${HF_CACHE}; export HUGGINGFACE_HUB_CACHE=${HF_CACHE}; python3 -c 'from huggingface_hub import snapshot_download; snapshot_download(repo_id=\"${VISION_MODEL}\", local_dir=\"${HF_CACHE}/vision\", local_dir_use_symlinks=False)'" || true
docker exec "${CONTAINER}" bash -c "export HF_HOME=${HF_CACHE}; export HUGGINGFACE_HUB_CACHE=${HF_CACHE}; python3 -c 'from huggingface_hub import snapshot_download; snapshot_download(repo_id=\"${TEXT_MODEL}\", local_dir=\"${HF_CACHE}/text\", local_dir_use_symlinks=False)'" || true

echo "=== Phase 6: Kill stale vLLM ==="
docker exec "${CONTAINER}" bash -c "pkill -f vllm.entrypoints || true"
sleep 3

echo "=== Phase 7: Start vLLM Vision ==="
docker exec -d "${CONTAINER}" bash -c "export HF_HOME=${HF_CACHE}; export VLLM_USE_V1=0; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True; nohup python3 -m vllm.entrypoints.openai.api_server --model ${HF_CACHE}/vision --served-model-name qwen2.5-vl-7b --dtype float16 --tensor-parallel-size 1 --port ${VISION_PORT} --host 0.0.0.0 --gpu-memory-utilization 0.30 --max-model-len 8192 --max-num-seqs 2 --trust-remote-code > /tmp/vllm_vision.log 2>&1 &"

echo "=== Phase 8: Start vLLM Text ==="
docker exec -d "${CONTAINER}" bash -c "export HF_HOME=${HF_CACHE}; export VLLM_USE_V1=0; export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True; nohup python3 -m vllm.entrypoints.openai.api_server --model ${HF_CACHE}/text --served-model-name qwen3.5-35b-a3b --dtype float16 --tensor-parallel-size 1 --port ${TEXT_PORT} --host 0.0.0.0 --gpu-memory-utilization 0.55 --max-model-len 4096 --max-num-seqs 2 --trust-remote-code > /tmp/vllm_text.log 2>&1 &"

echo "=== Phase 9: Wait for servers ==="
for i in {1..60}; do
    sleep 5
    V=$(curl -s http://127.0.0.1:8000/v1/models | grep -c id || true)
    T=$(curl -s http://127.0.0.1:8001/v1/models | grep -c id || true)
    if [ "$V" -ge 1 ] && [ "$T" -ge 1 ]; then
        echo "Both servers ready!"
        break
    fi
    echo "Wait $i/60: vision=$V text=$T"
done

echo "=== Phase 10: Health check ==="
curl -s http://127.0.0.1:8000/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('VISION:', d['data'][0]['id'])" || true
curl -s http://127.0.0.1:8001/v1/models | python3 -c "import sys,json; d=json.load(sys.stdin); print('TEXT:', d['data'][0]['id'])" || true

echo "=== GPU State ==="
rocm-smi --showproductname --showmeminfo vram --showuse 2>/dev/null | head -8 || true

echo "=== DONE ==="
