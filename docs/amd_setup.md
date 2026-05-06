# AMD GPU Setup Guide

## Overview

This project uses **two** vLLM servers on AMD GPU:

| Server | Model | Port | VRAM |
|---|---|---|---|
| Vision | Qwen2.5-VL-7B-Instruct | 8000 | ~14 GB |
| Text | Qwen3.5-35B-A3B | 8001 | ~70 GB |
| **Total** | | | **~84 GB** |

Recommended GPU: AMD MI300X (192 GB VRAM) leaves 108 GB headroom for KV cache + concurrent requests.

---

## Quick Start (Fresh Droplet)

```bash
# 1. Clone repo
git clone https://github.com/shamuddin/ClinSight.git
cd ClinSight

# 2. Run setup (installs ROCm deps, PyTorch, vLLM)
chmod +x scripts/setup_amd_gpu.sh
./scripts/setup_amd_gpu.sh

# 3. Start vLLM servers (in separate terminals or tmux)
source ~/clinsight-venv/bin/activate
./scripts/start_vllm_vision.sh &
./scripts/start_vllm_text.sh &

# 4. Verify
python scripts/gpu_health_check.py

# 5. Run benchmark (mock mode first, then real)
python scripts/run_benchmark.py --mode mock --cases 6 --iterations 10
python scripts/run_benchmark.py --mode real --cases 6 --iterations 5
```

---

## Manual Setup (If Script Fails)

### 1. Install ROCm

Follow AMD's official guide for your OS:
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/

Verify:
```bash
rocminfo | grep -E "Name:|Marketing name"
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv ~/clinsight-venv
source ~/clinsight-venv/bin/activate
pip install --upgrade pip wheel setuptools
```

### 3. Install PyTorch (ROCm)

```bash
pip install torch==2.4.0+rocm6.1 torchvision \
    --index-url https://download.pytorch.org/whl/rocm6.1
```

### 4. Build vLLM for ROCm

```bash
export VLLM_TARGET_DEVICE="cuda"
pip install vllm==0.6.3 \
    --extra-index-url https://download.pytorch.org/whl/rocm6.1 \
    --no-build-isolation
```

### 5. Install ClinSight Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VISION_MODEL` | `Qwen/Qwen2.5-VL-7B-Instruct` | HuggingFace model ID for vision |
| `VISION_PORT` | `8000` | vLLM API port for vision |
| `VISION_MAX_LEN` | `4096` | Max context length for vision model |
| `VISION_QUANT` | `none` | Quantization: none, awq, gptq |
| `TEXT_MODEL` | `Qwen/Qwen3.5-35B-A3B` | HuggingFace model ID for text |
| `TEXT_PORT` | `8001` | vLLM API port for text |
| `TEXT_MAX_LEN` | `8192` | Max context length for text model |
| `TEXT_TP_SIZE` | `1` | Tensor parallelism (set to 2 for 2x GPUs) |
| `TEXT_QUANT` | `none` | Quantization: none, awq, gptq, fp8 |
| `GPU_MEMORY_UTIL` | `0.90` | GPU memory utilization cap |

---

## Starting vLLM Servers

### Vision Server

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-VL-7B-Instruct \
    --port 8000 \
    --dtype bfloat16 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 4096 \
    --max-num-seqs 4 \
    --enable-chunked-prefill \
    --trust-remote-code
```

### Text Server

```bash
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3.5-35B-A3B \
    --port 8001 \
    --dtype bfloat16 \
    --tensor-parallel-size 1 \
    --gpu-memory-utilization 0.90 \
    --max-model-len 8192 \
    --max-num-seqs 4 \
    --enable-chunked-prefill \
    --trust-remote-code
```

---

## Health Check

```bash
python scripts/gpu_health_check.py [VISION_URL] [TEXT_URL]
```

Checks:
1. ROCm GPU visibility
2. vLLM /health endpoint on both servers
3. Warm-up inference call
4. Per-GPU memory snapshot

Report saved to `backend/data/gpu_health.json`.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `rocminfo` not found | ROCm not installed | Follow AMD install guide |
| `torch.cuda unavailable` | Wrong PyTorch build | Reinstall with `+rocm` wheel |
| vLLM build fails | Missing CMake/system deps | `sudo apt install build-essential cmake` |
| OOM on GPU | Model too large for VRAM | Use quantization (`--quantization awq`) or reduce `max-model-len` |
| Server timeout on first request | Cold KV cache | Run `gpu_health_check.py` warm-up |

---

## Performance Expectations (MI300X)

| Metric | Vision (7B) | Text (35B MoE) |
|---|---|---|
| First-token latency | ~0.5-1.0s | ~1.0-2.0s |
| Tokens/sec | ~40-60 | ~20-30 |
| Concurrent requests | 4 | 4 |
| Full pipeline (6 cases) | ~15s | ~30s |

---

## Multi-GPU Setup

If you have 2x MI210 or 2x MI250:

```bash
# Text model across 2 GPUs
TEXT_TP_SIZE=2 ./scripts/start_vllm_text.sh

# Or set explicitly
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3.5-35B-A3B \
    --port 8001 \
    --tensor-parallel-size 2
```

Vision model can stay on 1 GPU (7B fits easily).
