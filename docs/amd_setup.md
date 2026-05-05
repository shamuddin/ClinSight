# AMD GPU Setup

## Environment
- ROCm 6.x
- PyTorch with ROCm support
- vLLM compiled for ROCm

## Model Loading
```bash
vllm serve Qwen/Qwen2.5-VL-7B-Instruct --port 8000 --tensor-parallel-size 1
vllm serve Qwen/Qwen3.5-35B-A3B --port 8001 --tensor-parallel-size 1
```

## Memory
Total model VRAM: ~99GB
MI300X available: 192GB
Headroom: 93GB for concurrent requests + KV cache.
