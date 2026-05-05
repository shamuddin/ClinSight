# Architecture

## Multi-Agent Pipeline

```
Input → Coordinator → [Radiologist, Lab Analyst, Safety (parallel)] → Clinical Documenter → Output
```

## State Flow

AgentState carries data through the graph. Each agent reads previous outputs and writes its own.

## Model Stack

- Vision: Qwen2.5-VL-7B-Instruct (port 8000)
- Text: Qwen3.5-35B-A3B (port 8001)

## Deployment

AMD MI300X via RunPod / TensorDock. ROCm 6.x, vLLM.
