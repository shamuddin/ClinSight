# ClinSight — Resume Prompt for New Session

## Context
This is a handoff document. The previous session ended after 31 context compressions. A fresh session must resume work exactly where we left off.

## Current State (May 7 2026)
- GPU droplet is DOWN — previous IP 134.199.193.58 is orphaned.
- User will create a fresh DigitalOcean GPU droplet and provide a new IP.
- All deliverables are in progress; the blockers are:
  1. No live GPU droplet to run E2E benchmarks
  2. No real GPU metrics (rocm-smi, inference timing) to fill pitch deck placeholders
  3. HF Space app.py has demo cases but needs a "Performance" tab with live GPU data

## Active Tasks (in progress unless marked pending)
1. [IN PROGRESS] HF Space app.py — 3 pre-loaded demo cases + Performance tab
   - File: /workspace/hf_space/app.py
   - Missing: GPU utilization chart, inference latency display, model memory footprint
2. [IN PROGRESS] Pitch deck HTML — 10 slides with GPU data placeholders
   - File: /workspace/docs/pitch_deck.html
   - Placeholders: `{{gpu_utilization}}`, `{{inference_time}}`, `{{model_memory}}`, `{{throughput}}`, `{{rocm_smi}}`
3. [IN PROGRESS] docker-compose.yml + Dockerfile for full-stack deployment
   - File: /workspace/docker-compose.yml
   - Missing: Production-ready nginx reverse-proxy, health checks, restart policies
4. [IN PROGRESS] scripts/test_model_load.py — GPU validation script
   - File: /workspace/scripts/test_model_load.py
   - Must verify both vision (port 8000) and text (port 8001) vLLM models respond
5. [IN PROGRESS] scripts/run_full_benchmark.py — automated benchmark + rocm-smi capture
   - File: /workspace/scripts/run_benchmark.py (exists, may need rename)
   - Must capture: per-case inference time, GPU memory usage, accuracy vs ground truth
6. [IN PROGRESS] GPU droplet: boot, sync code, start vLLM, run E2E + benchmarks + generate cache
   - SSH key: /workspace/.ssh/id_ed25519
   - Required host mounts: /shared-docker/hf_cache (model cache), /shared-docker/clinsight (code)
   - Sequential start: vision first (--gpu-memory-utilization 0.20), wait /v1/models, then text (--gpu-memory-utilization 0.50 --enforce-eager)
7. [PENDING] Copy GPU results back, fill pitch deck placeholders, finalize HF Space
8. [IN PROGRESS] Git commit all deliverables
   - Latest commit: 43ffb89
   - Branch: main

## Technical Specs for New Droplet
- Container: `rocm` (privileged, host network, GPU access)
  - Mounts: /shared-docker/hf_cache:/root/.cache/huggingface:rw
  - Mounts: /shared-docker/clinsight:/opt/clinsight:rw
- Container: `clinsight` (backend FastAPI, port 3000, host network)
- Vision model: Qwen/Qwen2.5-VL-7B-Instruct (port 8000, ~30 GB VRAM)
- Text model: Qwen/Qwen3.5-35B-A3B (port 8001, ~88 GB VRAM, MUST use --gpu-memory-utilization 0.50 --enforce-eager --max-num-seqs 1)
- Total GPU RAM: ~206 GB (AMD MI300X)

## First Actions for New Session
1. Read this file (/workspace/RESUME_PROMPT.md)
2. Ask user for the new droplet IP
3. SSH in with: ssh -i /workspace/.ssh/id_ed25519 root@<NEW_IP>
4. Check if containers exist; if not, run bootstrap from /workspace/scripts/bootstrap_clinsight.sh
5. Install system deps inside rocm container: apt-get install -y libgl1 libglib2.0-0
6. Install pip deps inside clinsight container: pip install pydantic-settings opencv-python-headless langgraph langchain langchain-core openai
7. Start vision vLLM with low utilization, wait for /v1/models
8. Start text vLLM with strict limits
9. Run E2E test for 3 demo cases
10. Run benchmark script, capture rocm-smi output
11. Copy /shared-docker/vllm_logs/ and benchmark JSON back to /workspace/benchmarks/gpu_results/
12. Fill pitch deck placeholders with real numbers
13. Update HF Space Performance tab with real data
14. Git commit everything

## Key Contacts / References
- User prefers execution over planning — just do it, ask later if blocked.
- User requires exact file paths, command outputs, and error messages in responses.
- Do NOT pre-compute LLM caches; insist on real-time inference (~65s per case).
- Judge-facing accuracy must be HONEST (radiologist score ~50%, not fake 100%).
- Secrets: use [REDACTED], do not expose HF tokens or API keys.
